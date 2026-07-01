"""
db.py — MongoDB connection + generic user data CRUD via Motor (async)
"""
import motor.motor_asyncio
from config import MONGO_DB


class Database:
    def __init__(self, uri: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client["BotExtractor"]
        self.users = self.db["users"]

    # ── CRUD ──────────────────────────────────────────────────────────────────
    async def add_user(self, user_id: int):
        if not await self.users.find_one({"_id": user_id}):
            await self.users.insert_one({"_id": user_id, "plan": 0})

    async def get_data(self, user_id: int):
        return await self.users.find_one({"_id": user_id})

    async def update_data(self, user_id: int, data: dict):
        await self.users.update_one({"_id": user_id}, {"$set": data}, upsert=True)

    async def delete_data(self, user_id: int, key: str):
        await self.users.update_one({"_id": user_id}, {"$unset": {key: ""}})

    async def all_users(self):
        return [doc["_id"] async for doc in self.users.find({}, {"_id": 1})]

    async def total_users(self):
        return await self.users.count_documents({})

    # ── Session ───────────────────────────────────────────────────────────────
    async def set_session(self, user_id: int, session: str):
        await self.update_data(user_id, {"session": session})

    async def get_session(self, user_id: int):
        data = await self.get_data(user_id)
        return data.get("session") if data else None

    async def del_session(self, user_id: int):
        await self.delete_data(user_id, "session")

    # ── Plan ──────────────────────────────────────────────────────────────────
    async def set_plan(self, user_id: int, plan: int):
        await self.update_data(user_id, {"plan": plan})

    async def get_plan(self, user_id: int):
        data = await self.get_data(user_id)
        return data.get("plan", 0) if data else 0


db = Database(MONGO_DB)
