import os, json, logging, gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask
from threading import Thread

# --- 1. CẤU HÌNH BIẾN MÔI TRƯỜNG ---
TOKEN = os.getenv('BOT_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')
ADMIN_ID = 7346983056 
PORT = int(os.environ.get("PORT", 8000))

CONTACT_URL = "https://t.me/NgDanhThanhTrung"
DONATE_URL = "https://ngdanhthanhtrung.github.io/Bank/"
WEB_URL = "https://ngdanhthanhtrung.github.io/Modules-NDTT-Premium/"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- 2. KẾT NỐI GOOGLE SHEETS ---
def get_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = os.getenv('GOOGLE_CREDS')
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        return spreadsheet.worksheet("modules"), spreadsheet.worksheet("users")
    except Exception as e:
        logging.error(f"Lỗi kết nối Sheet: {e}")
        return None, None

def get_info_kb():
    return [[InlineKeyboardButton("💬 Liên hệ Admin", url=CONTACT_URL),
             InlineKeyboardButton("☕ Donate", url=DONATE_URL)],
            [InlineKeyboardButton("✨ Web Hướng Dẫn", url=WEB_URL)]]

# --- 3. TỰ ĐỘNG LƯU THÔNG TIN NGƯỜI DÙNG ---
async def auto_register(u: Update):
    user = u.effective_user
    user_id, name = str(user.id), user.full_name
    username = f"@{user.username}" if user.username else "N/A"
    _, sheet_users = get_sheets()
    if not sheet_users: return
    ids = sheet_users.col_values(1)
    if user_id not in ids:
        sheet_users.append_row([user_id, name, username])

# --- 4. XỬ LÝ LỆNH ---
async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Khởi động Bot"),
        BotCommand("list", "Danh sách Module"),
        BotCommand("hdsd", "Hướng dẫn sử dụng"),
        BotCommand("info", "Liên hệ & Donate")
    ])

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await auto_register(u)
    welcome = (f"👋 Chào <b>{u.effective_user.first_name}</b>!\n\n"
               f"Sử dụng lệnh /hdsd để xem cách dùng.\n"
               f"Sử dụng /list để xem các Module hack mới nhất.")
    await u.message.reply_text(welcome, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await auto_register(u)
    if not u.message.text or not u.message.text.startswith('/'): return
    cmd = u.message.text.replace("/", "").lower()
    sheet_mod, sheet_users = get_sheets()

    # Lệnh /hdsd
    if cmd == "hdsd":
        text = ("📖 <b>HƯỚNG DẪN LỆNH:</b>\n\n"
                "• /list : Xem danh sách Module.\n"
                "• /info : Liên hệ & Donate.\n"
                "• <code>/[tên_module]</code> : Lấy link (VD: /locket).")
        if u.effective_user.id == ADMIN_ID:
            text += "\n\n⚡ <b>ADMIN:</b>\n• /list : Hiện thêm danh sách User.\n• /setlink : Thêm/Sửa Module."
        return await u.message.reply_text(text, parse_mode=ParseMode.HTML)

    # Lệnh /list (Phân quyền)
    if cmd == "list":
        mod_records = sheet_mod.get_all_records()
        msg_mod = "<b>📂 DANH SÁCH MODULE:</b>\n\n" + "\n".join([f"🔹 /{r['key']} - {r['title']}" for r in mod_records])
        await u.message.reply_text(msg_mod, parse_mode=ParseMode.HTML)
        if u.effective_user.id == ADMIN_ID:
            user_records = sheet_users.get_all_records()
            msg_user = "<b>👥 USER ĐÃ LƯU (ADMIN):</b>\n\n" + "\n".join([f"👤 {r['name']} ({r['username']})" for r in user_records])
            await u.message.reply_text(msg_user, parse_mode=ParseMode.HTML)
        return

    if cmd == "info":
        return await u.message.reply_text("📱 <b>THÔNG TIN HỖ TRỢ:</b>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))

    # Tra cứu Module và HIỂN THỊ HƯỚNG DẪN 4 BƯỚC
    mod_data = {r['key'].lower(): r for r in sheet_mod.get_all_records()}
    if cmd in mod_data:
        item = mod_data[cmd]
        guide = (f"✨ <b>HƯỚNG DẪN: {item['title'].upper()}</b> ✨\n\n"
                 f"1️⃣ <b>Copy URL:</b> Chạm giữ link bên dưới:\n<code>{item['url']}</code>\n\n"
                 f"2️⃣ <b>Shadowrocket:</b> Tab <b>Module</b> ➔ <b>Add Module</b> ➔ Dán URL ➔ OK.\n\n"
                 f"3️⃣ <b>HTTPS Decryption:</b>\n"
                 f"• Bật <b>HTTPS Decryption</b> trong Settings.\n"
                 f"• Chọn <b>Generate New CA</b> ➔ Install.\n"
                 f"• Vào Cài đặt máy ➔ Tin cậy chứng chỉ.\n\n"
                 f"4️⃣ <b>Kết nối:</b> Bật VPN và tận hưởng!\n\n"
                 f"⚠️ <i>Lưu ý: Luôn bật VPN khi sử dụng.</i>")
        kb = [[InlineKeyboardButton(f"🔗 Copy URL {item['title']}", url=item['url'])]] + get_info_kb()
        await u.message.reply_text(guide, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

# --- LỆNH QUẢN LÝ CỦA ADMIN ---
async def set_link(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID: return
    try:
        key, title, url = [a.strip() for a in " ".join(c.args).split("|")]
        sheet_mod, _ = get_sheets()
        cell = sheet_mod.find(key.lower(), in_column=1)
        if cell: sheet_mod.update(f'B{cell.row}:C{cell.row}', [[title, url]])
        else: sheet_mod.append_row([key.lower(), title, url])
        await u.message.reply_text(f"✅ Đã lưu Module: {title}")
    except: await u.message.reply_text("❌ Cú pháp: /setlink key | Tên | URL")

# --- KHỞI CHẠY WEB SERVER DUY TRÌ ---
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
