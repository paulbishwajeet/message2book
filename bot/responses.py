import random
import time
from bot.config import config
from bot.utils import is_business_hours

def get_response(message_text: str, user_name: str) -> str:
    lower_message = message_text.lower()

    # Check for urgent keywords
    if any(keyword in lower_message for keyword in config.keywords.get('urgent', [])):
        return config.response_templates.get('urgent', "").replace("[USER_NAME]", user_name)

    # Check for greeting keywords
    if any(keyword in lower_message for keyword in config.keywords.get('greeting', [])):
        return config.response_templates.get('greeting', "").replace("[USER_NAME]", user_name)

    # Check for business hours
    if not is_business_hours():
        return config.response_templates.get('business_hours', "").replace("[USER_NAME]", user_name)

    # Default response
    return config.response_templates.get('default', "").replace("[USER_NAME]", user_name)

async def send_response(update, context, response_text):
    if not response_text:
        return

    # Simulate typing
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    time.sleep(random.uniform(1, 3))  # Simulate natural delay

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
