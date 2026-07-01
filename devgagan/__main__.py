"""
devgagan/__main__.py — Entry point: python -m devgagan
Saare modules load karta hai, bot start karta hai.
"""
import asyncio
import importlib
import logging
import threading
from devgagan import app, userrbot
from config import DEFAULT_SESSION
from app import run_flask   # Flask web server (Render keep-alive)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modules to load (order matters for dependency-free loading)
MODULES = [
    "devgagan.modules.start",
    "devgagan.modules.login",
    "devgagan.modules.main",
    "devgagan.modules.settings",
    "devgagan.modules.stats",
    "devgagan.modules.plans",
    "devgagan.modules.gcast",
    "devgagan.modules.eval",
]


async def main():
    for mod in MODULES:
        importlib.import_module(mod)
        logger.info(f"Loaded: {mod}")

    # Start default userbot if session provided
    if userrbot:
        await userrbot.start()
        me = await userrbot.get_me()
        logger.info(f"Default userbot: {me.first_name} (@{me.username})")

    await app.start()
    me = await app.get_me()
    logger.info(f"Bot started: {me.first_name} (@{me.username})")
    logger.info("BotExtractor is running...")

    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    # Flask web thread (keep-alive ping for Render free tier)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask web server started (keep-alive)")

    asyncio.run(main())
