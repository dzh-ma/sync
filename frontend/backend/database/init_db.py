# backend/database/init_db.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def init_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.project_test
    
    # Create unique index on email
    await db.users.create_index("email", unique=True)
    await db.users.create_index("otp_expires_at")
    print("Database initialized with indexes!")

if __name__ == "__main__":
    asyncio.run(init_db())
