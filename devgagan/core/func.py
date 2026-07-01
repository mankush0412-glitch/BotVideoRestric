"""
func.py — Helper utilities: subscription check, flood wait, progress bar
"""
import asyncio
import time
from pyrogram.errors import FloodWait
from config import CHANNEL_ID, OWNER_ID


async def subscribe(client, message):
    """Force-subscribe check — agar CHANNEL_ID set hai to user ko join karna padega."""
    if not CHANNEL_ID:
        return 0
    user_id = message.from_user.id
    if user_id in OWNER_ID:
        return 0
    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        if member.status.name in ("BANNED", "LEFT", "KICKED"):
            raise Exception("Not member")
        return 0
    except Exception:
        try:
            link = await client.export_chat_invite_link(CHANNEL_ID)
        except Exception:
            link = ""
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await message.reply(
            "⚠️ Pehle channel join karo, phir use karo.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Join Channel", url=link)
            ]])
        )
        return 1


async def chk_user(message, user_id):
    """
    Returns 0 = premium/owner, 1 = freemium.
    """
    if user_id in OWNER_ID:
        return 0
    from devgagan.core.mongo import db
    user = await db.get_data(user_id)
    if user and user.get("plan", 0) == 1:
        return 0
    return 1


async def progress_bar(current, total, text, message, start_time):
    """Inline progress bar — har 5 seconds mein update hota hai."""
    now = time.time()
    elapsed = now - start_time
    if elapsed < 5 and current != total:
        return

    percent = current * 100 / total if total else 0
    filled = int(percent / 5)
    bar = "█" * filled + "░" * (20 - filled)
    speed = current / elapsed if elapsed else 0
    eta = (total - current) / speed if speed else 0

    size_done = _human_size(current)
    size_total = _human_size(total)
    spd = _human_size(speed) + "/s"

    try:
        await message.edit(
            f"{text}\n"
            f"╰ [{bar}] {percent:.1f}%\n"
            f"📦 {size_done} / {size_total} | ⚡ {spd} | ⏱ {int(eta)}s"
        )
    except Exception:
        pass


def _human_size(b):
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} TB"
