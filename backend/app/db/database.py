import os
from pymongo import MongoClient

# Loading MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Initialize MongoDB client
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client.smart_home

    # Collections for different functions
    users_collection = db["users"]
    energy_collection = db["energy_data"]
except Exception as e:
    raise ConnectionError(f"Failed to connect to MongoDB: {e}") from e

async def init_db():
    """Initialize the database, such as creating necessary indexes."""
    try:
        # Create uniqueness of user emails
        users_collection.create_index("email", unique = True)

        # Optimize queries by creating indexes on frequently queried fields
        energy_collection.create_index("device_id")
        energy_collection.create_index("timestamp")

        print("Database initialized successfully.")
    except Exception as e:
        raise RuntimeError(f"Error during database initialization: {e}") from e
