import asyncio
from flask import Flask, request
from telegram import Update
from bot.main import initialize_bot

app = Flask(__name__)

# Initialize the bot application globally
# This will be done once when the Lambda function is initialized
# We need to run this in an event loop, but outside of a request context
# For Zappa, this is typically handled by the wsgi handler

# We will initialize the bot application when the first request comes in
# or use a global variable that gets initialized once.
# For simplicity, let's make it a global variable that gets initialized once.

_application = None

async def get_telegram_application():
    global _application
    if _application is None:
        _application = await initialize_bot()
    return _application

@app.route('/webhook', methods=['POST'])
async def webhook():
    telegram_application = await get_telegram_application()
    update = Update.de_json(request.get_json(force=True), telegram_application.bot)
    await telegram_application.process_update(update)
    return 'ok'

# This is for local development only, Zappa will not use this.
if __name__ == '__main__':
    # For local testing, we need to run the Flask app directly
    # and ensure the bot is initialized.
    # This part is not used when deployed with Zappa.
    print("Running Flask app locally. This is for testing purposes only.")
    # You would typically run this with a separate script for local development
    # For now, we'll just run the Flask app without the Telegram bot polling
    # as Zappa handles the webhook part.
    app.run(host='0.0.0.0', port=8080)