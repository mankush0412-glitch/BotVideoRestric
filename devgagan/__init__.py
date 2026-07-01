"""
devgagan/__init__.py — Bot + Userbot clients initialize hote hain yahan.
"""
import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, DEFAULT_SESSION

# ── Main Bot (BotToken se chalta hai) ────────────────────────────────────────
app = Client(
    "BotExtractor",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=60,
)

# ── Default Userbot (agar DEFAULT_SESSION set hai to seedha use hoga) ─────────
userrbot = None
if DEFAULT_SESSION:
    userrbot = Client(
        "default_userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=DEFAULT_SESSION,
    )
