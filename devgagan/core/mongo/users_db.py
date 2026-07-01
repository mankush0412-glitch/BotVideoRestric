"""
users_db.py — User-specific helpers (settings: rename, caption, thumbnail)
"""
from devgagan.core.mongo.db import db


async def get_rename(user_id):
    data = await db.get_data(user_id)
    return data.get("rename") if data else None


async def set_rename(user_id, name):
    await db.update_data(user_id, {"rename": name})


async def del_rename(user_id):
    await db.delete_data(user_id, "rename")


async def get_caption(user_id):
    data = await db.get_data(user_id)
    return data.get("caption") if data else None


async def set_caption(user_id, cap):
    await db.update_data(user_id, {"caption": cap})


async def del_caption(user_id):
    await db.delete_data(user_id, "caption")


async def get_thumbnail(user_id):
    data = await db.get_data(user_id)
    return data.get("thumbnail") if data else None


async def set_thumbnail(user_id, file_id):
    await db.update_data(user_id, {"thumbnail": file_id})


async def del_thumbnail(user_id):
    await db.delete_data(user_id, "thumbnail")
