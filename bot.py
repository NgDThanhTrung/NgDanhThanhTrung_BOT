import os
import logging
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# --- 1. CẤU HÌNH ---
TOKEN = os.getenv("BOT_TOKEN")
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

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# --- 2. HỆ THỐNG ---
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
        [KeyboardButton("🔴 YouTube"), KeyboardButton("💎 Siêu Combo 3-in-1")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# --- 3. HANDLERS ---
async def post_init(application):
    commands = [
        BotCommand("start", "Khởi động bot"),
        BotCommand("hdsd", "Danh sách lệnh"),
        BotCommand("locket", "Locket Gold"),
        BotCommand("spotify", "Spotify Premium"),
        BotCommand("youtube", "YouTube Premium"),
        BotCommand("stats", "Thống kê"),
        BotCommand("backup", "Backup"),
        BotCommand("broadcast", "Thông báo"),
    ]
    await application.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    await update.message.reply_text(
        f"👋 Chào mừng <b>{user.first_name}</b> đến với NgDanhThanhTrung_BOT!\n\n"
        "Gõ /hdsd hoặc dùng menu bên dưới.",
        reply_markup=main_menu_keyboard(),
        parse_mode=ParseMode.HTML,
    )


async def hdsd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("✨ Web Hướng Dẫn", url=WEB_URL)],
        [
            InlineKeyboardButton("💬 Liên hệ Admin", url=CONTACT_URL),
            InlineKeyboardButton("☕ Donate", url=DONATE_URL),
        ],
    ]
    text = (
        "<b>📚 DANH SÁCH LỆNH:</b>\n\n"
        "💛 /locket\n"
        "🎵 /spotify\n"
        "🔴 /youtube\n\n"
        "<b>🎁 COMBO:</b>\n"
        "✌️ /spotify_locketgold\n"
        "💎 /spotify_youtube_locket"
    )
    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML
    )


async def send_guide(update, title, url, note=""):
    keyboard = [[InlineKeyboardButton("🔗 Sao chép URL", url=url)]]
    text = (
        f"✨ <b>{title.upper()}</b>\n\n"
        f"<code>{url}</code>\n\n"
        "Shadowrocket → Module → Add Module → Dán URL\n\n"
        f"{note}\n\n"
        f"📩 Hỗ trợ: {CONTACT_URL}"
    )
    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📚 Danh Sách Lệnh (HDSD)":
        await hdsd(update, context)
    elif text == "💛 Locket Gold":
        await locket(update, context)
    elif text == "🎵 Spotify":
        await spotify(update, context)
    elif text == "🔴 YouTube":
        await youtube(update, context)
    elif text == "💎 Siêu Combo 3-in-1":
        await combo3(update, context)


# --- ADMIN ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = " ".join(context.args)
    with open(USER_LIST_FILE) as f:
        users = f.read().splitlines()
    for uid in users:
        try:
            await context.bot.send_message(uid, msg)
            await asyncio.sleep(0.05)
        except:
            pass


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        with open(USER_LIST_FILE) as f:
            await update.message.reply_text(f"Tổng user: {len(f.readlines())}")


async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_document(open(USER_LIST_FILE, "rb"))


# --- LỆNH ---
async def locket(u, c): await send_guide(u, "Locket Gold", LOCKET_RAW_URL)
async def spotify(u, c): await send_guide(u, "Spotify Premium", SPOTIFY_RAW_URL)
async def youtube(u, c): await send_guide(u, "YouTube Premium", YOUTUBE_RAW_URL)
async def combo2(u, c): await send_guide(u, "Spotify + Locket", SPOTIFY_LOCKETGOLD_RAW_URL)
async def combo3(u, c): await send_guide(u, "Combo 3-in-1", SPOTIFY_YOUTUBE_LOCKET_RAW_URL)

# --- APPLICATION EXPORT ---
application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("hdsd", hdsd))
application.add_handler(CommandHandler("locket", locket))
application.add_handler(CommandHandler("spotify", spotify))
application.add_handler(CommandHandler("youtube", youtube))
application.add_handler(CommandHandler("spotify_locketgold", combo2))
application.add_handler(CommandHandler("spotify_youtube_locket", combo3))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("stats", stats))
application.add_handler(CommandHandler("backup", backup))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
