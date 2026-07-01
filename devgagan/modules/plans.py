"""
plans.py — Premium plan management (admin commands)
"""
from pyrogram import filters
from devgagan import app
from devgagan.core.mongo.plans_db import add_premium, remove_premium, is_premium
from config import OWNER_ID


@app.on_message(filters.command("add") & filters.private)
async def add_plan(_, message):
    if message.from_user.id not in OWNER_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Usage: `/add user_id`")
    try:
        uid = int(args[1])
    except ValueError:
        return await message.reply("❌ Valid user ID do.")
    await add_premium(uid)
    await message.reply(f"✅ `{uid}` ko premium mila!")


@app.on_message(filters.command("rem") & filters.private)
async def rem_plan(_, message):
    if message.from_user.id not in OWNER_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Usage: `/rem user_id`")
    try:
        uid = int(args[1])
    except ValueError:
        return await message.reply("❌ Valid user ID do.")
    await remove_premium(uid)
    await message.reply(f"✅ `{uid}` ka premium hata diya!")


@app.on_message(filters.command("myplan") & filters.private)
async def my_plan(_, message):
    uid = message.from_user.id
    premium = await is_premium(uid)
    if uid in OWNER_ID:
        await message.reply("👑 Tum Owner ho — unlimited access!")
    elif premium:
        await message.reply("⭐ Tum **Premium** user ho!")
    else:
        from config import FREEMIUM_LIMIT
        await message.reply(
            f"🆓 Tum **Free** user ho.\n"
            f"Limit: {FREEMIUM_LIMIT} files per session.\n\n"
            "Premium ke liye admin se contact karo."
        )
