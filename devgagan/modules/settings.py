"""
settings.py — Custom rename, caption, thumbnail settings
"""
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from devgagan import app
from devgagan.core.mongo.users_db import (
    get_rename, set_rename, del_rename,
    get_caption, set_caption, del_caption,
    get_thumbnail, set_thumbnail, del_thumbnail
)


def settings_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Set Rename", callback_data="set_rename"),
         InlineKeyboardButton("🗑 Del Rename",  callback_data="del_rename")],
        [InlineKeyboardButton("📝 Set Caption", callback_data="set_caption"),
         InlineKeyboardButton("🗑 Del Caption", callback_data="del_caption")],
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="set_thumb"),
         InlineKeyboardButton("🗑 Del Thumbnail", callback_data="del_thumb")],
        [InlineKeyboardButton("📊 My Settings", callback_data="my_settings")],
    ])


@app.on_message(filters.command("settings") & filters.private)
async def settings_cmd(_, message):
    await message.reply("⚙️ **Settings**\nKya change karna hai?", reply_markup=settings_kb())


@app.on_callback_query(filters.regex("^my_settings$"))
async def my_settings(client, cb):
    uid = cb.from_user.id
    rename  = await get_rename(uid)  or "Not set"
    caption = await get_caption(uid) or "Not set"
    thumb   = await get_thumbnail(uid)
    await cb.answer()
    await cb.message.edit(
        f"📊 **Your Settings**\n\n"
        f"✏️ Rename: `{rename}`\n"
        f"📝 Caption: `{caption}`\n"
        f"🖼 Thumbnail: {'Set ✅' if thumb else 'Not set'}",
        reply_markup=settings_kb()
    )


# ── Rename ────────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex("^set_rename$"))
async def prompt_rename(client, cb):
    await cb.answer()
    await cb.message.reply("✏️ Naya naam bhejo (extension mat likho):\nExample: `MyVideo`")

    try:
        import asyncio
        resp = await client.ask(cb.from_user.id, "Waiting...", timeout=60)
        await set_rename(cb.from_user.id, resp.text.strip())
        await resp.reply("✅ Rename saved!")
    except asyncio.TimeoutError:
        pass


@app.on_callback_query(filters.regex("^del_rename$"))
async def rm_rename(client, cb):
    await del_rename(cb.from_user.id)
    await cb.answer("Rename deleted!", show_alert=True)


# ── Caption ───────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex("^set_caption$"))
async def prompt_caption(client, cb):
    await cb.answer()
    await cb.message.reply(
        "📝 Custom caption bhejo.\n"
        "`{caption}` likho jahan original caption aana chahiye.\n"
        "Example: `📁 {caption} | @MyChannel`"
    )
    try:
        import asyncio
        resp = await client.ask(cb.from_user.id, "Waiting...", timeout=60)
        await set_caption(cb.from_user.id, resp.text.strip())
        await resp.reply("✅ Caption saved!")
    except asyncio.TimeoutError:
        pass


@app.on_callback_query(filters.regex("^del_caption$"))
async def rm_caption(client, cb):
    await del_caption(cb.from_user.id)
    await cb.answer("Caption deleted!", show_alert=True)


# ── Thumbnail ─────────────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex("^set_thumb$"))
async def prompt_thumb(client, cb):
    await cb.answer()
    await cb.message.reply("🖼 Ek photo bhejo jo thumbnail banega.")
    try:
        import asyncio
        resp = await client.ask(cb.from_user.id, "Waiting...", timeout=60)
        if resp.photo:
            await set_thumbnail(cb.from_user.id, resp.photo.file_id)
            await resp.reply("✅ Thumbnail saved!")
        else:
            await resp.reply("❌ Photo bhejo, kuch aur nahi.")
    except asyncio.TimeoutError:
        pass


@app.on_callback_query(filters.regex("^del_thumb$"))
async def rm_thumb(client, cb):
    await del_thumbnail(cb.from_user.id)
    await cb.answer("Thumbnail deleted!", show_alert=True)
