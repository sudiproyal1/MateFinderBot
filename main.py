from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers.profile_handler import register_profile_handler
from handlers.find_handler import register_find_handlers
from handlers.chat_handler import register_chat_handler
from handlers.admin_handler import register_admin_handler
from handlers.stats_handler import register_stats_handler  # Optional: likehistory, skiphistory, likestats

def main():
    # Initialize MongoDB connection
    init_db()

    # Create bot application
    app = ApplicationBuilder().token(TOKEN).build()

    # Register all handlers
    register_profile_handler(app)
    register_find_handlers(app)
    register_chat_handler(app)
    register_admin_handler(app)
    register_stats_handler(app)  # Only if implemented

    # Run the bot
    print("✅ MateFinder bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
