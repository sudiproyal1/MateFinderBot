from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from database.db import get_user

waiting_users = {
    "match": [],
    "random": []
}
active_chats = {}  # user_id -> partner_id

def register_chat_handler(app):
    app.add_handler(CommandHandler("chat", start_chat_menu))
    app.add_handler(CommandHandler("randomchat", start_random_chat))  # ✅
    app.add_handler(CommandHandler("stop", stop_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

# /chat - menu
async def start_chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Match Chat", "Random Chat"]]
    await update.message.reply_text(
        "🧑‍🤝‍🧑 Choose chat type:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )

# /randomchat
async def start_random_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        await update.message.reply_text("⚠️ You’re already in a chat. Use /stop to end it.")
        return

    partner = match_user(user_id, "random")
    if partner:
        active_chats[user_id] = partner
        active_chats[partner] = user_id
        await context.bot.send_message(user_id, "🔗 Connected to a stranger! Say hi!")
        await context.bot.send_message(partner, "🔗 A stranger connected with you!")
    else:
        await update.message.reply_text("⌛ Waiting for a partner...")

# message forwarder
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        await context.bot.send_message(chat_id=partner_id, text=update.message.text)

# /stop
async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_chats:
        await update.message.reply_text("❌ You are not in a chat.")
        return

    partner_id = active_chats.pop(user_id)
    active_chats.pop(partner_id, None)
    await update.message.reply_text("🛑 Chat ended.")
    await context.bot.send_message(partner_id, "🛑 Your chat partner left the chat.")

# Matchmaker core logic
def match_user(user_id, match_type):
    pool = waiting_users[match_type]
    if user_id in pool:
        return None
    if pool:
        partner_id = pool.pop(0)
        return partner_id
    else:
        pool.append(user_id)
        return None
