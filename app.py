import os
import logging
import asyncio
from flask import Flask, request
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# ================== 1. CONFIG ==================
TOKEN = os.getenv('BOT_TOKEN') or "YOUR_TOKEN_HERE"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = 7346983056
USER_LIST_FILE = "users.txt"

LOCKET_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/LOCKET/Locket_NDTT.sgmodule"
SPOTIFY_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/SPOTIFY/SPOTIFY.sgmodule"
YOUTUBE_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/YOUTUBE/YOUTUBE.sgmodule"
SPOTIFY_LOCKETGOLD_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/Test_modules/Tong_hop/Spotify_LocketGold.sgmodule"
SPOTIFY_YOUTUBE_LOCKET_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/tonghopv2/Spotity_Youtube_Locket%20.conf"

WEB_URL = "https://ngdanhthanhtrung.github.io/Modules-NDTT-Premium/"
CONTACT_URL = "https://t.me/NgDanhThanhTrung"
DONATE_URL = "https://ngdanhthanhtrung.github.io/Bank/"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================== 2. FLASK + TELEGRAM APP ==================
flask_app = Flask(__name__)
tg_app: Application = ApplicationBuilder().token(TOKEN).build()

# ================== 3. LOGIC HỆ THỐNG ==================
def save_user(user_id):
    if not os.path.exists(USER_LIST_FILE):
        open(USER_LIST_FILE, "w").close()
    with open(USER_LIST_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_LIST_FILE, "a") as f:
            f.write(f"{user_id}\n")

def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📚 Danh Sách Lệnh (HDSD)")],
        [KeyboardButton("💛 Locket Gold"), KeyboardButton("🎵 Spotify")],
        [KeyboardButton("🔴 YouTube"), KeyboardButton("💎 Siêu Combo 3-in-1")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================== 4. HANDLERS ==================
async def post_init(application):
    commands = [
        BotCommand("start", "Khởi động bot"),
        BotCommand("hdsd", "Danh sách lệnh hỗ trợ"),
        BotCommand("locket", "Cài Locket Gold"),
        BotCommand("spotify", "Cài Spotify Premium"),
        BotCommand("youtube", "Cài YouTube Premium"),
        BotCommand("stats", "Thống kê (Admin)"),
        BotCommand("backup", "Backup User (Admin)"),
        BotCommand("broadcast", "Thông báo (Admin)")
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    await update.message.reply_text(
        f"👋 Chào mừng <b>{user.first_name}</b> đến với NgDanhThanhTrung_BOT!\n\n"
        "Gõ /hdsd hoặc chọn các nút bên dưới để xem hướng dẫn cài đặt Module.",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )

async def hdsd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("✨ Web Hướng Dẫn", url=WEB_URL)],
        [
            InlineKeyboardButton("💬 Liên hệ Admin", url=CONTACT_URL),
            InlineKeyboardButton("☕ Donate", url=DONATE_URL)
        ]
    ]
    text = (
        "<b>📚 DANH SÁCH LỆNH CÀI ĐẶT:</b>\n\n"
        "💛 /locket - Locket Gold\n"
        "🎵 /spotify - Spotify Premium\n"
        "🔴 /youtube - YouTube Premium\n\n"
        "<b>🎁 CÁC BẢN COMBO:</b>\n"
        "✌️ /spotify_locketgold - Combo 2-trong-1\n"
        "💎 /spotify_youtube_locket - Siêu Combo 3-trong-1\n\n"
        "<i>Hãy chọn lệnh tương ứng để lấy link Module!</i>"
    )
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

async def send_guide(update, title, url, note=""):
    keyboard = [[InlineKeyboardButton(f"🔗 Sao chép URL {title}", url=url)]]
    guide_text = (
        f"✨ <b>HƯỚNG DẪN CÀI ĐẶT {title.upper()}</b> ✨\n\n"
        f"1️⃣ <b>Copy URL:</b>\n<code>{url}</code>\n\n"
        f"2️⃣ <b>Shadowrocket:</b> Module ➔ Add ➔ Paste ➔ OK\n"
        f"{note}\n"
        f"3️⃣ <b>HTTPS Decryption:</b>\n"
        f"• Generate New CA ➔ Install ➔ Trust\n\n"
        f"4️⃣ <b>Kết nối:</b> Bật VPN\n\n"
        f"⚠️ <b>Tắt VPN là mất – Inbox để dùng lâu dài</b>\n\n"
        f"👉 {CONTACT_URL}"
    )
    await update.message.reply_text(
        guide_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📚 Danh Sách Lệnh (HDSD)": await hdsd(update, context)
    elif text == "💛 Locket Gold": await locket(update, context)
    elif text == "🎵 Spotify": await spotify(update, context)
    elif text == "🔴 YouTube": await youtube(update, context)
    elif text == "💎 Siêu Combo 3-in-1": await combo3(update, context)

# ================== 5. ADMIN ==================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Cú pháp: /broadcast [Nội dung]")
        return
    msg = " ".join(context.args)
    with open(USER_LIST_FILE, "r") as f:
        users = f.read().splitlines()
    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 <b>THÔNG BÁO:</b>\n\n{msg}",
                parse_mode=ParseMode.HTML
            )
            await asyncio.sleep(0.05)
        except:
            pass

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        with open(USER_LIST_FILE, "r") as f:
            count = len(f.read().splitlines())
        await update.message.reply_text(f"📊 Tổng: {count} người dùng.")

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_document(
            document=open(USER_LIST_FILE, 'rb'),
            caption="Backup Users"
        )

# ================== 6. ROUTES ==================
async def locket(u, c): await send_guide(u, "Locket Gold", LOCKET_RAW_URL)
async def spotify(u, c): await send_guide(u, "Spotify Premium", SPOTIFY_RAW_URL)
async def youtube(u, c): await send_guide(u, "YouTube Premium", YOUTUBE_RAW_URL)
async def combo2(u, c): await send_guide(u, "Combo Spotify & Locket", SPOTIFY_LOCKETGOLD_RAW_URL)
async def combo3(u, c): await send_guide(
    u, "Siêu Combo 3-in-1",
    SPOTIFY_YOUTUBE_LOCKET_RAW_URL,
    "<i>(File .conf dùng như Module)</i>\n"
)

# ================== 7. REGISTER HANDLERS ==================
tg_app.post_init = post_init
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("hdsd", hdsd))
tg_app.add_handler(CommandHandler("locket", locket))
tg_app.add_handler(CommandHandler("spotify", spotify))
tg_app.add_handler(CommandHandler("youtube", youtube))
tg_app.add_handler(CommandHandler("spotify_locketgold", combo2))
tg_app.add_handler(CommandHandler("spotify_youtube_locket", combo3))
tg_app.add_handler(CommandHandler("broadcast", broadcast))
tg_app.add_handler(CommandHandler("stats", stats))
tg_app.add_handler(CommandHandler("backup", backup))
tg_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

# ================== 8. WEBHOOK ==================
@flask_app.route("/", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    await tg_app.process_update(update)
    return "ok"

@flask_app.before_first_request
async def init_webhook():
    await tg_app.initialize()
    await tg_app.bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)
