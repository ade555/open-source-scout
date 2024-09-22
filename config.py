import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")

GH_APP_ID = os.getenv('GH_APP_ID')
GH_PRIVATE_KEY = os.getenv("GH_PRIVATE_KEY")
INSTALLATION_ID = os.getenv('INSTALLATION_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = os.getenv('PORT')

# States
CHOOSING, TYPING_REPLY = range(2)