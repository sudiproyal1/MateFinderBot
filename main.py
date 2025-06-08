from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers.profile_handler import register_profile_handlers
from handlers.find_handler import register_find_handlers
from handlers.chat_handler import register_chat_handlers
from handlers.admin_handler import register_admin_handlers

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Register all handlers
register_profile_handlers(app)
register_find_handlers(app)
register_chat_handlers(app)
register_admin_handlers(app)

print("🤖 MateFinder Bot is running...")
app.run_polling()
