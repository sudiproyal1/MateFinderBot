from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import get_user, get_user_by_id

def register_stats_handler(app):
    app.add_handler(CommandHandler("likehistory", like_history))
    app.add_handler(CommandHandler("skiphistory", skip_history))
    app.add_handler(CommandHandler("likestats", like_stats))

async def like_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    likes = user.get("likes", [])
    if not likes:
        await update.message.reply_text("💔 You haven't liked anyone yet.")
        return
    names = [get_user_by_id(uid)["name"] for uid in likes if get_user_by_id(uid)]
    await update.message.reply_text("❤️ You liked:\n" + "\n".join(names))

async def skip_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    skips = user.get("skips", [])
    if not skips:
        await update.message.reply_text("✅ You haven't skipped anyone.")
        return
    names = [get_user_by_id(uid)["name"] for uid in skips if get_user_by_id(uid)]
    await update.message.reply_text("👎 You skipped:\n" + "\n".join(names))

async def like_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_users = context.bot_data["all_users"] = context.bot_data.get("all_users") or []
    if not all_users:
        from database.db import get_all_users
        all_users = get_all_users()
        context.bot_data["all_users"] = all_users

    likes_received = sum([1 for u in all_users if user_id in u.get("likes", [])])
    skips_received = sum([1 for u in all_users if user_id in u.get("skips", [])])

    await update.message.reply_text(f"📊 Stats:\n❤️ Likes received: {likes_received}\n👎 Skips received: {skips_received}")
