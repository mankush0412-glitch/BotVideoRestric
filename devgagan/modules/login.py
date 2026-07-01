"""
login.py — Userbot login/logout via Pyromod conversation
"""
import asyncio
from pyrogram import filters, Client
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid
)
from pyromod import listen   # noqa — patches Client for .ask()
from devgagan import app
from devgagan.core.mongo import db
from config import API_ID, API_HASH, OWNER_ID


@app.on_message(filters.command("login") & filters.private)
async def login(client, message):
    user_id = message.chat.id
    existing = await db.get_session(user_id)
    if existing:
        await message.reply(
            "✅ Tum pehle se login ho.\n"
            "/logout karke dobara login kar sakte ho."
        )
        return

    await message.reply(
        "📱 **Login — Step 1/3**\n\n"
        "Apna phone number bhejo (country code ke saath):\n"
        "Example: `+919876543210`\n\n"
        "Cancel karna ho to `/cancel` bhejo."
    )

    try:
        phone_msg = await client.ask(user_id, "Waiting...", timeout=60)
    except asyncio.TimeoutError:
        await message.reply("⏱ Timeout! Dobara /login bhejo.")
        return

    if phone_msg.text.strip() == "/cancel":
        await phone_msg.reply("Cancelled.")
        return

    phone = phone_msg.text.strip()

    # Temporary client to get OTP
    temp = Client(
        f"temp_{user_id}",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True
    )

    try:
        await temp.connect()
        sent = await temp.send_code(phone)
        phone_hash = sent.phone_code_hash
    except PhoneNumberInvalid:
        await phone_msg.reply("❌ Phone number invalid hai.")
        await temp.disconnect()
        return
    except Exception as e:
        await phone_msg.reply(f"❌ Error: `{e}`")
        await temp.disconnect()
        return

    await phone_msg.reply(
        "📲 **Step 2/3 — OTP**\n\n"
        "Telegram mein OTP aaya hoga.\n"
        "Space se alag karke bhejo:\n"
        "Example: `1 2 3 4 5`"
    )

    try:
        otp_msg = await client.ask(user_id, "Waiting for OTP...", timeout=120)
    except asyncio.TimeoutError:
        await temp.disconnect()
        await message.reply("⏱ Timeout! Dobara /login bhejo.")
        return

    otp = otp_msg.text.strip().replace(" ", "")

    try:
        await temp.sign_in(phone, phone_hash, otp)
    except SessionPasswordNeeded:
        await otp_msg.reply(
            "🔒 **Step 3/3 — 2FA Password**\n\n"
            "Apna Telegram 2FA password bhejo:"
        )
        try:
            pw_msg = await client.ask(user_id, "Waiting for password...", timeout=120)
        except asyncio.TimeoutError:
            await temp.disconnect()
            await message.reply("⏱ Timeout!")
            return
        try:
            await temp.check_password(pw_msg.text.strip())
        except PasswordHashInvalid:
            await pw_msg.reply("❌ Password galat hai!")
            await temp.disconnect()
            return
        except Exception as e:
            await pw_msg.reply(f"❌ Error: `{e}`")
            await temp.disconnect()
            return
    except PhoneCodeInvalid:
        await otp_msg.reply("❌ OTP galat hai!")
        await temp.disconnect()
        return
    except PhoneCodeExpired:
        await otp_msg.reply("❌ OTP expire ho gaya, dobara /login karo.")
        await temp.disconnect()
        return
    except Exception as e:
        await otp_msg.reply(f"❌ Error: `{e}`")
        await temp.disconnect()
        return

    session_string = await temp.export_session_string()
    await temp.disconnect()

    await db.set_session(user_id, session_string)
    await message.reply(
        "✅ **Login successful!**\n\n"
        "Ab `/getbot @botname` use karo."
    )


@app.on_message(filters.command("logout") & filters.private)
async def logout(client, message):
    user_id = message.chat.id
    session = await db.get_session(user_id)
    if not session:
        await message.reply("Tum login hi nahi ho.")
        return
    await db.del_session(user_id)
    await message.reply("✅ Logout ho gaye!")
