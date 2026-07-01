"""
get_func.py — Media upload helpers, filename/caption utilities
"""
import os
import time
from pyrogram.errors import FloodWait
from devgagan import app
from devgagan.core.func import progress_bar
from devgagan.core.mongo import db
from config import LOG_GROUP

# Per-user output chat mapping: {user_id: chat_id} or {user_id: "chat_id/topic_id"}
user_chat_ids = {}


async def get_final_caption(msg, user_id):
    """Build final caption using user's custom template or fall back to original."""
    data = await db.get_data(user_id)
    custom = data.get("caption") if data else None
    original = msg.caption or msg.text or ""

    if custom:
        return custom.replace("{caption}", original)
    return original


async def get_media_filename(msg):
    """Extract or generate a filename for the media."""
    if msg.document and msg.document.file_name:
        return msg.document.file_name
    if msg.video:
        return f"video_{msg.id}.mp4"
    if msg.audio:
        name = msg.audio.file_name or f"audio_{msg.id}.mp3"
        return name
    if msg.photo:
        return f"photo_{msg.id}.jpg"
    if msg.voice:
        return f"voice_{msg.id}.ogg"
    if msg.video_note:
        return f"vnote_{msg.id}.mp4"
    return f"file_{msg.id}"


async def get_message_file_size(msg):
    """Return file size in bytes or None."""
    for attr in ("document", "video", "audio", "photo", "voice", "video_note"):
        obj = getattr(msg, attr, None)
        if obj:
            return getattr(obj, "file_size", None)
    return None


async def rename_file(file_path, user_id):
    """Rename file if user has a custom rename template set."""
    data = await db.get_data(user_id)
    rename = data.get("rename") if data else None
    if not rename:
        return file_path
    ext = os.path.splitext(file_path)[1]
    new_path = os.path.join(os.path.dirname(file_path), rename + ext)
    try:
        os.rename(file_path, new_path)
        return new_path
    except Exception:
        return file_path


async def upload_media(user_id, target_chat_id, file_path, caption, edit_msg, topic_id=None):
    """
    Upload a file (video/document) to target_chat_id with a progress bar.
    Handles FloodWait automatically.
    """
    start = time.time()
    ext = os.path.splitext(file_path)[1].lower()

    async def prog(current, total):
        await progress_bar(
            current, total,
            "╭─────────────────────╮\n│      **__Uploading...__**\n├─────────────────────",
            edit_msg,
            start
        )

    try:
        # Video extensions
        if ext in (".mp4", ".mkv", ".avi", ".mov", ".webm"):
            result = await app.send_video(
                target_chat_id,
                file_path,
                caption=caption,
                supports_streaming=True,
                progress=prog,
                reply_to_message_id=topic_id
            )
        else:
            result = await app.send_document(
                target_chat_id,
                file_path,
                caption=caption,
                progress=prog,
                reply_to_message_id=topic_id
            )

        if LOG_GROUP:
            try:
                await result.copy(LOG_GROUP)
            except Exception:
                pass

        await edit_msg.delete()

    except FloodWait as fw:
        import asyncio
        await asyncio.sleep(fw.value + 5)
        await upload_media(user_id, target_chat_id, file_path, caption, edit_msg, topic_id)
    except Exception as e:
        try:
            await edit_msg.edit(f"❌ Upload failed: `{e}`")
        except Exception:
            pass
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
