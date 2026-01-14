import os, json, logging, gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask
from threading import Thread

# --- 1. CẤU HÌNH ---
TOKEN = os.getenv('BOT_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')
ADMIN_ID = 7346983056 
PORT = int(os.environ.get("PORT", 8000))

# Thông tin cố định
CONTACT_URL = "https://t.me/NgDanhThanhTrung"
DONATE_URL = "https://ngdanhthanhtrung.github.io/Bank/"
WEB_URL = "https://ngdanhthanhtrung.github.io/Modules-NDTT-Premium/"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- 2. KẾT NỐI GOOGLE SHEETS ---
def get_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.getenv('GOOGLE_CREDS')
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        sheet = gspread.authorize(creds).open_by_key(SHEET_ID).get_worksheet(0)
        return sheet, sheet.get_all_records()
    except Exception as e:
        logging.error(f"Sheet Error: {e}"); return None, []

# Keyboard cố định cho Contact/Donate
def get_info_kb():
    return [
        [InlineKeyboardButton("💬 Liên hệ Admin", url=CONTACT_URL),
         InlineKeyboardButton("☕ Donate", url=DONATE_URL)],
        [InlineKeyboardButton("✨ Web Hướng Dẫn", url=WEB_URL)]
    ]

# --- 3. XỬ LÝ LỆNH ---
async def post_init(application):
    # Thiết lập menu lệnh nhanh bên trái ô chat
    await application.bot.set_my_commands([
        BotCommand("start", "Khởi động Bot"),
        BotCommand("list", "Danh sách Module hack"),
        BotCommand("info", "Thông tin liên hệ & Donate")
    ])

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Lời chào tích hợp sẵn các lệnh bấm nhanh
    welcome_text = (
        f"👋 Chào <b>{u.effective_user.first_name}</b>!\n\n"
        f"Tôi là Bot trợ lý cung cấp Module Premium.\n\n"
        f"🚀 <b>Các lệnh chính của tôi:</b>\n"
        f"• /list : Xem toàn bộ danh sách Module hiện có.\n"
        f"• /info : Xem thông tin liên hệ và ủng hộ Admin.\n\n"
        f"👉 Hoặc bạn có thể gõ trực tiếp tên Module (VD: /locket) để lấy hướng dẫn ngay lập tức."
    )
    await u.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(get_info_kb())
    )

async def set_link(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID: return
    try:
        # Cú pháp: /setlink locket | Locket Gold | https://url
        args = " ".join(c.args).split("|")
        key, title, url = [a.strip() for a in args]
        sheet, _ = get_data()
        cell = sheet.find(key.lower(), in_column=1)
        if cell:
            sheet.update(f'B{cell.row}:C{cell.row}', [[title, url]])
            txt = "Cập nhật"
        else:
            sheet.append_row([key.lower(), title, url])
            txt = "Thêm mới"
        await u.message.reply_text(f"✅ {txt} thành công: <b>{title}</b>", parse_mode=ParseMode.HTML)
    except:
        await u.message.reply_text("❌ Cú pháp: `/setlink key | Tên | URL`")

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message.text or not u.message.text.startswith('/'): return
    cmd = u.message.text.replace("/", "").lower()
    
    sheet, records = get_data()
    
    # Xử lý lệnh xem danh sách
    if cmd == "list":
        if not records:
            return await u.message.reply_text("Hiện tại chưa có Module nào trong hệ thống.")
        msg = "<b>📂 DANH SÁCH MODULE HIỆN CÓ:</b>\n\n" + "\n".join([f"🔹 /{r['key']} - {r['title']}" for r in records])
        return await u.message.reply_text(msg, parse_mode=ParseMode.HTML)
    
    # Xử lý lệnh xem thông tin hỗ trợ
    if cmd == "info":
        return await u.message.reply_text("📱 <b>THÔNG TIN HỖ TRỢ</b>\n\nBạn có thể liên hệ Admin hoặc ủng hộ kinh phí duy trì Bot tại đây:", 
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=InlineKeyboardMarkup(get_info_kb()))

    # Tra cứu lệnh động từ Google Sheet
    data = {r['key'].lower(): r for r in records}
    if cmd in data:
        item = data[cmd]
        guide = (f"✨ <b>HƯỚNG DẪN: {item['title'].upper()}</b> ✨\n\n"
                 f"1️⃣ <b>Copy URL:</b> Chạm giữ link bên dưới để sao chép:\n<code>{item['url']}</code>\n\n"
                 f"2️⃣ <b>Shadowrocket:</b> Tab <b>Module</b> ➔ <b>Add Module</b> ➔ Dán URL ➔ OK.\n\n"
                 f"3️⃣ <b>HTTPS Decryption:</b>\n"
                 f"• Bật <b>HTTPS Decryption</b> trong Settings.\n"
                 f"• Chọn <b>Generate New CA</b> ➔ Install.\n"
                 f"• Vào Cài đặt máy ➔ Đã tải về hồ sơ ➔ Tin cậy chứng chỉ.\n\n"
                 f"4️⃣ <b>Kết nối:</b> Bật VPN và tận hưởng!\n\n"
                 f"⚠️ <i>Lưu ý: Luôn duy trì VPN để dùng Premium.</i>")
        kb = [[InlineKeyboardButton("🔗 Mở liên kết Module", url=item['url'])]] + get_info_kb()
        await u.message.reply_text(guide, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

# --- 4. KHỞI CHẠY ---
server = Flask(__name__)
@server.route('/')
def ping(): return "Bot is Alive!", 200

if __name__ == "__main__":
    Thread(target=lambda: server.run(host="0.0.0.0", port=PORT), daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlink", set_link))
    app.add_handler(MessageHandler(filters.COMMAND, handle_msg))
    app.run_polling(drop_pending_updates=True)
