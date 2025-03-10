"""
This module handles MongoDB database connections & operations

It provides:
- Initialization of MongoDB collections & indexes
- Functions to fetch energy consumption data with optional filtering
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient

# Setup logging
logger = logging.getLogger(__name__)

# Loading MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Initialize MongoDB client
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client.smart_home

    # Collections for different functions
    users_collection = db["users"]
    energy_collection = db["energy_data"]
    devices_collection = db["devices"]
    profiles_collection = db["profiles"]
    rooms_collection = db["rooms"]
    schedules_collection = db["schedules"]
    summary_collection = db["energy_summaries"]

    print(f"Connected to MongoDB database: {MONGO_URI}")
except Exception as e:
    raise ConnectionError(f"Failed to connect to MongoDB: {e}") from e

async def init_db():
    """
    Initialize the database by creating necessary indexes

    This function ensures:
    - Unique email constraint for users
    - Indexes on `device_id` & `timestamp` in the energy collection for optimized queries

    Raises:
        RuntimeError: If there is an error during database initialization
    """
    try:
        # User collection indexes
        users_collection.create_index("email", unique = True)

        # Energy data collection indexes
        energy_collection.create_index("device_id")
        energy_collection.create_index("timestamp")
        energy_collection.create_index([("device_id", 1), ("timestamp", 1)])
        energy_collection.create_index("location")

        # Device collection indexes
        devices_collection.create_index("id", unique=True)
        devices_collection.create_index("room_id")
        devices_collection.create_index("type")

        # Profile collection indexes
        profiles_collection.create_index("user_id")
        profiles_collection.create_index([("user_id", 1), ("name", 1)], unique=True)

        # Room collection indexes
        rooms_collection.create_index("id", unique=True)
        rooms_collection.create_index("created_by")

        # Schedule collection indexes
        schedules_collection.create_index("device_id")
        schedules_collection.create_index("created_by")
        schedules_collection.create_index("start_date")
        schedules_collection.create_index("end_date")

        # Energy summary collection indexes
        summary_collection.create_index("user_id")
        summary_collection.create_index([("user_id", 1), ("period", 1), ("start_date", 1)], unique=True)

        logger.info("Database initialized successfully with all collections and indexes.")

        print("Database initialized successfully.")
    except Exception as e:
        raise RuntimeError(f"Error during database initialization: {e}") from e

def get_energy_data(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """
    Fetch energy data consumption from MongoDB with optional date filtering

    Args:
        start_date (str, optional): Start date in `YYYY-MM-DD` format
        end_date (str, optional): End date in `YYYY-MM-DD` format

    Returns:
        List[Dict]: A list of energy consumption records

    Raises:
        ValueError: If the provided date format is incorrect
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
