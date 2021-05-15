import express from 'express';
import { WebhookEvent, Client, middleware } from '@line/bot-sdk';
import { env } from './env';

const PORT = 5000;

const config = {
  channelAccessToken: env.lineChannelAccessToken,
  channelSecret: env.lineChannelSecret,
};

const app = express();
app.post('/webhook', middleware(config), (req, res) => {
  Promise.all(req.body.events.map(handleEvent)).then((result) =>
    res.json(result)
  );
});

const client = new Client(config);
function handleEvent(event: WebhookEvent) {
  if (event.type !== 'message' || event.message.type !== 'text') {
    return Promise.resolve(null);
  }

  console.log(event.message);

  return client.replyMessage(event.replyToken, {
    type: 'text',
    text: event.message.text,
  });
}

app.listen(PORT);
