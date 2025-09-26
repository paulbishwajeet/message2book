from datetime import datetime
from bot.config import config

def is_business_hours():
    if not config.business_hours:
        return True  # No business hours configured, so always open

    now = datetime.now().time()
    start = datetime.strptime(config.business_hours['start'], '%H:%M').time()
    end = datetime.strptime(config.business_hours['end'], '%H:%M').time()

    return start <= now <= end
