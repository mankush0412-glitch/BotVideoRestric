"""
settings.py — /settings command + inline buttons only.
Input handling is in conversation.py via settings_state dict.
"""
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from devgagan import app
from devgagan.core.mongo.users_db import (
    get_rename, get_caption, get_thumbnail,
    del_rename, del_caption, del_thumbnail
)
from devgagan.modules.conversation import settings_state
from devgagan.core.safe import safe


def settings_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Set Rename",    callback_data="set_rename"),
         InlineKeyboardButton("🗑 Del Rename",    callback_data="del_rename")],
        [InlineKeyboardButton("📝 Set Caption",   callback_data="set_caption"),
         InlineKeyboardButton("🗑 Del Caption",   callback_data="del_caption")],
        [InlineKeyboardButton("🖼 Set Thumbnail", callback_data="set_thumb"),
         InlineKeyboardButton("🗑 Del Thumbnail", callback_data="del_thumb")],
        [InlineKeyboardButton("📊 My Settings",   callback_data="my_settings")],
    ])


@app.on_message(filters.command("settings") & filters.private)
@safe
async def settings_cmd(_, message):
    await message.reply("⚙️ **Settings**\nKya change karna hai?", reply_markup=settings_kb())


@app.on_callback_query(filters.regex("^my_settings$"))
@safe
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


@app.on_callback_query(filters.regex("^set_rename$"))
@safe
async def prompt_rename(client, cb):
    await cb.answer()
    settings_state[cb.from_user.id] = "rename"
    await cb.message.reply("✏️ Naya naam bhejo (extension mat likho):\nExample: `MyVideo`")


@app.on_callback_query(filters.regex("^set_caption$"))
@safe
async def prompt_caption(client, cb):
    await cb.answer()
    settings_state[cb.from_user.id] = "caption"
    await cb.message.reply(
        "📝 Custom caption bhejo.\n"
        "`{caption}` likho jahan original aana chahiye.\n"
        "Example: `📁 {caption} | @MyChannel`"
    )


@app.on_callback_query(filters.regex("^set_thumb$"))
@safe
async def prompt_thumb(client, cb):
    await cb.answer()
    settings_state[cb.from_user.id] = "thumbnail"
    await cb.message.reply("🖼 Ek photo bhejo jo thumbnail banega.")


@app.on_callback_query(filters.regex("^del_rename$"))
@safe
async def rm_rename(client, cb):
    await del_rename(cb.from_user.id)
    await cb.answer("Rename deleted!", show_alert=True)


@app.on_callback_query(filters.regex("^del_caption$"))
@safe
async def rm_caption(client, cb):
    await del_caption(cb.from_user.id)
    await cb.answer("Caption deleted!", show_alert=True)


@app.on_callback_query(filters.regex("^del_thumb$"))
@safe
async def rm_thumb(client, cb):
    await del_thumbnail(cb.from_user.id)
    await cb.answer("Thumbnail deleted!", show_alert=True)
