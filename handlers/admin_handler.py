from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from config import ADMIN_IDS
from database.db import get_all_users, get_user, delete_user

def register_admin_handler(app):
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("users", show_users))

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Access denied.")
        return
    await update.message.reply_text("🛠 Admin Panel:\n/users\n/ban <id>\n/unban <id>")

async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    users = get_all_users()
    text = f"👥 Total Users: {len(users)}\n"
    for u in users[:20]:  # limit
        text += f"{u['id']} - {u['name']} ({u['gender']})\n"
    await update.message.reply_text(text)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    try:
        uid = int(context.args[0])
        user = get_user(uid)
        if user:
            user["banned"] = True
            delete_user(uid)
            await update.message.reply_text(f"⛔ User {uid} banned.")
        else:
            await update.message.reply_text("❌ User not found.")
    except:
        await update.message.reply_text("⚠️ Usage: /ban <user_id>")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    try:
        uid = int(context.args[0])
        user = get_user(uid)
        if user:
            user["banned"] = False
            delete_user(uid)
            await update.message.reply_text(f"✅ User {uid} unbanned.")
        else:
            await update.message.reply_text("❌ User not found.")
    except:
        await update.message.reply_text("⚠️ Usage: /unban <user_id>")
