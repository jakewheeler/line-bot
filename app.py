from __future__ import unicode_literals

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import pytz
import datetime
import requests
import json
import math
import random

#### bot code ####
import bot


app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        if ('!help') in event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(bot.get_help())
            )
        else:
            for k in bot.cmd.keys():
                if k in event.message.text:
                    args = event.message.text[len(k)+1:]
                    if args != None and args != '' and bot.cmd[k]['hasParams'] is True:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=bot.cmd[k]['func'](args))
                        )
                    elif bot.cmd[k]['hasParams'] is False:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=bot.cmd[k]['func'])
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text='Could not get command')
                        )  

    return 'OK'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)