"""
conversation.py — Single catch-all handler for all state-based conversations.
Handles: login flow (phone→otp→2fa) + settings input (rename/caption/thumbnail).
No pyromod needed.
"""
from pyrogram import filters
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid
)
from pyrogram import Client as PyroClient
from devgagan import app
from devgagan.core.mongo import db
from devgagan.core.mongo.users_db import set_rename, set_caption, set_thumbnail
from devgagan.core.safe import safe
from config import API_ID, API_HASH

# Shared state dicts (imported by login.py and settings.py too)
login_sessions = {}    # {user_id: {"step":..., "phone":..., "hash":..., "client":...}}
settings_state = {}    # {user_id: "rename"|"caption"|"thumbnail"}


@app.on_message(filters.private & ~filters.command([
    "start", "login", "logout", "getbot", "cancel",
    "settings", "stats", "add", "rem", "myplan",
    "gcast", "eval", "exec", "set", "help"
]))
@safe
async def conversation_handler(client, message):
    uid = message.chat.id
    text = (message.text or "").strip()

    # ── LOGIN FLOW ────────────────────────────────────────────────────────────
    login_state = login_sessions.get(uid)
    if login_state:
        step = login_state["step"]

        if step == "phone":
            temp = PyroClient(
                f"temp_{uid}", api_id=API_ID, api_hash=API_HASH, in_memory=True
            )
            try:
                await temp.connect()
                sent = await temp.send_code(text)
                login_sessions[uid] = {
                    "step": "otp",
                    "phone": text,
                    "hash": sent.phone_code_hash,
                    "client": temp,
                }
                await message.reply(
                    "📲 **Step 2/3 — OTP**\n\n"
                    "Telegram mein OTP aaya hoga.\n"
                    "Space se alag karke bhejo:\n"
                    "Example: `1 2 3 4 5`"
                )
            except PhoneNumberInvalid:
                login_sessions.pop(uid, None)
                await temp.disconnect()
                await message.reply("❌ Phone number invalid. /login dobara karo.")
            except Exception as e:
                login_sessions.pop(uid, None)
                try: await temp.disconnect()
                except Exception: pass
                await message.reply(f"❌ Error: `{e}`\n/login dobara karo.")
            return

        elif step == "otp":
            otp = text.replace(" ", "")
            temp = login_state["client"]
            try:
                await temp.sign_in(login_state["phone"], login_state["hash"], otp)
                session = await temp.export_session_string()
                await temp.disconnect()
                await db.set_session(uid, session)
                login_sessions.pop(uid, None)
                await message.reply("✅ **Login successful!**\n\nAb `/getbot @botname` use karo.")
            except SessionPasswordNeeded:
                login_sessions[uid]["step"] = "2fa"
                await message.reply(
                    "🔒 **Step 3/3 — 2FA Password**\n\nApna Telegram 2FA password bhejo:"
                )
            except PhoneCodeInvalid:
                await message.reply("❌ OTP galat! Dobara bhejo.")
            except PhoneCodeExpired:
                login_sessions.pop(uid, None)
                try: await temp.disconnect()
                except Exception: pass
                await message.reply("❌ OTP expire. /login dobara karo.")
            except Exception as e:
                login_sessions.pop(uid, None)
                try: await temp.disconnect()
                except Exception: pass
                await message.reply(f"❌ Error: `{e}`\n/login dobara karo.")
            return

        elif step == "2fa":
            temp = login_state["client"]
            try:
                await temp.check_password(text)
                session = await temp.export_session_string()
                await temp.disconnect()
                await db.set_session(uid, session)
                login_sessions.pop(uid, None)
                await message.reply("✅ **Login successful!**\n\nAb `/getbot @botname` use karo.")
            except PasswordHashInvalid:
                await message.reply("❌ Password galat! Dobara bhejo.")
            except Exception as e:
                login_sessions.pop(uid, None)
                try: await temp.disconnect()
                except Exception: pass
                await message.reply(f"❌ Error: `{e}`\n/login dobara karo.")
            return

    # ── SETTINGS INPUT ────────────────────────────────────────────────────────
    sstate = settings_state.pop(uid, None)
    if sstate:
        if sstate == "rename":
            if message.text:
                await set_rename(uid, message.text.strip())
                await message.reply("✅ Rename saved!")
            else:
                await message.reply("❌ Text bhejo.")
        elif sstate == "caption":
            if message.text:
                await set_caption(uid, message.text.strip())
                await message.reply("✅ Caption saved!")
            else:
                await message.reply("❌ Text bhejo.")
        elif sstate == "thumbnail":
            if message.photo:
                await set_thumbnail(uid, message.photo.file_id)
                await message.reply("✅ Thumbnail saved!")
            else:
                await message.reply("❌ Photo bhejo.")
