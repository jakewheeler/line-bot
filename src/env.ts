import dotenv from 'dotenv';
dotenv.config();

export const env = {
  enableLogging: process.env.ENABLE_LOGGING!,
  weatherApiKey: process.env.APPID!,
  beerApiKey: process.env.BEER_API_KEY!,
  currencyConversionKey: process.env.CURRENCY_CONVERSION_KEY!,
  lineChannelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN!,
  lineChannelSecret: process.env.LINE_CHANNEL_SECRET!,
  githubApiKey: process.env.GITHUB_API_KEY!,
  lunchMoneyApiKey: process.env.LUNCHMONEY_API_KEY!,
};
