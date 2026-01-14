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
    user_id, name = str(user.id), user.full_name
    username = f"@{user.username}" if user.username else "N/A"
    _, sheet_users = get_sheets()
    if not sheet_users: return
    ids = sheet_users.col_values(1)
    if user_id not in ids:
        sheet_users.append_row([user_id, name, username])

# --- 4. XỬ LÝ LỆNH ---
async def post_init(application):
    # Chỉ hiện các lệnh cơ bản trong Menu Bot cho tất cả mọi người
    await application.bot.set_my_commands([
        BotCommand("start", "Khởi động Bot"),
        BotCommand("list", "Danh sách Module"),
        BotCommand("hdsd", "Hướng dẫn sử dụng"),
        BotCommand("info", "Liên hệ & Donate")
    ])

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await auto_register(u)
    welcome = (f"👋 Chào <b>{u.effective_user.first_name}</b>!\n\n"
               f"Sử dụng /hdsd để xem hướng dẫn các lệnh.\n"
               f"Sử dụng /list để xem danh sách Module Premium.")
    await u.message.reply_text(welcome, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await auto_register(u)
    if not u.message.text or not u.message.text.startswith('/'): return
    cmd = u.message.text.replace("/", "").lower()
    sheet_mod, sheet_users = get_sheets()

    # --- LỆNH /HDSD (ĐÃ ẨN ADMIN) ---
    if cmd == "hdsd":
        text = ("📖 <b>HƯỚNG DẪN SỬ DỤNG:</b>\n\n"
                "• /list : Xem danh sách Module đang có.\n"
                "• /info : Thông tin liên hệ và ủng hộ.\n"
                "• <code>/[tên_module]</code> : Lấy link & hướng dẫn (VD: /locket).")
        # Chỉ hiện thêm nội dung nếu ID là Admin
        if u.effective_user.id == ADMIN_ID:
            text += "\n\n⚡ <b>QUYỀN ADMIN:</b>\n• /setlink key | Tên | URL\n• /list (tự hiện danh sách User)"
        return await u.message.reply_text(text, parse_mode=ParseMode.HTML)

    # --- LỆNH /LIST (ĐÃ ẨN ADMIN) ---
    if cmd == "list":
        mod_records = sheet_mod.get_all_records()
        msg_mod = "<b>📂 DANH SÁCH MODULE:</b>\n\n" + "\n".join([f"🔹 /{r['key']} - {r['title']}" for r in mod_records])
        await u.message.reply_text(msg_mod, parse_mode=ParseMode.HTML)
        
        # Chỉ Admin mới nhận được thêm tin nhắn danh sách User
        if u.effective_user.id == ADMIN_ID:
            user_records = sheet_users.get_all_records()
            msg_user = "<b>👥 DANH SÁCH NGƯỜI DÙNG:</b>\n\n" + "\n".join([f"👤 {r['name']} ({r['username']})" for r in user_records])
            await u.message.reply_text(msg_user, parse_mode=ParseMode.HTML)
        return

    if cmd == "info":
        return await u.message.reply_text("📱 <b>THÔNG TIN HỖ TRỢ:</b>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))

    # --- TRA CỨU MODULE (GIỮ NGUYÊN HƯỚNG DẪN 4 BƯỚC) ---
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
        kb = [[InlineKeyboardButton(f"🔗 Mở Link {item['title']}", url=item['url'])]] + get_info_kb()
        await u.message.reply_text(guide, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

# --- LỆNH ADMIN (ẨN HOÀN TOÀN) ---
async def set_link(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID: return # Người thường dùng lệnh này sẽ không có phản hồi
    try:
        key, title, url = [a.strip() for a in " ".join(c.args).split("|")]
        sheet_mod, _ = get_sheets()
        cell = sheet_mod.find(key.lower(), in_column=1)
        if cell: sheet_mod.update(f'B{cell.row}:C{cell.row}', [[title, url]])
        else: sheet_mod.append_row([key.lower(), title, url])
        await u.message.reply_text(f"✅ Đã lưu Module: {title}")
    except: await u.message.reply_text("❌ Cú pháp: /setlink key | Tên | URL")

# --- KHỞI CHẠY ---
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
