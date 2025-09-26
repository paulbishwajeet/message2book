import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from bot.config import config
from bot.responses import get_response, send_response

# Rate limiting
user_timestamps = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Blacklist/Whitelist check
    if config.blacklist and user_id in config.blacklist:
        return
    if config.whitelist and user_id not in config.whitelist:
        return

    # Rate limiting check
    if config.rate_limit:
        now = time.time()
        if user_id in user_timestamps:
            time_since_last_message = now - user_timestamps[user_id]
            if time_since_last_message < config.rate_limit['seconds'] / config.rate_limit['messages']:
                return  # Ignore message
        user_timestamps[user_id] = now

    message_text = update.message.text
    user_name = update.effective_user.full_name

    response_text = get_response(message_text, user_name)
    await send_response(update, context, response_text)

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.full_name
    response_text = config.response_templates.get('default', "").replace("[USER_NAME]", user_name)
    await send_response(update, context, response_text)


message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
other_message_handler = MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.TEXT, handle_other_messages)
