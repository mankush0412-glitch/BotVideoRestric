"""
main.py — Bot Content Extractor
=================================
Kisi bhi restricted/protected bot ka content extract karo — bina message ID ke.

How it works:
- Userbot apne Telegram DM se target bot ki poori history fetch karta hai
- protect_content=True sirf UI button disable karta hai; API se file_id milta hai
- Sab media download hoti hai Telegram server se, tere paas bheji jaati hai bina restriction ke

Commands:
  /getbot @botusername          — Us bot ke saare files nikalo (full history)
  /getbot @botusername 50       — Last 50 messages se files nikalo
  /cancel                       — Chal raha process band karo
"""

import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, PeerIdInvalid
from devgagan import app, userrbot
from devgagan.core.get_func import (
    upload_media, get_final_caption, rename_file,
    get_media_filename, get_message_file_size,
    user_chat_ids
)
from devgagan.core.func import subscribe, chk_user, progress_bar
from devgagan.core.mongo import db
from config import FREEMIUM_LIMIT, PREMIUM_LIMIT, OWNER_ID, API_ID, API_HASH, LOG_GROUP
import time
import os
import gc


users_loop = {}   # user_id -> True/False (running process tracker)


# ── Initialize userbot for a user ────────────────────────────────────────────
async def initialize_userbot(user_id):
    data = await db.get_data(user_id)
    if data and data.get("session"):
        try:
            userbot = Client(
                f"ub_{user_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=data.get("session")
            )
            await userbot.start()
            return userbot
        except Exception as e:
            await app.send_message(user_id, f"❌ Login expire ho gaya, /login dobara karo.\n`{e}`")
            return None
    else:
        if userrbot:
            return userrbot
        return None


# ── Core: fetch + upload ONE message ─────────────────────────────────────────
async def process_single_message(userbot, sender, msg, target_chat_id, topic_id):
    """
    Given a Pyrogram Message object (received by userbot from another bot),
    download its media and re-upload to sender — bypassing protect_content.
    Returns True if a file was sent, False if skipped.
    """
    file = None
    edit = None

    try:
        # Text only — no media
        if not msg.media and msg.text:
            return False

        # No content at all
        if not msg.media:
            return False

        caption = await get_final_caption(msg, sender)
        file_name = await get_media_filename(msg)
        edit = await app.send_message(sender, f"⬇️ Downloading...")

        # Download from Telegram server (works even if protect_content=True)
        file = await userbot.download_media(
            msg,
            file_name=file_name,
            progress=progress_bar,
            progress_args=(
                "╭─────────────────────╮\n│      **__Downloading...__**\n├─────────────────────",
                edit,
                time.time()
            )
        )

        if not file:
            await edit.delete()
            return False

        # Sticker
        if msg.sticker:
            await app.send_sticker(target_chat_id, msg.sticker.file_id, reply_to_message_id=topic_id)
            await edit.delete()
            if os.path.exists(file):
                os.remove(file)
            return True

        # Photo
        if msg.photo:
            result = await app.send_photo(target_chat_id, file, caption=caption, reply_to_message_id=topic_id)
            if LOG_GROUP:
                try:
                    await result.copy(LOG_GROUP)
                except Exception:
                    pass
            await edit.delete()
            if os.path.exists(file):
                os.remove(file)
            return True

        # Audio / Voice / Video Note — send as-is
        if msg.audio:
            file = await rename_file(file, sender)
            result = await app.send_audio(target_chat_id, file, caption=caption, reply_to_message_id=topic_id)
            if LOG_GROUP:
                await result.copy(LOG_GROUP)
            await edit.delete()
            if os.path.exists(file):
                os.remove(file)
            return True

        if msg.voice:
            result = await app.send_voice(target_chat_id, file, reply_to_message_id=topic_id)
            await edit.delete()
            if os.path.exists(file):
                os.remove(file)
            return True

        if msg.video_note:
            result = await app.send_video_note(target_chat_id, file, reply_to_message_id=topic_id)
            await edit.delete()
            if os.path.exists(file):
                os.remove(file)
            return True

        # Video or Document (PDF, etc.) — use upload_media for progress
        file = await rename_file(file, sender)
        await upload_media(sender, target_chat_id, file, caption, edit, topic_id)
        return True

    except Exception as e:
        print(f"Error processing msg {msg.id}: {e}")
        return False
    finally:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except Exception:
                pass
        if edit:
            try:
                await edit.delete()
            except Exception:
                pass
        gc.collect()


# ── /getbot — extract ALL files from a bot (no message ID needed) ─────────────
@app.on_message(filters.command("getbot") & filters.private)
async def get_from_bot(_, message):
    joined = await subscribe(_, message)
    if joined == 1:
        return

    user_id = message.chat.id

    if users_loop.get(user_id, False):
        await message.reply("⚠️ Ek process pehle se chal raha hai.\n/cancel karo ya khatam hone do.")
        return

    args = message.text.split()
    # Usage: /getbot @botusername [optional_limit]
    if len(args) < 2:
        await message.reply(
            "**📖 Usage:**\n"
            "`/getbot @botusername` — Saare files nikalo\n"
            "`/getbot @botusername 50` — Last 50 messages se files nikalo\n\n"
            "**Example:**\n"
            "`/getbot @SomeRestrictedBot`\n\n"
            "**Note:** Pehle us bot ko apne Telegram se `/start` bhejo, phir yahan extract karo."
        )
        return

    bot_peer = args[1].lstrip('@')

    # Optional limit
    limit = 0  # 0 = no limit (full history)
    if len(args) >= 3:
        try:
            limit = int(args[2])
        except ValueError:
            await message.reply("❌ Limit ek number hona chahiye.")
            return

    freecheck = await chk_user(message, user_id)
    if freecheck == 1 and FREEMIUM_LIMIT == 0 and user_id not in OWNER_ID:
        await message.reply("❌ Freemium available nahi. Premium lo.")
        return

    max_limit = FREEMIUM_LIMIT if freecheck == 1 else PREMIUM_LIMIT
    if limit == 0 or limit > max_limit:
        if freecheck == 1:
            limit = max_limit if max_limit > 0 else 50
        # Premium/owner: no cap unless explicitly set

    userbot = await initialize_userbot(user_id)
    if userbot is None:
        await message.reply("❌ Pehle /login karo.")
        return

    # Determine target output chat
    target_chat_id = user_chat_ids.get(user_id, user_id)
    topic_id = None
    if '/' in str(target_chat_id):
        target_chat_id, topic_id = map(int, str(target_chat_id).split('/', 1))

    status_msg = await message.reply(
        f"🔍 **@{bot_peer}** ki history scan ho rahi hai...\n"
        f"{'Limit: ' + str(limit) + ' messages' if limit else 'Full history scan'}\n\n"
        f"⏳ Please wait...",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🚫 Cancel", callback_data=f"cancel_{user_id}")
        ]])
    )

    users_loop[user_id] = True
    found = 0
    sent = 0
    scanned = 0

    try:
        # ── get_chat_history: no message ID needed ────────────────────────────
        # Iterates through ALL messages in userbot's DM with the target bot
        # protect_content=True messages are fully accessible via API
        async for msg in userbot.get_chat_history(bot_peer, limit=limit if limit else None):
            if not users_loop.get(user_id, False):
                break

            scanned += 1

            # Only process messages with media
            if not msg.media:
                continue

            found += 1
            ok = await process_single_message(userbot, user_id, msg, target_chat_id, topic_id)
            if ok:
                sent += 1

            # Update status every 10 files
            if found % 10 == 0:
                try:
                    await status_msg.edit(
                        f"📊 **Extracting from @{bot_peer}**\n\n"
                        f"🔍 Scanned: {scanned} messages\n"
                        f"📦 Media found: {found}\n"
                        f"✅ Sent: {sent}",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🚫 Cancel", callback_data=f"cancel_{user_id}")
                        ]])
                    )
                except Exception:
                    pass

            await asyncio.sleep(2)  # anti-flood

        # Done
        cancelled = not users_loop.get(user_id, True)
        await status_msg.edit(
            f"{'🚫 Cancelled!' if cancelled else '✅ Done!'}\n\n"
            f"🤖 Bot: @{bot_peer}\n"
            f"🔍 Scanned: {scanned} messages\n"
            f"📦 Media found: {found}\n"
            f"✅ Sent: {sent}"
        )

    except PeerIdInvalid:
        await status_msg.edit(
            f"❌ **@{bot_peer}** nahi mila.\n\n"
            "**Fix:** Pehle apne Telegram account se us bot ko `/start` bhejo, phir try karo."
        )
    except Exception as e:
        await status_msg.edit(f"❌ Error: `{str(e)}`")
    finally:
        users_loop.pop(user_id, None)


# ── Callback: cancel ──────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^cancel_(\d+)$"))
async def cancel_cb(client, cb):
    target_uid = int(cb.matches[0].group(1))
    if cb.from_user.id != target_uid and cb.from_user.id not in OWNER_ID:
        await cb.answer("Sirf tumhara process cancel ho sakta hai.", show_alert=True)
        return
    users_loop[target_uid] = False
    await cb.answer("Cancelling...")
    await cb.message.edit("🚫 Cancelling...")


# ── /cancel command ───────────────────────────────────────────────────────────
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(_, message):
    user_id = message.chat.id
    if users_loop.get(user_id, False):
        users_loop[user_id] = False
        await message.reply("🚫 Process cancel ho raha hai.")
    else:
        await message.reply("Koi process nahi chal raha.")
