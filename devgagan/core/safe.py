"""
safe.py — Decorator to catch & log exceptions in every handler.
Without this, an exception inside a handler can silently kill that update
with no visible error — looks like the bot is "dead" but it isn't.
"""
import logging
from functools import wraps

logger = logging.getLogger("BotExtractor.handlers")


def safe(func):
    @wraps(func)
    async def wrapper(client, update, *args, **kwargs):
        try:
            return await func(client, update, *args, **kwargs)
        except Exception as e:
            logger.exception(f"❌ Error in handler '{func.__name__}': {e}")
            try:
                if hasattr(update, "reply"):
                    await update.reply(f"❌ Internal error:\n`{e}`")
                elif hasattr(update, "answer"):
                    await update.answer(f"Error: {e}", show_alert=True)
            except Exception:
                pass
    return wrapper
