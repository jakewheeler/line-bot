import datetime
import json
import requests
import math
import random
import pytz
import os

import osrs
from randomEmoji import random_emoji

# env variables
DEBUG = os.getenv("DEBUG", False)
ENV = os.getenv("ENV", "dev")

if ENV == "dev":
    from dotenv import load_dotenv

    load_dotenv()

# Access keys
WEATHER_API_KEY = os.getenv("APPID", None)
CURRENCY_CONVERSION_KEY = os.getenv("CURRENCY_CONVERSION_KEY", None)
BEER_API_KEY = os.getenv("BEER_API_KEY", None)
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY", None)
LUNCHMONEY_API_KEY = os.getenv("LUNCHMONEY_API_KEY", None)

# API URLs
weather_api_url = f"https://api.openweathermap.org/data/2.5/weather?id=2110498&APPID={WEATHER_API_KEY}&units=imperial"

beer_api_url = f"https://sandbox-api.brewerydb.com/v2/beers/?key={BEER_API_KEY}"

currency_conversion_api_url = (
    f"http://data.fixer.io/api/latest?access_key={CURRENCY_CONVERSION_KEY}"
)

changelog_api_url = "https://api.github.com/repos/jakewheeler/line-bot/commits"

lunchmoney_api_url = (
    f"https://dev.lunchmoney.app/v1/transactions?access_token={LUNCHMONEY_API_KEY}"
)


def money_spent_on_coffee_this_month():
    category_url = "&category_id=183868"  # this is ☕️

    start_date = datetime.datetime.today().date().replace(day=1)
    end_date = datetime.datetime.now().date()
    date_url = f"&start_date={start_date}&end_date={end_date}"
    full_coffee_url = lunchmoney_api_url + date_url + category_url
    response = requests.get(full_coffee_url)
    if response.status_code == 200:
        try:
            data = json.loads(response.content.decode("utf-8"))["transactions"]
            prices_list = [float(transaction["amount"]) for transaction in data]
            total = sum(prices_list)
            return f"Since {start_date.strftime('%b %d %Y')}, Jake has spent ${total:.2f} on delicious coffee ☕️"
        except:
            return "No ☕️ data yet!"
    else:
        return "Bad response from Lunch Money API 😞"


def josh():
    emoji = random_emoji()
    try:
        # emoji and text
        return f"Josh is a {emoji[0]} ({emoji[2]})"
    except:
        return "I broke trying to call Josh an emoji."


def get_usd_to_yen(amt):
    if amt is None or amt == "":
        return "Please specify an amount."
    response = requests.get(currency_conversion_api_url)
    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))

        # need to convert from USD to EUR
        usd = float(amt) / float(data["rates"]["USD"])
        jpy = float(usd) * float(data["rates"]["JPY"])
        return f"JP¥{jpy:.2f}"

    return "USD to JPY might be fucked right now."


def get_yen_to_usd(amt):
    if amt is None or amt == "":
        return "Please specify an amount."
    response = requests.get(currency_conversion_api_url)
    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))
        jpy = float(amt) * float(data["rates"]["USD"])
        usd = float(jpy) / float(data["rates"]["JPY"])
        return f"${usd:.2f}"

    return "JPY to USD might be fucked right now."


def get_japan_time():
    jp = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
    jesse_date = jp.strftime("It is currently %b %d %Y at %I:%M:%S %p for Jesse.")
    return jesse_date


def _is_friday():
    Friday = 4
    jp_day = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo")).weekday()
    us_day = datetime.datetime.now(tz=pytz.timezone("US/Eastern")).weekday()
    return us_day == Friday or jp_day == Friday


def get_friday_video():
    if _is_friday():
        return "https://www.youtube.com/shorts/A40dWK-T6lM"
    return "Not Friday 😔"


def get_japan_weather_info():
    response = requests.get(weather_api_url)
    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))

        curr_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        return f"Jesse is experiencing {curr_temp} F weather and a humidity of {humidity}%."
    else:
        return "Weather API might be fucked up right now or command is incorrect. Try `!help`."


def get_beer():
    response = requests.get(beer_api_url)
    if response.status_code == 200:
        body = json.loads(response.content.decode("utf-8"))
        random_beer_num = math.floor(random.randint(1, len(body["data"])))
        random_beer = body["data"][random_beer_num]

        beer = random_beer["name"]
        abv = random_beer["abv"]
        return f"Jesse is currently drinking a {beer} with an ABV of {abv}%"
    else:
        return "Beer API might be fucked up right now or command is incorrect. Try `!help`."


def get_changelog():
    headers = {"Authorization": f"Bearer {GITHUB_API_KEY}"}
    response = requests.get(changelog_api_url, headers=headers).json()

    line_msg = ""
    for i in range(3):
        record = response[i]
        name = record["author"]["login"]
        time = record["commit"]["author"]["date"][0:10]

        message = record["commit"]["message"]
        line_msg = line_msg + f"{name} ({time}): {message}\n"

    return line_msg[:-1]


def get_help():
    help_text = ""
    for v in cmd.values():
        help_text += v["syntax"] + ": " + v["detail"] + "\n"
    return help_text[:-1]  # remove \n from the end


cmd = {
    "!help": {
        "syntax": "!help",
        "hasParams": False,
        "func": get_help,
        "detail": "Get command help",
    },
    "!time": {
        "syntax": "!time",
        "hasParams": False,
        "func": get_japan_time,
        "detail": "Get time in Yonezawa",
    },
    "!weather": {
        "syntax": "!weather",
        "hasParams": False,
        "func": get_japan_weather_info,
        "detail": "Get weather in Yonezawa",
    },
    "!beer": {
        "syntax": "!beer",
        "hasParams": False,
        "func": get_beer,
        "detail": "Get random beer",
    },
    "!rs": {
        "syntax": "!rs [item name]",
        "hasParams": True,
        "func": osrs.get_ge_price,
        "detail": "Gets current price of specified item from the Grand Exchange",
    },
    "!usdjpy": {
        "syntax": "!usdjpy [usd amt]",
        "hasParams": True,
        "func": get_usd_to_yen,
        "detail": "Converts USD to JPY",
    },
    "!jpyusd": {
        "syntax": "!jpyusd [jpy amt]",
        "hasParams": True,
        "func": get_yen_to_usd,
        "detail": "Converts JPY to USD",
    },
    "!josh": {
        "syntax": "!josh",
        "hasParams": False,
        "func": josh,
        "detail": "Calls Josh a random emoji",
    },
    "!friday": {
        "syntax": "!friday",
        "hasParams": False,
        "func": get_friday_video,
        "detail": "Its Friday 🤠",
    },
    "!cl": {
        "syntax": "!cl",
        "hasParams": False,
        "func": get_changelog,
        "detail": "Changelog - get the last 3 commits in the repository",
    },
    "!coffeemoney": {
        "syntax": "!coffeemoney",
        "hasParams": False,
        "func": money_spent_on_coffee_this_month,
        "detail": "Gets the amount of money Jake spent on coffee so far this month ☕️",
    },
}


def handle_cmd(chat_msg):
    for key in cmd.keys():
        if key in chat_msg:
            args = chat_msg[len(key) + 1 :]
            if args != None and args != "" and cmd[key]["hasParams"] == True:
                return cmd[key]["func"](args)
            elif cmd[key]["hasParams"] == False:
                return cmd[key]["func"]()
            else:
                return "Could not get command. Try !help."

    return ""


if __name__ == "__main__":
    test_text = "!help"

    test_resp = handle_cmd(test_text)
    print(test_resp)
