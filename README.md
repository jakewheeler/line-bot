# Line Bot

This project is a Line chat bot that I created for my group chat.

## Running the Bot

### API Keys

To get started, you will need your own API keys from:

- [Line](https://developers.line.biz/en/)
- [OpenWeatherMap](https://openweathermap.org/)
- [BreweryDB](https://www.brewerydb.com/)
- [fixer.io](https://fixer.io/)

All API keys can be had for free, although with some limitations.

### Running Locally

1. Run `pip install -r requirements.txt` to install dependencies (recommended to do this in a virtual environment)
2. Obtain API keys and place them into your file called `.env`, which should look similar to the example file in this repository
3. In the main function of `bot.py` replace the variable called `test_text` with the command of your choice
4. Run `python bot.py` to test your command

### Deployment

For info on deployment, check out Line's guide on [building a bot](https://developers.line.biz/en/docs/messaging-api/building-bot/). Line recommends using Heroku, which is what this project is using.

Note that when deploying, your server will need to run the following script:

`python app.py`

If running on a Heroku Dyno, there is no need to modify the Procfile included in this repository.

## Usage

- `!help` - Lists all available commands and how to use them
- `!time` - Gets the current time in the Yamagata Prefecture in Japan
- `!weather` - Gets the current temperature and humidity details in Yamagata Prefecture in Japan
- `!beer` - Gets a random beer and its ABV%
- `!rs [item name]` - Given an Old School Runescape item, gets the current price of the item from the Grand Exchange
- `!ac` - Gets the remaining days until Animal Crossing: New Horizons is released
- `!usdjpy` - Given an amount in US dollars, gets the equivalent amount in Japanese Yen
- `!jpyusd` - Given an amount in Japanese Yen, gets the equivalent amount in US dollars
- `!josh` - Calls Josh a random emoji 🤠
- `!friday` - Adds Friday hype video to the chat (only works on Fridays)
