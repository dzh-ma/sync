import sys
import os

# Ensure 'app/' is in the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pymongo import MongoClient
from app.core.security import hash_password
from datetime import datetime, timezone

client = MongoClient("mongodb://localhost:27017")
db = client.smart_home
users_collection = db["users"]

test_user = {
    "email": "test_user@example.com",
    "password_hash": hash_password("TestPassword123!"),
    "is_verified": True,
    "role": "admin",
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc),
}

existing_user = users_collection.find_one({"email": test_user["email"]})

if not existing_user:
    users_collection.insert_one(test_user)
    print("✅ Admin user seeded successfully!")
else:
    print("ℹ️ Admin user already exists.")
