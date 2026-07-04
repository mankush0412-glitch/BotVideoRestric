import logging
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from devgagan import app
from config import OWNER_ID
from devgagan.core.func import subscribe
from devgagan.core.safe import safe

logger = logging.getLogger("BotExtractor.debug")


@app.on_message(filters.command("set"))
@safe
async def set_commands(_, message):
    if message.from_user.id not in OWNER_ID:
        return await message.reply("Not authorized.")
    await app.set_bot_commands([
        BotCommand("start",   "🚀 Start the bot"),
        BotCommand("login",   "🔑 Apna account login karo"),
        BotCommand("logout",  "🚪 Logout"),
        BotCommand("getbot",  "🔓 Kisi bot se saare files nikalo"),
        BotCommand("cancel",  "🚫 Process band karo"),
        BotCommand("settings","⚙️ Settings"),
        BotCommand("stats",   "📊 Stats (Admin)"),
        BotCommand("help",    "❓ Help"),
    ])
    await message.reply("✅ Commands set!")


@app.on_message(filters.command("start") & filters.private)
@safe
async def start(client, message):
    logger.info(f"🎯 start() handler TRIGGERED for {message.chat.id}")
    joined = await subscribe(client, message)
    if joined == 1:
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 Kaise Use Karein?", callback_data="help_extract")],
        [InlineKeyboardButton("🔑 Login Guide",  callback_data="help_login"),
         InlineKeyboardButton("❓ Help",         callback_data="help_main")],
    ])
    await message.reply(
        "**🔓 Bot Extractor**\n\n"
        "Kisi bhi restricted/protected Telegram bot ka content nikaalo —\n"
        "videos, PDFs, files — seedha bina kisi link ya ID ke.\n\n"
        "**Bas itna karo:**\n"
        "1️⃣ `/login` — Apna account link karo\n"
        "2️⃣ Target bot ko apne Telegram se `/start` bhejo\n"
        "3️⃣ `/getbot @botname` — Saara content aa jaayega ✅",
        reply_markup=keyboard
    )


@app.on_message(filters.command("help") & filters.private)
@safe
async def help_cmd(client, message):
    joined = await subscribe(client, message)
    if joined == 1:
        return
    await message.reply(
        "**❓ Help**\n\n"
        "`/login` — Account login karo\n"
        "`/logout` — Logout karo\n"
        "`/getbot @botname` — Us bot ke saare files nikalo\n"
        "`/getbot @botname 50` — Last 50 messages se files nikalo\n"
        "`/cancel` — Chal raha process rok do\n"
        "`/settings` — Rename, caption, thumbnail settings\n\n"
        "**Example:**\n"
        "`/getbot @SomeRestrictedBot`"
    )


@app.on_callback_query(filters.regex("^help_main$"))
async def help_main(client, cb):
    await cb.answer()
    await cb.message.reply(
        "**❓ Commands**\n\n"
        "`/login` — Account login karo\n"
        "`/logout` — Logout karo\n"
        "`/getbot @botname` — Saare files nikalo\n"
        "`/getbot @botname 50` — Last 50 messages\n"
        "`/cancel` — Process band karo\n"
        "`/settings` — Settings\n\n"
        "**Example:**\n"
        "`/getbot @SomeRestrictedBot`"
    )


@app.on_callback_query(filters.regex("^help_extract$"))
async def help_extract(client, cb):
    await cb.answer()
    await cb.message.reply(
        "**🔓 Kaise Use Karein**\n\n"
        "**Step 1:** Apne Telegram account se target bot ko `/start` bhejo\n"
        "_(jis bot ka content chahiye usse manually open karo aur start karo)_\n\n"
        "**Step 2:** Apna account is bot se link karo\n"
        "`/login` → phone number → OTP\n\n"
        "**Step 3:** Extract karo\n"
        "`/getbot @TargetBot`\n\n"
        "Bot **khud us bot ki poori history scan karega** —\n"
        "koi message ID nahi chahiye, koi link nahi chahiye.\n\n"
        "**Kyun kaam karta hai?**\n"
        "`protect_content=True` sirf Forward button disable karta hai.\n"
        "Userbot API se `get_chat_history()` call karta hai aur\n"
        "seedha Telegram server se file download karta hai. 🔓"
    )


@app.on_callback_query(filters.regex("^help_login$"))
async def help_login(client, cb):
    await cb.answer()
    await cb.message.reply(
        "**🔑 Login Guide**\n\n"
        "1. `/login` bhejo\n"
        "2. Phone number bhejo (e.g. `+919876543210`)\n"
        "3. Telegram mein OTP aayega → space se alag karke bhejo\n"
        "   Example: `1 2 3 4 5`\n"
        "4. 2FA enabled hai toh password bhi maangega\n\n"
        "Login ke baad `/getbot @botname` use karo."
    )
