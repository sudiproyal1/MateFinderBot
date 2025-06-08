from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from database.db import get_all_users, get_user, add_to_list
import random

def register_find_handlers(app):
    app.add_handler(CommandHandler("find", start_finding))
    app.add_handler(CallbackQueryHandler(handle_action))

user_sessions = {}

async def start_finding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    all_users = get_all_users()
    current_user = get_user(user_id)

    # Filter profiles: not self, not skipped/liked, not banned
    potential = [
        u for u in all_users
        if u["id"] != user_id and
        user_id not in u.get("likes", []) and
        u["id"] not in current_user.get("likes", []) and
        u["id"] not in current_user.get("skips", []) and
        not u.get("banned", False)
    ]

    if not potential:
        await update.message.reply_text("🙁 No new profiles found.")
        return

    random.shuffle(potential)
    user_sessions[user_id] = potential
    await show_profile(update, context, user_id)

async def show_profile(update, context, user_id):
    session = user_sessions.get(user_id)
    if not session:
        await context.bot.send_message(user_id, "🔄 No more profiles. Use /find again later.")
        return

    profile = session[0]
    caption = f"👤 *{profile['name']}*, {profile['age']} ({profile['gender']})"
    if profile.get("place"):
        caption += f"\n🏙️ {profile['place']}"
    if profile.get("bio"):
        caption += f"\n📝 {profile['bio']}"

    keyboard = [
        [InlineKeyboardButton("👍 Like", callback_data=f"like_{profile['id']}"),
         InlineKeyboardButton("👎 Skip", callback_data=f"skip_{profile['id']}")],
        [InlineKeyboardButton("💬 Comment", callback_data=f"comment_{profile['id']}"),
         InlineKeyboardButton("🔄 Next", callback_data="next")]
    ]

    await context.bot.send_photo(
        chat_id=user_id,
        photo=profile["photo"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data
    if data.startswith("like_"):
        target_id = int(data.split("_")[1])
        add_to_list(user_id, "likes", target_id)
        await query.edit_message_caption(caption="❤️ You liked this profile.")
        await show_next(user_id, context)

    elif data.startswith("skip_"):
        target_id = int(data.split("_")[1])
        add_to_list(user_id, "skips", target_id)
        await query.edit_message_caption(caption="👎 You skipped this profile.")
        await show_next(user_id, context)

    elif data.startswith("comment_"):
        target_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="✍️ Feature coming soon: Comment System!")
    
    elif data == "next":
        await show_next(user_id, context)
        
elif data.startswith("like_"):
    target_id = int(data.split("_")[1])
    add_to_list(user_id, "likes", target_id)
    await query.edit_message_caption(caption="❤️ You liked this profile.")

    # ✅ MATCH DETECTION
    target_user = get_user(target_id)
    if target_user and user_id in target_user.get("likes", []):
        await context.bot.send_message(user_id, f"🎉 It's a Match! Start chatting with @{target_user['name']}!")
        await context.bot.send_message(target_id, f"🎉 You matched with @{query.from_user.first_name}!")
    
    await show_next(user_id, context)

async def show_next(user_id, context):
    session = user_sessions.get(user_id)
    if session:
        session.pop(0)
        if session:
            await show_profile(None, context, user_id)
        else:
            await context.bot.send_message(user_id, "✅ You've browsed all profiles. Use /find again to reshuffle.")
            user_sessions[user_id] = []
