import os


TELEBOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_SHIFFER_LOGIN = os.getenv("API_SHIFFER_LOGIN")
API_SHIFFER_PASSWORD = os.getenv("API_SHIFFER_PASSWORD")

try:
    from config.local_config import *
except ImportError:
    pass
