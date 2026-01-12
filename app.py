import os
import asyncio
from flask import Flask, request
from telegram import Update
import bot

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

app = Flask(__name__)
telegram_app = bot.application

# ✅ TẠO EVENT LOOP DUY NHẤT
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


async def setup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL + "webhook")


# ✅ CHẠY SETUP 1 LẦN DUY NHẤT
loop.run_until_complete(setup())


@app.route("/", methods=["GET"])
def index():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)

    # ✅ DÙNG LOOP CŨ – KHÔNG TẠO LOOP MỚI
    loop.create_task(telegram_app.process_update(update))

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
