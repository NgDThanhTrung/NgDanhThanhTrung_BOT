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

CONTACT_URL = "https://t.me/NgDanhThanhTrung"
DONATE_URL = "https://ngdanhthanhtrung.github.io/Bank/"
WEB_URL = "https://ngdanhthanhtrung.github.io/Modules-NDTT-Premium/"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- 2. KẾT NỐI GOOGLE SHEETS ---
def get_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.getenv('GOOGLE_CREDS')
        if not creds_json:
            return "MISSING_CREDS", []
        
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
        return sheet, sheet.get_all_records()
    except Exception as e:
        logging.error(f"Sheet Error: {e}")
        return str(e), []

def get_info_kb():
    return [[InlineKeyboardButton("💬 Liên hệ Admin", url=CONTACT_URL),
             InlineKeyboardButton("☕ Donate", url=DONATE_URL)],
            [InlineKeyboardButton("✨ Web Hướng Dẫn", url=WEB_URL)]]

# --- 3. XỬ LÝ LỆNH ---
async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Khởi động Bot"),
        BotCommand("list", "Danh sách Module"),
        BotCommand("info", "Liên hệ & Donate")
    ])

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    welcome_text = (f"👋 Chào <b>{u.effective_user.first_name}</b>!\n\n"
                    f"Tôi là Bot cung cấp Module Premium.\n\n"
                    f"🚀 <b>Lệnh chính:</b>\n• /list : Xem danh sách\n• /info : Liên hệ & Donate\n\n"
                    f"👉 Gõ trực tiếp tên Module (VD: /locket) để lấy link.")
    await u.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))

async def set_link(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID: return
    
    # Kiểm tra cú pháp nhập vào
    raw_text = " ".join(c.args)
    if "|" not in raw_text or len(raw_text.split("|")) < 3:
        await u.message.reply_text("❌ <b>Sai cú pháp nhập liệu!</b>\n\nVui lòng nhập đúng:\n`/setlink key | Tên | URL`", parse_mode=ParseMode.HTML)
        return

    try:
        key, title, url = [a.strip() for a in raw_text.split("|")]
        sheet, _ = get_data()
        
        # Kiểm tra lỗi kết nối Sheet
        if isinstance(sheet, str):
            await u.message.reply_text(f"❌ <b>Lỗi kết nối Google Sheet!</b>\n\nChi tiết: <code>{sheet}</code>\n\nKiểm tra lại GOOGLE_CREDS và SHEET_ID trên Koyeb.", parse_mode=ParseMode.HTML)
            return

        cell = sheet.find(key.lower(), in_column=1)
        if cell:
            sheet.update(f'B{cell.row}:C{cell.row}', [[title, url]])
            txt = "Cập nhật"
        else:
            sheet.append_row([key.lower(), title, url])
            txt = "Thêm mới"
        await u.message.reply_text(f"✅ {txt} thành công: <b>{title}</b>", parse_mode=ParseMode.HTML)
    except Exception as e:
        await u.message.reply_text(f"❌ <b>Lỗi thực thi:</b> <code>{str(e)}</code>", parse_mode=ParseMode.HTML)

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message.text or not u.message.text.startswith('/'): return
    cmd = u.message.text.replace("/", "").lower()
    
    sheet, records = get_data()
    if isinstance(sheet, str): return # Bỏ qua nếu lỗi kết nối

    if cmd == "list":
        msg = "<b>📂 DANH SÁCH MODULE:</b>\n\n" + "\n".join([f"🔹 /{r['key']} - {r['title']}" for r in records])
        return await u.message.reply_text(msg, parse_mode=ParseMode.HTML)
    
    if cmd == "info":
        return await u.message.reply_text("📱 <b>HỖ TRỢ:</b>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))

    data = {r['key'].lower(): r for r in records}
    if cmd in data:
        item = data[cmd]
        guide = (f"✨ <b>HƯỚNG DẪN: {item['title'].upper()}</b> ✨\n\n"
                 f"1️⃣ <b>Copy URL:</b>\n<code>{item['url']}</code>\n\n"
                 f"2️⃣ <b>Shadowrocket:</b> Tab <b>Module</b> ➔ <b>Add Module</b> ➔ Dán URL.\n\n"
                 f"3️⃣ <b>HTTPS Decryption:</b> Bật & tin cậy CA trong Cài đặt.\n\n"
                 f"⚠️ <i>Lưu ý: Luôn duy trì VPN để dùng Premium.</i>")
        kb = [[InlineKeyboardButton("🔗 Mở liên kết Module", url=item['url'])]] + get_info_kb()
        await u.message.reply_text(guide, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

# --- 4. RUN ---
server = Flask(__name__)
@server.route('/')
def ping(): return "OK", 200

if __name__ == "__main__":
    Thread(target=lambda: server.run(host="0.0.0.0", port=PORT), daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlink", set_link))
    app.add_handler(MessageHandler(filters.COMMAND, handle_msg))
    app.run_polling(drop_pending_updates=True)
