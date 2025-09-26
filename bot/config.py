import json
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self, config_file='config.json'):
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        with open(config_file, 'r') as f:
            config = json.load(f)

        if not self.telegram_token:
            self.telegram_token = config.get('telegram_token')

        if not self.telegram_token:
            raise ValueError("Telegram token not found in config.json or environment variables.")

        self.use_webhook = config.get('use_webhook', False)
        self.webhook_url = config.get('webhook_url')
        self.polling_fallback = config.get('polling_fallback', True)
        self.business_hours = config.get('business_hours')
        self.blacklist = config.get('blacklist', [])
        self.whitelist = config.get('whitelist', [])
        self.rate_limit = config.get('rate_limit')
        self.response_templates = config.get('response_templates')
        self.keywords = config.get('keywords')

config = Config()
