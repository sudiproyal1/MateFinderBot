from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from database.db import save_user, get_user

ASK_NAME, ASK_AGE, ASK_GENDER, ASK_PHOTO, ASK_PLACE, ASK_BIO = range(6)

def register_profile_handler(app):
    app.add_handler(CommandHandler("profile", view_profile))
    app.add_handler(CommandHandler("edit", start_profile_creation))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start_profile_creation), CommandHandler("edit", start_profile_creation)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
            ASK_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_photo)],
            ASK_PHOTO: [MessageHandler(filters.PHOTO, ask_place)],
            ASK_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_bio)],
            ASK_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_profile)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

async def start_profile_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 What's your name?")
    return ASK_NAME

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("🎂 Enter your age:")
    return ASK_AGE

async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    keyboard = [["Male", "Female", "Other"]]
    await update.message.reply_text("🚻 Select your gender:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return ASK_GENDER

async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text("📷 Send your profile photo:", reply_markup=ReplyKeyboardRemove())
    return ASK_PHOTO

async def ask_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    context.user_data["photo"] = photo
    await update.message.reply_text("🏙️ Optional: What's your place?")
    return ASK_PLACE

async def ask_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["place"] = update.message.text
    await update.message.reply_text("📝 Optional: Write a short bio about yourself:")
    return ASK_BIO

async def save_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["bio"] = update.message.text
    user_data = {
        "id": update.effective_user.id,
        "name": context.user_data["name"],
        "age": context.user_data["age"],
        "gender": context.user_data["gender"],
        "photo": context.user_data["photo"],
        "place": context.user_data.get("place"),
        "bio": context.user_data.get("bio"),
        "likes": [],
        "skips": [],
        "banned": False,
    }
    save_user(user_data)
    await update.message.reply_text("✅ Profile saved!")
    return ConversationHandler.END

async def view_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("❌ You don't have a profile yet. Use /start or /edit.")
        return

    caption = f"👤 *Name*: {user['name']}\n🎂 *Age*: {user['age']}\n🚻 *Gender*: {user['gender']}"
    if user.get("place"):
        caption += f"\n🏙️ *Place*: {user['place']}"
    if user.get("bio"):
        caption += f"\n📝 *Bio*: {user['bio']}"

    await update.message.reply_photo(photo=user["photo"], caption=caption, parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
