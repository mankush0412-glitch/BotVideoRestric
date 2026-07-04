"""
diagnostics.py — Loaded FIRST. Logs every incoming update so we can
confirm Telegram updates are actually reaching the bot's dispatcher.
Uses group=-1 so it never blocks normal command handlers (which stay in group 0).
"""
import logging
from pyrogram import filters
from devgagan import app

logger = logging.getLogger("BotExtractor.diagnostics")


@app.on_message(filters.all, group=-1)
async def log_all_messages(client, message):
    try:
        uid = message.chat.id if message.chat else "?"
        text = message.text or message.caption or f"<{message.media}>" if message.media else "<no text>"
        logger.info(f"📩 Message from {uid}: {text}")
    except Exception as e:
        logger.exception(f"diagnostics log_all_messages error: {e}")


@app.on_callback_query(filters.all, group=-1)
async def log_all_callbacks(client, cb):
    try:
        logger.info(f"🔘 Callback from {cb.from_user.id}: {cb.data}")
    except Exception as e:
        logger.exception(f"diagnostics log_all_callbacks error: {e}")
