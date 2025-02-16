import os
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict

# Loading MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Initialize MongoDB client
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client.smart_home

    # Collections for different functions
    users_collection = db["users"]
    energy_collection = db["energy_data"]

    print(f"Connected to MongoDB database: {MONGO_URI}")
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

def get_energy_data(start_date: str = None, end_date: str = None) -> List[Dict]:
    """
    Fetch energy consumption data from MongoDB with optional date filtering.

    :param start_date: Optional start date in 'YYYY-MM-DD' format
    :param end_date: Optional end date in 'YYYY-MM-DD' format
    :return: List of energy data documents
    """

    query = {}

    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query["timestamp"] = {"$gte": start_dt, "$lte": end_dt}
        except ValueError as exc:
            raise ValueError("Invalid date format. Use `YYYY-MM-DD`.") from exc

    energy_data = list(energy_collection.find(query, {"_id": 0}))   # Exclude MongoDB _id field

    return energy_data
