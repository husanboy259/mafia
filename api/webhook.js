const { Telegraf } = require('telegraf');
const config = require('../config');
const { setupBot } = require('../bot');

const bot = new Telegraf(config.TOKEN);
setupBot(bot);

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(200).send('Bot is running');
    return;
  }
  try {
    await bot.handleUpdate(req.body);
    res.status(200).send('OK');
  } catch (err) {
    console.error(err);
    res.status(500).send('Error');
  }
};
