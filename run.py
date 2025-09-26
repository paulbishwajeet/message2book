import asyncio
import logging
from bot.config import config
from bot.main import initialize_bot
from webserver import run_webserver

def start_polling_bot_sync(): # This function is now synchronous
    application = asyncio.run(initialize_bot()) # Initialize the async part
    logging.info("Starting bot in polling mode.")
    application.run_polling() # This is a blocking call

async def start_webhook_bot():
    application = await initialize_bot()
    logging.info("Starting bot in webhook mode.")
    await application.bot.set_webhook(config.webhook_url)
    logging.info(f"Webhook set to {config.webhook_url}")
    run_webserver(application)

if __name__ == '__main__':
    try:
        if config.use_webhook:
            asyncio.run(start_webhook_bot())
        elif config.polling_fallback:
            start_polling_bot_sync() # Call the synchronous function directly
        else:
            logging.warning("Polling is disabled and webhook is not configured. The bot will not run.")
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")