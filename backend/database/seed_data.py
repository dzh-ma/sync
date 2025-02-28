# backend/database/seed_data.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.project_test

    # Check if users already exist
    existing_users = await db.users.count_documents({})
    if existing_users > 0:
        print("Database already seeded. Skipping...")
        return

    users = [
        {"email": "quandale@dingle.com", "password": pwd_context.hash("123")},
        {"email": "bus@conductor.com", "password": pwd_context.hash("456")},
    ]

    await db.users.insert_many(users)
    print("Sample data inserted!")

if __name__ == "__main__":
    asyncio.run(seed_data())
