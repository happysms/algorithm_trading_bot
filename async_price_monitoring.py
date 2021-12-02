import ccxt
import time
import logger
import datetime
from alert import post_message
import asyncio
import aiohttp
from monitoring_util import (get_trade_list,
                             check_trading_start,
                             check_trade_point,
                             exit_position,
                             enter_position)


class OrderType:
    def __init__(self, type, bybit, order_dict):
        self.type = type
        self.bybit = bybit
        self.order_dict = order_dict

    def __str__(self):
        return f"{self.type} {self.bybit} {self.order_dict}"


async def main_loop():
    while True:
        try:
            now = datetime.datetime.now()

            # 포지션 종료
            if now.hour == 8 and now.minute == 59 and (30 <= now.second <= 59):
                for trade in trade_list:
                    if trade['position']:
                        yield OrderType("exit", bybit, trade)
                        trade['position'] = None
                        await asyncio.sleep(1)   # 1초 텀으로 비동기 주문
                    
            else:
                for trade in trade_list:
                    trade_condition = check_trade_point(trade, bybit)

                    # long 진입
                    if trade_condition == "long" and not trade['position']:
                        trade['position'] = "long"
                        yield OrderType("enter", bybit, trade)

                    # short 진입
                    elif trade_condition == "short" and not trade['position']:
                        trade['position'] = "short"
                        yield OrderType("enter", bybit, trade)

            await asyncio.sleep(2)

        except Exception as e:
            logger.info(e)
            post_message({"error": str(e)})
            await asyncio.sleep(1)


async def init():
    async for order in main_loop():
        if order.type == "exit":
            asyncio.ensure_future(exit_position(order.bybit,
                                                order.order_dict))

        elif order.type == "enter":
            asyncio.ensure_future(enter_position(order.bybit,
                                                 order.order_dict))


if "__main__" == __name__:
    bybit = ccxt.bybit(config={'options': {'defaultType': 'future'}})
    logger = logger.make_logger("mylogger")
    trade_list = get_trade_list()
    trade_list = check_trading_start(bybit, trade_list)
    bot_loop = asyncio.get_event_loop()
    bot_loop.run_until_complete(init())

