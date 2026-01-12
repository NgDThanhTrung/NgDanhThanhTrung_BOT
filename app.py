import os
import asyncio
from flask import Flask, request
from telegram import Update
import bot

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Flask(__name__)
telegram_app = bot.application


async def setup_webhook():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)


# chạy khi start app
asyncio.run(setup_webhook())


# ✅ GET dùng cho health check + test
@app.route("/", methods=["GET"])
def index():
    return "OK", 200


# ✅ POST dùng cho Telegram webhook
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
