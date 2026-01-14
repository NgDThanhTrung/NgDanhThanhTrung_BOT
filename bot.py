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
def get_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = json.loads(os.getenv('GOOGLE_CREDS'))
        client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope))
        ss = client.open_by_key(SHEET_ID)
        return ss.worksheet("modules"), ss.worksheet("users")
    except Exception as e:
        logging.error(f"Sheet Error: {e}"); return None, None

def get_info_kb():
    return [[InlineKeyboardButton("💬 Liên hệ Admin", url=CONTACT_URL),
             InlineKeyboardButton("☕ Donate", url=DONATE_URL)],
            [InlineKeyboardButton("✨ Web Hướng Dẫn", url=WEB_URL)]]
# --- 3. TỰ ĐỘNG LƯU NGƯỜI DÙNG ---
async def auto_register(u: Update):
    user = u.effective_user
    user_id = str(user.id)
    name = user.full_name
    username = f"@{user.username}" if user.username else "N/A"
    
    _, sheet_users = get_sheets()
    if not sheet_users: return
    
    ids = sheet_users.col_values(1)
    if user_id not in ids:
        sheet_users.append_row([user_id, name, username])
# --- 4. XỬ LÝ LỆNH ---
async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await auto_register(u)
    welcome = (f"👋 Chào <b>{u.effective_user.first_name}</b>!\n\n"
               f"Dùng /list để xem danh sách Module.\n"
               f"Dùng /info để liên hệ hỗ trợ.")
    await u.message.reply_text(welcome, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await auto_register(u)
    if not u.message.text or not u.message.text.startswith('/'): return
    
    cmd = u.message.text.replace("/", "").lower()
    sheet_mod, sheet_users = get_sheets()
        # --- XỬ LÝ LỆNH /LIST PHÂN QUYỀN ---
    if cmd == "list":
        # 1. Hiển thị danh sách Modules (Ai cũng thấy)
        mod_records = sheet_mod.get_all_records()
        if not mod_records:
            await u.message.reply_text("Chưa có Module nào.")
        else:
            msg_mod = "<b>📂 DANH SÁCH MODULE:</b>\n\n" + "\n".join([f"🔹 /{r['key']} - {r['title']}" for r in mod_records])
            await u.message.reply_text(msg_mod, parse_mode=ParseMode.HTML)        
        # 2. Nếu là Admin, hiển thị thêm danh sách Username người dùng
        if u.effective_user.id == ADMIN_ID:
            user_records = sheet_users.get_all_records()
            if user_records:
                msg_user = "<b>👥 DANH SÁCH NGƯỜI DÙNG (ADMIN ONLY):</b>\n\n"
                msg_user += "\n".join([f"👤 {r['name']} ({r['username']}) - <code>{r['user_id']}</code>" for r in user_records])
                await u.message.reply_text(msg_user, parse_mode=ParseMode.HTML)
        return

    if cmd == "info":
        return await u.message.reply_text("📱 <b>THÔNG TIN:</b>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))
    # Tra cứu Module động
    mod_data = {r['key'].lower(): r for r in sheet_mod.get_all_records()}
    if cmd in mod_data:
        item = mod_data[cmd]
        guide = (f"✨ <b>{item['title'].upper()}</b> ✨\n\n<code>{item['url']}</code>\n\n"
                 f"Shadowrocket ➔ Module ➔ Add Module ➔ Dán link.")
        await u.message.reply_text(guide, parse_mode=ParseMode.HTML, 
                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Copy Link", url=item['url'])]] + get_info_kb()))

async def set_link(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID: return
    try:
        key, title, url = [a.strip() for a in " ".join(c.args).split("|")]
        sheet_mod, _ = get_sheets()
        cell = sheet_mod.find(key.lower(), in_column=1)
        if cell: sheet_mod.update(f'B{cell.row}:C{cell.row}', [[title, url]])
        else: sheet_mod.append_row([key.lower(), title, url])
        await u.message.reply_text(f"✅ Đã lưu: {title}")
    except: await u.message.reply_text("❌ Cú pháp: /setlink key | Tên | URL")
# --- KHỞI CHẠY ---
server = Flask(__name__)
@server.route('/')
def ping(): return "OK", 200

if __name__ == "__main__":
    Thread(target=lambda: server.run(host="0.0.0.0", port=PORT), daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlink", set_link))
    app.add_handler(MessageHandler(filters.COMMAND, handle_msg))
    app.run_polling()
