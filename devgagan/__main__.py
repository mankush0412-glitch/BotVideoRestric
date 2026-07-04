"""
devgagan/__main__.py — Entry point: python -m devgagan
"""
import asyncio
import importlib
import logging
import threading
from devgagan import app, userrbot
from app import run_flask

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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


async def main():
    for mod in MODULES:
        importlib.import_module(mod)
        logger.info(f"Loaded: {mod}")

    if userrbot:
        await userrbot.start()
        me = await userrbot.get_me()
        logger.info(f"Default userbot: {me.first_name} (@{me.username})")

    await app.start()
    me = await app.get_me()
    logger.info(f"Bot started: {me.first_name} (@{me.username})")
    logger.info("BotExtractor is running...")

    await asyncio.Event().wait()


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask keep-alive started")
    asyncio.run(main())
