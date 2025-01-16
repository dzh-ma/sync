import os
from pymongo import MongoClient

# Loading MongoDB URI from envvars
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Initialize MongoDB client
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client.smart_home
    users_collection = db["users"]
except Exception as e:
    raise ConnectionError(f"Failed to connect to MongoDB: {e}") from e

async def init_db():
    """Initialize the database, such as creating necessary indexes."""
    try:
        users_collection.create_index("email", unique = True)
        print("Database initialized successfully.")
    except Exception as e:
        raise RuntimeError(f"Error during database initialization: {e}") from e
