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

weather_api_url = 'https://api.openweathermap.org/data/2.5/weather?id=2110498&APPID={APPID}&units=imperial'.format(APPID=os.getenv('APPID', None))

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

def get_japan_time():
    jp = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo'))
    jesse_date = jp.strftime('It is currently %b %d %Y at %H:%M:%S %p for Jesse.')
    return jesse_date

def get_japan_weather_info():
    response = requests.get(weather_api_url)
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))

        curr_temp = data['main']['temp']
        humidity = data['main']['humidity']

        return 'Jesse is experiencing {curr_temp} F weather and a humidity of {humidity}%.'.format(curr_temp=curr_temp, humidity=humidity)
    else:
        return 'Weather API might be fucked up right now.'



@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

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

        if '!time' in event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=get_japan_time())
            )
        elif '!weather' in event.message.text:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=get_japan_weather_info())
            )

    return 'OK'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)