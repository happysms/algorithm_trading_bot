import ccxt
import math
import pymysql
from datetime import datetime
import time
import json
import logging
import boto3
import os


def make_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.propagate = False

    return logger


logger = make_logger("mylogger")


def get_database_connection():
    with open(os.path.dirname(os.path.realpath(__file__))+'/volatility_config.json', 'r', encoding="UTF-8") as auth_file:
        auth_dict = json.load(auth_file)

    conn = pymysql.connect(host=auth_dict["host"],
                           user=auth_dict["user"],
                           password=auth_dict["password"],
                           db=auth_dict["db"],
                           charset="utf8")

    return conn


def get_bybit_object():
    bybit = ccxt.bybit(config={
        'apiKey': os.getenv('api_key'),
        'secret': os.getenv('secret'),
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'
        }})

    return bybit


def get_trade_list():
    with open(os.path.dirname(os.path.realpath(__file__))+'/volatility_config.json', 'r', encoding="UTF-8") as auth_file:
        auth_dict = json.load(auth_file)

    s3_client = boto3.client('s3',
                             aws_access_key_id=auth_dict['AWS_ACCESS_KEY_ID'],
                             aws_secret_access_key=auth_dict['AWS_SECRET_ACCESS_KEY'],
                             region_name=auth_dict['AWS_DEFAULT_REGION'])

    s3_obj = s3_client.get_object(Bucket='', Key='')  # TODO 입력
    s3_data = s3_obj['Body'].read().decode('utf-8')
    trade_list = json.loads(s3_data)

    return trade_list


def write_trade_list(symbol, position, amount, usdt=None):
    with open(os.path.dirname(os.path.realpath(__file__))+'/volatility_config.json', 'r', encoding="UTF-8") as auth_file:
        auth_dict = json.load(auth_file)

    s3_client = boto3.client('s3',
                             aws_access_key_id=auth_dict['AWS_ACCESS_KEY_ID'],
                             aws_secret_access_key=auth_dict['AWS_SECRET_ACCESS_KEY'],
                             region_name=auth_dict['AWS_DEFAULT_REGION'])

    s3_obj = s3_client.get_object(Bucket='', Key='')
    s3_data = s3_obj['Body'].read().decode('utf-8')
    before_trade_list = json.loads(s3_data)

    for trade in before_trade_list:  # get amount & set position
        if trade.get("symbol") == symbol:
            trade['position'] = position
            trade['amount'] = amount

            if not trade['is_possible']:
                trade['is_possible'] = True

            if usdt:
                trade['usdt'] = usdt

            break

    s3_client.put_object(
        Body=json.dumps(before_trade_list),
        Bucket='',
        Key=''  # TODO 입력
    )


def enter_position(symbol, position, target_price):
    bybit = get_bybit_object()
    amount = cal_enter_possible_amount(bybit, symbol)

    if position == "long":
        order = bybit.create_order(symbol, "market", "buy", amount)
        order_id = order['info']['order_id']
        time.sleep(10)
        logger.info(position + " position " + str(symbol) + " " + str(amount) + "개")

    else:
        order = bybit.create_order(symbol, "market", "sell", amount)
        order_id = order['info']['order_id']
        time.sleep(10)
        logger.info(position + " position " + str(symbol) + " " + str(amount) + "개")

    write_trade_list(symbol, position, amount)
    add_record_log(order_id, bybit, symbol, target_price)


def exit_position(symbol, position, target_price):
    bybit = get_bybit_object()
    amount = cal_exit_possible_amount(bybit, symbol)

    if position == "long":
        order = bybit.create_order(symbol, "market", "sell", amount, params={'reduce_only': True})
        order_id = order['info']['order_id']
        time.sleep(10)
        logger.info(position + " position " + str(symbol) + " " + str(amount) + "개")

    else:
        order = bybit.create_order(symbol, "market", "buy", amount, params={'reduce_only': True})
        order_id = order['info']['order_id']
        time.sleep(10)
        logger.info(position + " position " + str(symbol) + " " + str(amount) + "개")

    usdt_balance = bybit.fetch_balance()['USDT']['total'] / 5   # TODO /5 부분은 종목 개수 만큼
    write_trade_list(symbol, None, 0, usdt_balance)
    add_record_log(order_id, bybit, symbol, target_price)


def cal_enter_possible_amount(bybit, symbol):
    usdt_balance = bybit.fetch_balance()['USDT']['total'] / 5  # TODO /5 부분은 종목 개수 만큼
    ticker = bybit.fetch_ticker(symbol=symbol)
    cur_price = ticker['last']
    amount = math.floor((usdt_balance * 1000000) / cur_price) / 1000000
    return amount


def cal_exit_possible_amount(bybit, symbol):
    bybit = bybit.fetch_balance()
    trade_list = get_trade_list()
    amount = 0 
    
    for trade in trade_list:
        if trade['symbol'] == symbol:
            amount = trade['amount']

    return amount


def add_record_log(order_id, bybit, symbol, target):
    conn = get_database_connection()
    record = bybit.fetch_order(order_id, symbol)['info']

    table_name = symbol.replace("/USDT", "").lower()
    date = record['created_time'].replace('T', " ").replace('Z', "")
    fee = float(record['cum_exec_fee'])
    side = record['side']
    symbol = record['symbol']
    price = float(record['price'])
    qty = float(record['qty'])
    value = float(record['cum_exec_value'])

    if side.lower() == "buy":
        trade_diff_rate = round((((price / target) - 1) * 100), 4)
    else:
        trade_diff_rate = round((((target / price) - 1) * 100), 4)

    with conn.cursor() as curs:
        sql = """
                INSERT INTO {} (datetime, qty, fee, side, symbol, price ,value, trade_diff_rate, target)
                            VALUES ('{}', {}, {}, '{}', '{}', {}, {}, {}, {})
                            """.format(table_name, date, qty, fee, side, symbol, price, value, trade_diff_rate,
                                       target)

        curs.execute(sql)
        conn.commit()
