"""
stats.py — Admin: user stats, broadcast
"""
from pyrogram import filters
from devgagan import app
from devgagan.core.mongo import db
from devgagan.core.mongo.plans_db import all_premium_users
from config import OWNER_ID


@app.on_message(filters.command("stats") & filters.private)
async def stats(_, message):
    if message.from_user.id not in OWNER_ID:
        return
    total   = await db.total_users()
    premium = len(await all_premium_users())
    await message.reply(
        f"📊 **Bot Stats**\n\n"
        f"👥 Total users: `{total}`\n"
        f"⭐ Premium users: `{premium}`\n"
        f"🆓 Free users: `{total - premium}`"
    )
