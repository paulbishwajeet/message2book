import asyncio
from flask import Flask, request
from telegram import Update

app = Flask(__name__)

def run_webserver(application):
    @app.route('/webhook', methods=['POST'])
    async def webhook():
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return 'ok'

    app.run(host='0.0.0.0', port=8080)
