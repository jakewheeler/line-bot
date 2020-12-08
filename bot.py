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

# API URLs
weather_api_url = f"https://api.openweathermap.org/data/2.5/weather?id=2110498&APPID={WEATHER_API_KEY}&units=imperial"

beer_api_url = f"https://sandbox-api.brewerydb.com/v2/beers/?key={BEER_API_KEY}"

currency_conversion_api_url = (
    f"http://data.fixer.io/api/latest?access_key={CURRENCY_CONVERSION_KEY}"
)

changelog_api_url = "https://api.github.com/repos/jakewheeler/line-bot/commits"


def josh():
    emoji = random_emoji()
    try:
        # emoji and text
        return f"Josh is a {emoji[0]} ({emoji[2]})"
    except:
        return "I broke trying to call Josh an emoji."


def _parseDateToDict(date):
    return {"year": date[0:4], "month": date[5:7], "day": date[8:10]}


def _get_covid_url(start_date, end_date):
    erie_covid_url = (
        f"https://covid-19.datasettes.com/covid.json?sql=select+rowid%2C+date%2C+county%2C+state%2C+fips%2C+cases%2C+deaths"
        f"+from+ny_times_us_counties"
        f"+where+%22county%22+%3D+%3Ap0+and+(%22date%22+%3D+%3Ap1+or+%22date%22+%3D+%3Ap2)+and+%22state%22+%3D+%3Ap3"
        f"+order+by+date+desc+limit+101&p0=Erie&p1={start_date['year']}-{start_date['month']}-{start_date['day']}"
        f"&p2={end_date['year']}-{end_date['month']}-{end_date['day']}&p3=Pennsylvania"
    )
    return erie_covid_url


def _format_covid_date_output(date_dict):
    return datetime.datetime(
        int(date_dict["year"]), int(date_dict["month"]), int(date_dict["day"])
    )


def _parse_covid_input(dates):
    split = dates.split(" ")
    t1 = split[0]
    t2 = split[1]
    return t1, t2


def get_covid_cases(dates):
    # takes string as one arg which should probably change in the future
    try:
        t1, t2 = _parse_covid_input(dates)

        t1_dict = _parseDateToDict(t1)
        t2_dict = _parseDateToDict(t2)

        erie_url = _get_covid_url(t1_dict, t2_dict)

        response = requests.get(erie_url)

        # response is good so we can continue
        if response.status_code == 200:
            data = json.loads(response.content)
            days_data = data["rows"]

            # Unexpected response, should have both days
            if len(days_data) < 2:
                return "Unable to get both of the specified dates."

            date1 = _format_covid_date_output(t1_dict)
            date2 = _format_covid_date_output(t2_dict)

            cases = abs(int(days_data[0][5]) - int(days_data[1][5]))
            deaths = abs(int(days_data[0][6]) - int(days_data[1][6]))
            return f"Between {date1.strftime('%b %d %Y')} and {date2.strftime('%b %d %Y')}, there has been +{cases} cases and +{deaths} deaths in Erie, PA."
        else:
            return "Incorrect query."
    except:
        return "Error with input"


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


def get_days_til_new_horizons():
    release = datetime.datetime(2020, 3, 20)
    today = datetime.datetime.now()
    delta = release - today
    days = str(delta).split(",", 1)[0]
    return f"There are {days} until AC:NH is out."


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
        return "https://www.youtube.com/watch?v=S-CMaONmduM"
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
    "!covid": {
        "syntax": "!covid yyyy-mm-dd yyyy-mm-dd",
        "hasParams": True,
        "func": get_covid_cases,
        "detail": "Gets confirmed COVID-19 cases in Erie, PA as of today",
    },
}


def handle_cmd(chat_msg):
    for key in cmd.keys():
        if key in chat_msg:
            args = chat_msg[len(key) + 1 :]
            if args != None and args != "" and cmd[key]["hasParams"] == True:
                return True, cmd[key]["func"](args)
            elif cmd[key]["hasParams"] == False:
                return True, cmd[key]["func"]()
            else:
                return True, "Could not get command. Try !help."

    return False, ""


if __name__ == "__main__":
    test_text = "!covid 2020-04-12 2020-12-04"

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
                    print("Could not get command. Try !help.")
