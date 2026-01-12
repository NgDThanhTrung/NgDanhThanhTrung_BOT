import os
import asyncio
from flask import Flask, request
from telegram import Update
from bot import application

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8000))

app = Flask(__name__)
loop = asyncio.get_event_loop()

@app.route("/", methods=["GET"])
def index():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop.create_task(application.process_update(update))
    return "OK", 200

async def setup():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    loop.run_until_complete(setup())
    app.run(host="0.0.0.0", port=PORT)
