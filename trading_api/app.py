from chalice import Chalice
from chalicelib import util, volatility_util
import time
import socket
import ccxt


app = Chalice(app_name='trading_api')

@app.route('/volatility', methods=['POST'])
def trade_volatility():
    request = app.current_request
    data = request.json_body

    try:
        symbol = data['symbol']
        position = data['position']
        target_price = data['target_price']

    except KeyError:
        raise NotFoundError()

    if position == "enter_long":
        volatility_util.enter_position(symbol, "long", target_price)
        return {"message": "success"}

    elif position == "enter_short":
        volatility_util.enter_position(symbol, "short", target_price)
        return {"message": "success"}

    elif position == "exit_long":
        volatility_util.exit_position(symbol, "long", target_price)
        return {"message": "success"}

    elif position == "exit_short":
        volatility_util.exit_position(symbol, "short", target_price)
        return {"message": "success"}

    return {"message": "fail"}
