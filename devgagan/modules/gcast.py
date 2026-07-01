"""
gcast.py — Admin broadcast to all users
"""
import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from devgagan import app
from devgagan.core.mongo import db
from config import OWNER_ID


@app.on_message(filters.command("gcast") & filters.private)
async def gcast(_, message):
    if message.from_user.id not in OWNER_ID:
        return
    if not message.reply_to_message:
        return await message.reply("Jis message ko broadcast karna hai usse reply karo aur /gcast bhejo.")

    users = await db.all_users()
    sent = failed = 0
    status = await message.reply(f"📢 Broadcasting to {len(users)} users...")

    for uid in users:
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
            await message.reply_to_message.copy(uid)
            sent += 1
        except (InputUserDeactivated, UserIsBlocked):
            failed += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.1)

    await status.edit(
        f"✅ Broadcast done!\n\n"
        f"📨 Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )
