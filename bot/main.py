import logging
import asyncio
from telegram.ext import Application
from bot.config import config
from bot.handlers import message_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def initialize_bot():
    application = Application.builder().token(config.telegram_token).build()

    application.add_handler(message_handler)

    return application


