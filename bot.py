import os, json, logging, gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask
from threading import Thread

# --- CẤU HÌNH ---
TOKEN, SHEET_ID, ADMIN_ID = os.getenv('BOT_TOKEN'), os.getenv('SHEET_ID'), 7346983056
PORT = int(os.environ.get("PORT", 8000))
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- KẾT NỐI GOOGLE SHEETS ---
def get_data():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.getenv('GOOGLE_CREDS')), scope)
        sheet = gspread.authorize(creds).open_by_key(SHEET_ID).get_worksheet(0)
        return sheet, sheet.get_all_records()
    except Exception as e:
        logging.error(f"Sheet Error: {e}"); return None, []

# --- XỬ LÝ LỆNH ---
async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("👋 Chào mừng! Dùng /list để xem danh sách hoặc gõ lệnh trực tiếp (VD: /locket).")

async def set_link(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID: return
    try:
        key, title, url = [a.strip() for a in " ".join(c.args).split("|")]
        sheet, _ = get_data()
        cell = sheet.find(key.lower(), in_column=1)
        if cell:
            sheet.update(f'B{cell.row}:C{cell.row}', [[title, url]])
        else:
            sheet.append_row([key.lower(), title, url])
        await u.message.reply_text(f"✅ Đã lưu: <b>{title}</b>", parse_mode=ParseMode.HTML)
    except:
        await u.message.reply_text("❌ Cú pháp: `/setlink key | Tên | URL`", parse_mode=ParseMode.HTML)

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message.text.startswith('/'): return
    cmd = u.message.text.replace("/", "").lower()
    
    # Xử lý lệnh /list
    sheet, records = get_data()
    if cmd == "list":
        msg = "<b>📂 DANH SÁCH MODULE:</b>\n\n" + "\n".join([f"🔹 /{r['key']} - {r['title']}" for r in records])
        return await u.message.reply_text(msg, parse_mode=ParseMode.HTML)

    # Tra cứu và gửi hướng dẫn
    data = {r['key'].lower(): r for r in records}
    if cmd in data:
        item = data[cmd]
        guide = (f"✨ <b>HƯỚNG DẪN: {item['title'].upper()}</b> ✨\n\n"
                 f"1️⃣ <b>Copy URL:</b>\n<code>{item['url']}</code>\n\n"
                 f"2️⃣ <b>Shadowrocket:</b> Tab <b>Module</b> ➔ <b>Add Module</b> ➔ Dán URL.\n\n"
                 f"3️⃣ <b>HTTPS Decryption:</b> Bật và tin cậy CA trong Cài đặt.\n\n"
                 f"⚠️ <i>Lưu ý: Luôn bật VPN khi sử dụng.</i>")
        await u.message.reply_text(guide, parse_mode=ParseMode.HTML, 
                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Mở URL", url=item['url'])]]))

# --- CHẠY BOT ---
server = Flask(__name__)
@server.route('/')
def ping(): return "OK", 200

if __name__ == "__main__":
    Thread(target=lambda: server.run(host="0.0.0.0", port=PORT), daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlink", set_link))
    app.add_handler(MessageHandler(filters.COMMAND, handle_msg))
    app.run_polling(drop_pending_updates=True)
