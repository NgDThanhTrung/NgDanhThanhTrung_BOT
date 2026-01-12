import os
import asyncio
from flask import Flask, request
from telegram import Update
from bot import application as telegram_app  # application trong bot.py

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://xxx.koyeb.app/webhook
PORT = int(os.getenv("PORT", 8000))

app = Flask(__name__)
loop = asyncio.get_event_loop()


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    loop.create_task(telegram_app.process_update(update))
    return "OK", 200


async def set_webhook():
    await telegram_app.bot.set_webhook(WEBHOOK_URL)


if __name__ == "__main__":
    loop.run_until_complete(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
