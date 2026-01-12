import os
import asyncio
from flask import Flask, request
from telegram import Update
import bot

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Flask(__name__)
telegram_app = bot.application

# cờ để chỉ set webhook 1 lần
webhook_ready = False


@app.route("/", methods=["GET"])
def index():
    global webhook_ready
    if not webhook_ready:
        asyncio.run(telegram_app.initialize())
        asyncio.run(telegram_app.bot.set_webhook(WEBHOOK_URL))
        webhook_ready = True
    return "OK", 200


@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )
    asyncio.run(telegram_app.process_update(update))
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
