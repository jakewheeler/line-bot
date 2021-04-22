# Line Bot

This project is a Line chat bot that I created for my group chat.

## Running the Bot

### API Keys

To get started, you will need your own API keys from:

- [Line](https://developers.line.biz/en/)
- [OpenWeatherMap](https://openweathermap.org/)
- [BreweryDB](https://www.brewerydb.com/)
- [fixer.io](https://fixer.io/)
- [GitHub](https://github.com/)
- [Firebase](https://firebase.google.com/)
- [Lunch Money](https://lunchmoney.app/)

All API keys can be had for free (besides Lunch Money, which you should pay for!)

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

## Bot Commands

- `!help` - Lists all available commands and how to use them
- `!time` - Gets the current time in the Yamagata Prefecture in Japan
- `!weather` - Gets the current temperature and humidity details in Yamagata Prefecture in Japan
- `!beer` - Gets a random beer and its ABV%
- `!rs [item name]` - Given an Old School Runescape item, gets the current price of the item from the Grand Exchange
- `!ac` - Gets the remaining days until Animal Crossing: New Horizons is released
- `!usdjpy [usd]` - Given an amount in US dollars, gets the equivalent amount in Japanese Yen
- `!jpyusd [jpy]` - Given an amount in Japanese Yen, gets the equivalent amount in US dollars
- `!josh` - Calls Josh a random emoji 🤠
- `!friday` - Adds Friday hype video to the chat (only works on Fridays)
- `!cl` - Changelog command shows the latest 3 commits in the repository
- `!covid [date range]` - Gets the difference in COVID-19 in Erie, PA cases and deaths between the date range provided
- `!coffeemoney` - Gets the total amount of money I've spent on coffee this month ☕️

## Payment Commands

- `!bankhelp` - Lists all commands below
- `!register [username]` - Register an account at the bank
- `!members` - Lists all members of the bank
- `!ubi` - Members can use this command to collect a paycheck once per day
- `!balance` - Check your account balance
- `!pay [username] [amount]` - Transfer a specified amount of money to another user
