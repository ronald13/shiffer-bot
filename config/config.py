import os


TELEBOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_SHIFFER_LOGIN = os.getenv("API_SHIFFER_LOGIN")
API_SHIFFER_PASSWORD = os.getenv("API_SHIFFER_PASSWORD")
API_SHIFFER_URL_BOT = os.getenv("API_SHIFFER_URL_BOT")
API_SHIFFER_ADD_CHAT_ID = os.getenv("API_SHIFFER_ADD_CHAT_ID")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

try:
    from config.local_config import *
except ImportError:
    pass
