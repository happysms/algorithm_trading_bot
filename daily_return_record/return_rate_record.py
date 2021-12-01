import ccxt
import pymysql
import pandas as pd
from datetime import datetime, timedelta


class ReturnRateRecord:
    def __init__(self):
        self.bybit = ccxt.bybit(config={
                    'apiKey': "",  # TODO 입력
                    'secret': "",   # TODO 입력
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'future'
                    }
                })

        self.conn = pymysql.connect(host="",
                                    user="", password="", db="", charset="utf8")  # TODO 입력

    def insert_record_to_database(self):
        sql = "select * from return_rate_record"   # TODO 본인이 지정한 DB 옵션 적용하기
        df = pd.read_sql(sql, self.conn)

        if len(df) == 0:
            total_balance = self.bybit.fetch_balance()['USDT']['total']
            ror = 1
            hpr = 1
            mdd = 0
            date = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")
        else:
            rr_df = df.iloc[-1]
            total_balance = self.bybit.fetch_balance()['USDT']['total']
            ror = float(total_balance) / rr_df['balance']
            hpr = rr_df['hpr'] * ror
            mdd = ((df['hpr'].cummax() - hpr) / df['hpr'].cummax() * 100).iloc[-1]
            date = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")

        with self.conn.cursor() as curs:
            sql = """
                    INSERT INTO return_rate_record (datetime, ror, hpr, mdd, total_balance) 
                               VALUES ('{}', {}, {}, {}, {})""".format(date, ror, hpr, mdd, total_balance)

            curs.execute(sql)
            self.conn.commit()

        self.conn.close()


