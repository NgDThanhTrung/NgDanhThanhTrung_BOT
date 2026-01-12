import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- 1. CẤU HÌNH (GIỮ NGUYÊN TỪ BẢN GỐC CỦA BẠN) ---
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 7346983056 

LOCKET_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/LOCKET/Locket_NDTT.sgmodule"
SPOTIFY_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/SPOTIFY/SPOTIFY.sgmodule"
YOUTUBE_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/YOUTUBE/YOUTUBE.sgmodule"
SPOTIFY_LOCKETGOLD_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/Test_modules/Tong_hop/Spotify_LocketGold.sgmodule"
SPOTIFY_YOUTUBE_LOCKET_RAW_URL = "https://raw.githubusercontent.com/NgDanhThanhTrung/modules/main/tonghopv2/Spotity_Youtube_Locket%20.conf"

WEB_URL = "https://ngdanhthanhtrung.github.io/Modules-NDTT-Premium/"
CONTACT_URL = "https://t.me/NgDanhThanhTrung"
DONATE_URL = "https://ngdanhthanhtrung.github.io/Bank/"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 2. LOGIC WEB SERVER (ĐỂ DÙNG GÓI FREE ECO) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Koyeb Web Service yêu cầu port 8080
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    logging.info("Web server started on port 8000")

# --- 3. LOGIC TELEGRAM BOT (GIỮ NGUYÊN NỘI DUNG CỦA BẠN) ---

async def post_init(application):
    commands = [
        BotCommand("start", "Khởi động bot"),
        BotCommand("hdsd", "Danh sách lệnh hỗ trợ"),
        BotCommand("locket", "Cài Locket Gold"),
        BotCommand("spotify", "Cài Spotify Premium"),
        BotCommand("youtube", "Cài YouTube Premium"),
    ]
    await application.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Chào mừng <b>{user.first_name}</b> đến với NgDanhThanhTrung_BOT!\n\n"
        "Gõ /hdsd để xem tất cả các hướng dẫn cài đặt Module.",
        parse_mode=ParseMode.HTML
    )

async def hdsd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✨ Web Hướng Dẫn", url=WEB_URL)],
        [InlineKeyboardButton("💬 Liên hệ Admin", url=CONTACT_URL), 
         InlineKeyboardButton("☕ Donate", url=DONATE_URL)]
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
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

async def send_guide(update, title, url, note=""):
    keyboard = [[InlineKeyboardButton(f"🔗 Sao chép URL {title}", url=url)]]
    guide_text = (
        f"✨ <b>HƯỚNG DẪN CÀI ĐẶT {title.upper()}</b> ✨\n\n"
        f"1️⃣ <b>Copy URL:</b> Chạm giữ link bên dưới để sao chép:\n<code>{url}</code>\n\n"
        f"2️⃣ <b>Shadowrocket:</b> Tab <b>Module</b> ➔ <b>Add Module</b> ➔ Dán URL ➔ OK.\n"
        f"{note}\n"
        f"3️⃣ <b>HTTPS Decryption:</b>\n"
        f"• Bật <b>HTTPS Decryption</b> trong Settings.\n"
        f"• Chọn <b>Generate New CA</b> ➔ Install.\n"
        f"• Vào Cài đặt máy ➔ Đã tải về hồ sơ ➔ Tin cậy chứng chỉ.\n\n"
        f"4️⃣ <b>Kết nối:</b> Bật VPN và tận hưởng!\n\n"
        f"⚠️ <b>LƯU Ý: NẾU TẮT VPN SẼ MẤT, INBOX AD ĐỂ ĐƯỢC HỖ TRỢ DÙNG LÂU DÀI</b>\n\n"
        f"💰 <b>Giá rẻ \"giật mình\" – Chỉ bằng vài ly trà sữa là có Combo trọn đời!</b>\n"
        f"👉 Nhắn tin tại đây: {CONTACT_URL}"
    )
    await update.message.reply_text(guide_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

# --- HANDLERS CHO CÁC MODULE ---
async def locket(u, c): await send_guide(u, "Locket Gold", LOCKET_RAW_URL)
async def spotify(u, c): await send_guide(u, "Spotify Premium", SPOTIFY_RAW_URL)
async def youtube(u, c): await send_guide(u, "YouTube Premium", YOUTUBE_RAW_URL)
async def combo2(u, c): await send_guide(u, "Combo Spotify & Locket", SPOTIFY_LOCKETGOLD_RAW_URL)
async def combo3(u, c): 
    note = "<i>(Lưu ý: File .conf này hoạt động tương tự Module)</i>\n"
    await send_guide(u, "Siêu Combo 3-trong-1", SPOTIFY_YOUTUBE_LOCKET_RAW_URL, note)

# --- 4. KHỞI CHẠY ---
async def main():
    if not TOKEN:
        logging.error("LỖI: Chưa có BOT_TOKEN!")
        return

    # 1. Chạy Web Server nền
    await start_web_server()

    # 2. Thiết lập Bot
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hdsd", hdsd))
    app.add_handler(CommandHandler("locket", locket))
    app.add_handler(CommandHandler("spotify", spotify))
    app.add_handler(CommandHandler("youtube", youtube))
    app.add_handler(CommandHandler("spotify_locketgold", combo2))
    app.add_handler(CommandHandler("spotify_youtube_locket", combo3))

    # 3. Chạy Polling song song với Web Server
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        # Giữ bot sống cho đến khi bị tắt
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
