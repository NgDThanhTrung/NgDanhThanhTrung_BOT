import os, json, logging, gspread, threading
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask

# --- CẤU HÌNH ---
TOKEN, SHEET_ID, ADMIN_ID = os.getenv('BOT_TOKEN'), os.getenv('SHEET_ID'), 7346983056
PORT = int(os.environ.get("PORT", 8000))
CONTACT_URL, DONATE_URL = "https://t.me/NgDanhThanhTrung", "https://ngdanhthanhtrung.github.io/Bank/"
WEB_URL = "https://ngdanhthanhtrung.github.io/Modules-NDTT-Premium/"
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def get_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.getenv('GOOGLE_CREDS')), scope)
        ss = gspread.authorize(creds).open_by_key(SHEET_ID)
        return ss.worksheet("modules"), ss.worksheet("users")
    except Exception as e: logging.error(f"Sheet Error: {e}"); return None, None

def get_info_kb():
    return [[InlineKeyboardButton("💬 Liên hệ", url=CONTACT_URL), InlineKeyboardButton("☕ Donate", url=DONATE_URL)], [InlineKeyboardButton("✨ Web Hướng Dẫn", url=WEB_URL)]]

async def auto_reg(u: Update):
    user = u.effective_user
    if not user: return
    _, s_u = get_sheets()
    try:
        if str(user.id) not in s_u.col_values(1): s_u.append_row([str(user.id), user.full_name, f"@{user.username}" if user.username else "N/A"])
    except: pass

async def post_init(app):
    await app.bot.set_my_commands([BotCommand("start","Khởi động"), BotCommand("list","Module"), BotCommand("hdsd","HDSD"), BotCommand("info","Liên hệ")])

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await auto_reg(u)
    await u.message.reply_text(f"👋 Chào <b>{u.effective_user.first_name}</b>!\nSử dụng /hdsd hoặc /list để bắt đầu.", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await auto_reg(u)
    if not u.message.text or not u.message.text.startswith('/'): return
    cmd, uid = u.message.text.replace("/", "").lower().split('@')[0], u.effective_user.id
    s_m, s_u = get_sheets()
    if cmd == "hdsd":
        txt = "📖 <b>HDSD:</b>\n• /list: Xem Module\n• /info: Liên hệ\n• <code>/[tên_module]</code>: Lấy link"
        if uid == ADMIN_ID: txt += "\n\n⚡ <b>ADMIN:</b>\n• <code>/setlink key|Tên|URL</code>\n• <code>/delmodule key</code>\n• /list: Xem User"
        return await u.message.reply_text(txt, parse_mode=ParseMode.HTML)
    if cmd == "list":
        m_list = "<b>📂 MODULE:</b>\n" + "\n".join([f"🔹 /{r['key']} - {r['title']}" for r in s_m.get_all_records()])
        await u.message.reply_text(m_list, parse_mode=ParseMode.HTML)
        if uid == ADMIN_ID:
            u_list = "<b>👥 USERS:</b>\n" + "\n".join([f"👤 {r['name']} ({r['username']})" for r in s_u.get_all_records()])
            await u.message.reply_text(u_list, parse_mode=ParseMode.HTML)
        return
    if cmd == "info": return await u.message.reply_text("📱 <b>HỖ TRỢ:</b>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(get_info_kb()))
    db = {r['key'].lower(): r for r in s_m.get_all_records()}
    if cmd in db:
        item = db[cmd]
        guide = f"✨ <b>{item['title'].upper()}</b>\n\n<code>{item['url']}</code>\n\n1. Copy link\n2. Shadowrocket -> Module -> Add\n3. Bật VPN."
        await u.message.reply_text(guide, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"🔗 Mở Link", url=item['url'])]] + get_info_kb()))

async def set_link(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID: return
    try:
        k, t, l = [a.strip() for a in " ".join(c.args).split("|")]
        s_m, _ = get_sheets()
        cell = s_m.find(k.lower(), in_column=1)
        if cell: s_m.update(f'B{cell.row}:C{cell.row}', [[t, l]])
        else: s_m.append_row([k.lower(), t, l])
        await u.message.reply_text(f"✅ Đã lưu: {t}")
    except: await u.message.reply_text("❌ Cú pháp: /setlink key | Tên | URL")

async def del_mod(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id != ADMIN_ID or not c.args: return
    s_m, _ = get_sheets()
    try:
        cell = s_m.find(c.args[0].lower(), in_column=1)
        if cell: s_m.delete_rows(cell.row); await u.message.reply_text(f"🗑 Đã xóa: {c.args[0]}")
        else: await u.message.reply_text("🔍 Không tìm thấy.")
    except Exception as e: await u.message.reply_text(f"❌ Lỗi: {e}")

# --- RUN ---
server = Flask(__name__)
@server.route('/')
def ping(): return "OK", 200
if __name__ == "__main__":
    threading.Thread(target=lambda: server.run(host="0.0.0.0", port=PORT), daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start)); app.add_handler(CommandHandler("setlink", set_link))
    app.add_handler(CommandHandler("delmodule", del_mod)); app.add_handler(MessageHandler(filters.COMMAND, handle_msg))
    app.run_polling(drop_pending_updates=True)
