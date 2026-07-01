"""
eval.py — Admin eval/exec for debugging (owner only)
"""
import asyncio
import traceback
from pyrogram import filters
from devgagan import app
from config import OWNER_ID


@app.on_message(filters.command("eval") & filters.private)
async def eval_cmd(_, message):
    if message.from_user.id not in OWNER_ID:
        return
    code = message.text.split(None, 1)
    if len(code) < 2:
        return await message.reply("Usage: `/eval <code>`")
    code = code[1]
    try:
        result = eval(code)
        if asyncio.iscoroutine(result):
            result = await result
        await message.reply(f"**Result:**\n`{result}`")
    except Exception:
        await message.reply(f"**Error:**\n`{traceback.format_exc()}`")


@app.on_message(filters.command("exec") & filters.private)
async def exec_cmd(_, message):
    if message.from_user.id not in OWNER_ID:
        return
    code = message.text.split(None, 1)
    if len(code) < 2:
        return await message.reply("Usage: `/exec <code>`")
    code = code[1]
    try:
        exec_globals = {"app": app, "message": message, "asyncio": asyncio}
        exec(f"async def _f():\n" + "\n".join(f"    {l}" for l in code.split("\n")), exec_globals)
        await exec_globals["_f"]()
    except Exception:
        await message.reply(f"**Error:**\n`{traceback.format_exc()}`")
