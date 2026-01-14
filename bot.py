import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from flask import Flask
from threading import Thread

# --- 1. CẤU HÌNH ---
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 7346983056 
PORT = int(os.environ.get("PORT", 8000))

# Quản lý URL tập trung
URLS = {
    "locket": "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/LOCKET/Locket_NDTT.sgmodule",
    "spotify": "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/SPOTIFY/SPOTIFY.sgmodule",
    "youtube": "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/YOUTUBE/YOUTUBE.sgmodule",
    "combo2": "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/Test_modules/Tong_hop/Spotify_LocketGold.sgmodule",
    "combo3": "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/tonghopv2/Spotity_Youtube_Locket%20.conf",
    "web": "https://ngdanhthanhtrung.github.io/Modules-NDTT-Premium/",
    "contact": "https://t.me/NgDanhThanhTrung",
    "donate": "https://ngdanhthanhtrung.github.io/Bank/"
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

server = Flask(__name__)
@server.route('/')
def ping(): return "Bot is Online!", 200

# --- 2. LOGIC TRỢ GIÚP ---
def get_hdsd_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Web Hướng Dẫn", url=URLS["web"])],
        [InlineKeyboardButton("💬 Liên hệ Admin", url=URLS["contact"]), 
         InlineKeyboardButton("☕ Donate", url=URLS["donate"])]
    ])

# --- 3. HANDLERS ---
async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Khởi động bot"),
        BotCommand("hdsd", "Hướng dẫn sử dụng"),
        BotCommand("locket", "Locket Gold"),
        BotCommand("spotify", "Spotify Premium"),
        BotCommand("youtube", "YouTube Premium"),
        BotCommand("combo", "Các bản tổng hợp")
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Thông báo cho Admin khi có người dùng mới (Tùy chọn)
    try:
        await context.bot.send_message(ADMIN_ID, f"👤 Người dùng mới: {user.full_name} (@{user.username})")
    except: pass

    await update.message.reply_text(
        f"👋 Chào <b>{user.first_name}</b>!\n\nTôi là trợ lý hỗ trợ cài đặt Module Premium.\n"
        "Bấm /hdsd để bắt đầu.",
        parse_mode=ParseMode.HTML
    )

async def hdsd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>📚 DANH SÁCH LỆNH:</b>\n\n"
        "💛 /locket - Locket Gold\n"
        "🎵 /spotify - Spotify Premium\n"
        "🔴 /youtube - YouTube Premium\n"
        "💎 /combo - Các bản tổng hợp (2in1, 3in1)\n"
    )
    await update.message.reply_text(text, reply_markup=get_hdsd_keyboard(), parse_mode=ParseMode.HTML)

async def send_guide(update: Update, title: str, key: str, is_conf=False):
    url = URLS[key]
    note = "<i>(Lưu ý: Đây là file .conf, cài đặt tương tự Module)</i>\n" if is_conf else ""
    
    guide_text = (
        f"✨ <b>HƯỚNG DẪN: {title.upper()}</b> ✨\n\n"
        f"1️⃣ <b>Sao chép link:</b>\n<code>{url}</code>\n\n"
        f"2️⃣ <b>Shadowrocket:</b>\nTab <b>Module</b> ➔ <b>Add Module</b> ➔ Dán link.\n"
        f"{note}\n"
        f"3️⃣ <b>HTTPS Decryption:</b> Phải bật và tin cậy chứng chỉ CA trong cài đặt máy.\n\n"
        f"⚠️ <i>Lưu ý: Duy trì VPN để sử dụng tính năng Premium.</i>"
    )
    await update.message.reply_text(
        guide_text, 
        parse_mode=ParseMode.HTML, 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Mở liên kết", url=url)]])
    )

# --- 4. KHỞI CHẠY ---
def main():
    if not TOKEN: return print("LỖI: Thiếu BOT_TOKEN")
    
    Thread(target=lambda: server.run(host="0.0.0.0", port=PORT), daemon=True).start()
    
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    
    # Đăng ký các lệnh
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hdsd", hdsd))
    app.add_handler(CommandHandler("locket", lambda u, c: send_guide(u, "Locket Gold", "locket")))
    app.add_handler(CommandHandler("spotify", lambda u, c: send_guide(u, "Spotify Premium", "spotify")))
    app.add_handler(CommandHandler("youtube", lambda u, c: send_guide(u, "YouTube Premium", "youtube")))
    app.add_handler(CommandHandler("combo", lambda u, c: update.message.reply_text("Chọn combo:\n/spotify_locketgold\n/spotify_youtube_locket")))
    app.add_handler(CommandHandler("spotify_locketgold", lambda u, c: send_guide(u, "Combo 2in1", "combo2")))
    app.add_handler(CommandHandler("spotify_youtube_locket", lambda u, c: send_guide(u, "Siêu Combo 3in1", "combo3", True)))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
