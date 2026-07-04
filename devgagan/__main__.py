"""
devgagan/__main__.py — Entry point: python -m devgagan

Ab yeh EXACT proven pattern follow karta hai (jaisa working reference bot
mein hai): bot pehle hi devgagan/__init__.py import hote hi start ho chuka
hota hai, yahan sirf modules load karke pyrogram ka apna `idle()` call karte
hain — yeh Pyrogram ka official, battle-tested "process ko zinda rakho aur
SIGINT/SIGTERM tak sun te raho" mechanism hai.

Extra hardening (hamare crash-debugging se):
  - PYTHONUNBUFFERED + stdout logging — koi bhi crash log turant flush hota
    hai, Render ke buffered-stdout ki wajah se kabhi gum nahi hota.
  - Poora boot ek restart-loop mein hai — agar kabhi crash ho jaaye, poora
    traceback log hoga aur process khud 5s baad restart ho jaayega.
  - asyncio loop-level exception handler — background handler-task ke
    unhandled errors bhi ab explicitly logged honge.
"""
import asyncio
import importlib
import logging
import sys
import threading
import time
import traceback
from pyrogram import idle
from devgagan import app, userrbot, loop
from app import run_flask, start_self_ping

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# diagnostics MUST be first (logs every update); conversation.py must load
# before login.py and settings.py since they import shared state from it
MODULES = [
    "devgagan.modules.diagnostics",
    "devgagan.modules.conversation",
    "devgagan.modules.start",
    "devgagan.modules.login",
    "devgagan.modules.main",
    "devgagan.modules.settings",
    "devgagan.modules.stats",
    "devgagan.modules.plans",
    "devgagan.modules.gcast",
    "devgagan.modules.eval",
]


def _loop_exception_handler(_loop, context):
    """Catches exceptions raised inside background asyncio Tasks (e.g. a
    handler task) that would otherwise silently vanish into stderr."""
    exc = context.get("exception")
    msg = context.get("message")
    if exc:
        logger.error(f"💥 UNHANDLED asyncio exception: {msg}", exc_info=exc)
    else:
        logger.error(f"💥 UNHANDLED asyncio error context: {context}")


async def devggn_boot():
    for mod in MODULES:
        importlib.import_module(mod)
        logger.info(f"Loaded: {mod}")

    logger.info("BotExtractor is running...")
    await idle()
    logger.info("Bot stopped (idle() returned — SIGINT/SIGTERM received).")


def run_forever():
    """Restart-loop — agar boot/idle kisi bhi wajah se crash ho, poora
    traceback yahan log hoga aur bot khud-ba-khud 5 second baad restart
    hoga. Isse silent-crash mystery hamesha ke liye khatam ho jaayegi."""
    loop.set_exception_handler(_loop_exception_handler)
    while True:
        try:
            loop.run_until_complete(devggn_boot())
            break  # idle() returned normally (clean shutdown) — exit loop
        except Exception:
            logger.error("💥 FATAL CRASH in bot loop — full traceback below:")
            logger.error(traceback.format_exc())
            logger.error("🔄 Restarting bot in 5 seconds...")
            try:
                loop.run_until_complete(app.stop())
            except Exception:
                pass
            if userrbot:
                try:
                    loop.run_until_complete(userrbot.stop())
                except Exception:
                    pass
            time.sleep(5)
            try:
                loop.run_until_complete(app.start())
                if userrbot:
                    loop.run_until_complete(userrbot.start())
            except Exception:
                logger.error("💥 Restart attempt failed too — full traceback below:")
                logger.error(traceback.format_exc())


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask keep-alive started")

    # CRITICAL for Render free tier: without this, Render spins the whole
    # container down after ~15 min of no inbound HTTP traffic, killing the
    # bot's Telegram connection too — bot then stops responding to everything.
    start_self_ping()
    logger.info("Self-ping loop started (prevents Render free-tier spin-down)")

    run_forever()
