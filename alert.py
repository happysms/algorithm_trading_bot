import requests
import json


def post_message(text):
    myToken = "자신의 slack bot 토큰"  #TODO 작성
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + myToken},
                             data={"channel": "#alert", "text": json.dumps(text)})


# def message_usage(bool):
#     def decorator(func):
#         def wrapper(symbol, position, target_price):
#             if bool:
#                 post_message({"symbol": symbol,
#                               "position": position,
#                               "target_price": target_price})
#                 func(symbol, position, target_price)
#             else:
#                 func(symbol, position, target_price)
#
#         return wrapper
#     return decorator

