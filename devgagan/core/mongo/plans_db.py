"""
plans_db.py — Premium plan management helpers
"""
from devgagan.core.mongo.db import db


async def add_premium(user_id: int):
    await db.set_plan(user_id, 1)


async def remove_premium(user_id: int):
    await db.set_plan(user_id, 0)


async def is_premium(user_id: int) -> bool:
    plan = await db.get_plan(user_id)
    return plan == 1


async def all_premium_users():
    users = []
    async for doc in db.users.find({"plan": 1}, {"_id": 1}):
        users.append(doc["_id"])
    return users
