import asyncio
import logging
from bot.config import config
from bot.main import initialize_bot

def start_polling_bot_sync(): # This function is now synchronous
    application = asyncio.run(initialize_bot()) # Initialize the async part
    logging.info("Starting bot in polling mode.")
    application.run_polling() # This is a blocking call

if __name__ == '__main__':
    try:
        if config.polling_fallback:
            start_polling_bot_sync() # Call the synchronous function directly
        else:
            logging.warning("Polling is disabled. The bot will not run in polling mode.")
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")
