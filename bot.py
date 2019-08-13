import datetime
import json
import requests
import math
import random
import pytz
import os

weather_api_url = 'https://api.openweathermap.org/data/2.5/weather?id=2110498&APPID={WEATHER_API_KEY}&units=imperial'.format(WEATHER_API_KEY=os.getenv('APPID', None))
beer_api_url = 'https://sandbox-api.brewerydb.com/v2/beers/?key={beerApiKey}'.format(beerApiKey=os.getenv('BEER_API_KEY', None))


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

def get_beer():
    response = requests.get(beer_api_url)
    if response.status_code == 200:
        body = json.loads(response.content.decode('utf-8'))
        random_beer_num = math.floor(random.randint(1, len(body['data'])))
        random_beer = body['data'][random_beer_num]
        return 'Jesse is currently drinking a {beer} with an ABV of {abv}%'.format(beer=random_beer['name'], abv=random_beer['abv'])
    else:
        return 'Beer API might be fucked up right now.'
