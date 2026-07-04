"""
devgagan/__init__.py — Bot + Userbot clients initialize hote hain yahan.

IMPORTANT: Yeh ab exact wahi PROVEN boot pattern use karta hai jo user ke
working reference bot (BMC) mein hai — explicit event loop banao, use current
loop set karo, aur app.start() ko IMPORT TIME PAR hi run_until_complete se
chala do (asyncio.run() ke bajaye, jo apna naya loop banata/band karta hai
aur kabhi kabhi cleanup timing masla de sakta hai).
"""
import asyncio
import logging
import sys
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, DEFAULT_SESSION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ── Main Bot (BotToken se chalta hai) ────────────────────────────────────────
app = Client(
    "BotExtractor",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=60,
    workers=50,
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


async def _boot_clients():
    await app.start()
    getme = await app.get_me()
    logger.info(f"Bot started: {getme.first_name} (@{getme.username})")

    if userrbot:
        try:
            await userrbot.start()
            ume = await userrbot.get_me()
            logger.info(f"Default userbot: {ume.first_name} (@{ume.username})")
        except Exception:
            logger.exception("❌ userrbot.start() failed — continuing without default userbot")


# Bot ko YAHIN, import time par hi start kar dete hain — exact wahi pattern
# jo proven working reference bot mein hai. Isse __main__.py sirf idle()
# call karke process ko zinda rakhta hai, koi extra asyncio.run() wrapper
# layer nahi jo cleanup/shutdown timing masla de sake.
loop.run_until_complete(_boot_clients())
