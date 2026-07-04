"""
login.py — /login /logout /cancel commands only.
Actual conversation state handled in conversation.py
"""
from pyrogram import filters
from devgagan import app
from devgagan.core.mongo import db
from devgagan.core.safe import safe
from devgagan.modules.conversation import login_sessions


@app.on_message(filters.command("login") & filters.private)
@safe
async def login_start(client, message):
    uid = message.chat.id
    existing = await db.get_session(uid)
    if existing:
        return await message.reply(
            "✅ Tum pehle se login ho.\n/logout karke dobara login karo."
        )
    login_sessions[uid] = {"step": "phone"}
    await message.reply(
        "📱 **Login — Step 1/3**\n\n"
        "Apna phone number bhejo (country code ke saath):\n"
        "Example: `+919876543210`\n\n"
        "/cancel bhejo band karne ke liye."
    )


@app.on_message(filters.command("logout") & filters.private)
@safe
async def logout(client, message):
    uid = message.chat.id
    if not await db.get_session(uid):
        return await message.reply("Tum login hi nahi ho.")
    await db.del_session(uid)
    login_sessions.pop(uid, None)
    await message.reply("✅ Logout ho gaye!")


@app.on_message(filters.command("cancel") & filters.private)
@safe
async def cancel_cmd(client, message):
    uid = message.chat.id
    # Cancel login flow
    state = login_sessions.pop(uid, None)
    if state:
        temp = state.get("client")
        if temp:
            try: await temp.disconnect()
            except Exception: pass
        return await message.reply("❌ Login cancelled.")
    # Cancel extraction flow
    from devgagan.modules.main import users_loop
    if users_loop.get(uid, False):
        users_loop[uid] = False
        return await message.reply("🚫 Process cancel ho raha hai.")
    await message.reply("Koi active process nahi hai.")
