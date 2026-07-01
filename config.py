import os
from dotenv import load_dotenv

load_dotenv()

# ─── Required ───────────────────────────────────────────────
API_ID   = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID  = list(map(int, os.environ.get("OWNER_ID", "0").split()))
MONGO_DB  = os.environ.get("MONGO_DB", "")

# ─── Optional ───────────────────────────────────────────────
LOG_GROUP       = int(os.environ.get("LOG_GROUP", 0)) if os.environ.get("LOG_GROUP") else None
CHANNEL_ID      = int(os.environ.get("CHANNEL_ID", 0)) if os.environ.get("CHANNEL_ID") else None
FREEMIUM_LIMIT  = int(os.environ.get("FREEMIUM_LIMIT", "5"))
PREMIUM_LIMIT   = int(os.environ.get("PREMIUM_LIMIT", "200"))
DEFAULT_SESSION = os.environ.get("DEFAULT_SESSION", "")   # optional pre-set userbot session
