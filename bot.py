import datetime
import json
import requests
import math
import random
import pytz
import os
import sys
import osrs

# from dotenv import load_dotenv
# load_dotenv()

weather_api_url = "https://api.openweathermap.org/data/2.5/weather?id=2110498&APPID={WEATHER_API_KEY}&units=imperial".format(
    WEATHER_API_KEY=os.getenv("APPID", None)
)
beer_api_url = "https://sandbox-api.brewerydb.com/v2/beers/?key={beerApiKey}".format(
    beerApiKey=os.getenv("BEER_API_KEY", None)
)
currency_conversion_api_url = "http://data.fixer.io/api/latest?access_key={currency_conversion__api_key}".format(
    currency_conversion__api_key=os.getenv("CURRENCY_CONVERSION_KEY", None)
)
ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", False)


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

        # need to convert from USD to EUR
        # 2,500 * 1.09 / 117
        jpy = float(amt) * float(data["rates"]["USD"])
        usd = float(jpy) / float(data["rates"]["JPY"])
        return f"${usd:.2f}"

    return "JPY to USD might be fucked right now."


def get_days_til_new_horizons():
    release = datetime.datetime(2020, 3, 20)
    today = datetime.datetime.now()
    delta = release - today
    return "There are {days} until AC:NH is out.".format(
        days=str(delta).split(",", 1)[0]
    )


def get_japan_time():
    jp = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
    jesse_date = jp.strftime("It is currently %b %d %Y at %H:%M:%S %p for Jesse.")
    return jesse_date


def get_japan_weather_info():
    response = requests.get(weather_api_url)
    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))

        curr_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        return "Jesse is experiencing {curr_temp} F weather and a humidity of {humidity}%.".format(
            curr_temp=curr_temp, humidity=humidity
        )
    else:
        return "Weather API might be fucked up right now or command is incorrect. Try `!help`."


def get_beer():
    response = requests.get(beer_api_url)
    if response.status_code == 200:
        body = json.loads(response.content.decode("utf-8"))
        random_beer_num = math.floor(random.randint(1, len(body["data"])))
        random_beer = body["data"][random_beer_num]
        return "Jesse is currently drinking a {beer} with an ABV of {abv}%".format(
            beer=random_beer["name"], abv=random_beer["abv"]
        )
    else:
        return "Beer API might be fucked up right now or command is incorrect. Try `!help`."


cmd = {
    "!help": {
        "syntax": "!help",
        "hasParams": False,
        "func": None,
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
    "!ac": {
        "syntax": "!ac",
        "hasParams": False,
        "func": get_days_til_new_horizons,
        "detail": "Gets number of days until Animal Crossing: New Horizons is available in the US",
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
}


def get_help():
    help_text = ""
    for v in cmd.values():
        help_text += v["syntax"] + ": " + v["detail"] + "\n"
    return help_text[:-1]  # remove \n from the end


if __name__ == "__main__":
    test_text = "!help"

    if ("!help") in test_text:
        print(get_help())
    else:
        for k in cmd.keys():
            if k in test_text:
                args = test_text[len(k) + 1 :]
                if args != None and args != "" and cmd[k]["hasParams"] == True:
                    print(cmd[k]["func"](args))
                elif cmd[k]["hasParams"] == False:
                    print(cmd[k]["func"]())
                else:
                    print("Could not get command")
