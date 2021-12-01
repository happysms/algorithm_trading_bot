import requests
import json
import boto3
import pandas as pd
import asyncio
import aiohttp
import logger
import alert

logger = logger.make_logger("mylogger")


def get_price_df(bybit, symbol):
    data = bybit.fetch_ohlcv(
        symbol=symbol,
        timeframe='1d',
        since=None,
        limit=7
    )

    df = pd.DataFrame(
        data=data,
        columns=['datetime', 'open', 'high', 'low', 'close', 'volume']
    )

    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    return df


def check_trade_point(coin, bybit):
    df = get_price_df(bybit, coin['symbol'])
    ma = df['open'].rolling(window=coin['ma_condition']).mean().iloc[-1]
    yesterday = df.iloc[-2]
    today = df.iloc[-1]

    long_target = today['open'] + (yesterday['high'] - yesterday['low']) * coin['long_k']
    short_target = today['open'] - (yesterday['high'] - yesterday['low']) * coin['short_k']

    if coin['is_possible']:
        if today['close'] >= long_target and ma >= today['close']:
            return "long"

        elif today['close'] <= short_target and ma <= today['close'] and coin['is_possible']:
            return "short"

    else:
        if short_target <= today['close'] <= long_target:
            return None
        else:
            return True


def get_trade_list():
    with open('config.json', 'r', encoding="UTF-8") as auth_file:
        auth_dict = json.load(auth_file)

    s3_client = boto3.client('s3',
                             aws_access_key_id=auth_dict['AWS_ACCESS_KEY_ID'],
                             aws_secret_access_key=auth_dict['AWS_SECRET_ACCESS_KEY'],
                             region_name=auth_dict['AWS_DEFAULT_REGION'])

    s3_obj = s3_client.get_object(Bucket='   ', Key='  ')  #TODO 작성
    s3_data = s3_obj['Body'].read().decode('utf-8')
    trade_list = json.loads(s3_data)

    for data in trade_list:
        data['is_possible'] = False

    return trade_list


def check_trading_start(bybit, trade_list):
    for coin in trade_list:
        if not check_trade_point(coin, bybit):
            coin['is_possible'] = True
    return trade_list


async def exit_position(bybit, coin):
    df = get_price_df(bybit, coin['symbol'])
    target = df.iloc[-1]['close']

    if coin['position'] == "long":
        asyncio.ensure_future(request_order(coin['symbol'], "exit_long", target))
    elif coin['position'] == "short":
        asyncio.ensure_future(request_order(coin['symbol'], "exit_short", target))


async def enter_position(bybit, coin):
    df = get_price_df(bybit, coin['symbol'])
    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    long_target = today['open'] + (yesterday['high'] - yesterday['low']) * coin['long_k']
    short_target = today['open'] - (yesterday['high'] - yesterday['low']) * coin['short_k']

    if coin['position'] == "long":
        asyncio.ensure_future(request_order(coin['symbol'], "enter_long", long_target))
    elif coin['position'] == "short":
        asyncio.ensure_future(request_order(coin['symbol'], "enter_short", short_target))


async def request_order(symbol, position, target_price):
    url = "주문 endpoint!!" #TODO 작성
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    alert.post_message({"symbol": symbol,
                        "position": position,
                        "target_price": target_price})

    logger.info({"symbol": symbol,
                 "position": position,
                 "target_price": target_price})

    async with aiohttp.ClientSession() as session:
        async with session.post(url,
                                headers=headers,
                                json={"symbol": symbol,
                                      "position": position,
                                      "target_price": target_price}) as resp:

            logger.info(await resp.text())
