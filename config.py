# config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "21924886"))
API_HASH = os.getenv("API_HASH", "80fedf65e709768ae7a1d1cababc76f9")
SESSION_STRING = os.getenv("SESSION_STRING", None)

OWNER_ID = int(os.getenv("OWNER_ID", "7507099068"))
DEVELOPER_IDS = [int(x) for x in os.getenv("DEVELOPER_IDS","2031172223").split(",") if x.strip().isdigit()]

FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "/usr/bin/ffmpeg")

def is_dev(user_id: int):
    return user_id == OWNER_ID or user_id in DEVELOPER_IDS