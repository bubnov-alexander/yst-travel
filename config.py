import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
TIMEZONE = os.getenv('TIMEZONE')
CHAT_ID = os.getenv('CHAT_ID')
