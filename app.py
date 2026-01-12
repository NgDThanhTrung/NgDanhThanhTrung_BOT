import os
import asyncio
from flask import Flask, request
from telegram import Update
import bot

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Flask(__name__)
telegram_app = bot.application
webhook_ready = False


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )
    asyncio.run(telegram_app.process_update(update))
    return "OK", 200


def set_webhook_once():
    global webhook_ready
    if not webhook_ready:
        asyncio.run(telegram_app.initialize())
        asyncio.run(telegram_app.bot.set_webhook(WEBHOOK_URL + "webhook"))
        webhook_ready = True


set_webhook_once()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
