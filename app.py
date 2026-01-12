import os
import asyncio
from flask import Flask, request
from telegram import Update
import bot

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Flask(__name__)
telegram_app = bot.application

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok"

@app.before_first_request
def setup():
    asyncio.run(telegram_app.initialize())
    asyncio.run(telegram_app.bot.set_webhook(WEBHOOK_URL))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
