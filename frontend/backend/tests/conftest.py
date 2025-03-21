"""
This module defines pytest fixtures for setting up & cleaning up test data

Fixtures include:
- Seeding a test user before each test
- Seeding energy consumption data for specific test cases
- Cleaning up test energy data after each test
- Removing previously generated CSV & PDF reports before tests run
"""
import os
import pytest
from pymongo import MongoClient
from ..db.database import users_collection
from ..core.security import hash_password
from datetime import datetime, timezone

from ..routes.report_routes import REPORTS_DIR

# CHECK: If PDF documentation is displayed as intended
@pytest.fixture(scope="function", autouse=True)
def setup_test_user():
    """
    Fixture to seed a test user before every test

    Ensures a predefined admin test user exists in the database
    If the user doesn't exist, it's inserted before the test runs
    """
    print("Seeding test user...")
    test_user = {
        "email": "test_user@example.com",
        "password_hash": hash_password("TestPassword123!"),
        "is_verified": True,
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    if not users_collection.find_one({"email": "test_user@example.com"}):
        users_collection.insert_one(test_user)
        print("Test user inserted.")
    else:
        print("Test user already exists.")

def seed_energy_data():
    """
    Seed energy consumption data for testing

    Inserts energy data for devices within the date range 2025-02-01 to 2025-02-02
    This ensures consistent test data across test cases
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client.smart_home
    energy_collection = db["energy_data"]
    print("Seeding energy data...")
    energy_collection.insert_many([
        {
            "device_id": "test_device_1",
            "timestamp": datetime(2025, 2, 1, 12, 0, 0),
            "energy_consumed": 15.0,
            "location": "London"
        },
        {
            "device_id": "test_device_2",
            "timestamp": datetime(2025, 2, 2, 14, 30, 0),
            "energy_consumed": 20.0,
            "location": "London"
        }
    ])


@pytest.fixture(scope="function", autouse=True)
def cleanup_energy_data():
    """
    Fixture to clean up energy consumption data after each test

    Deletes all energy data records within the date range 2025-02-01 to 2025-02-02 to ensure test isolation
    """
    yield
    client = MongoClient("mongodb://localhost:27017/")
    db = client.smart_home
    energy_collection = db["energy_data"]
    energy_collection.delete_many({"timestamp": {"$gte": datetime(2025, 2, 1), "$lt": datetime(2025, 2, 3)}})

@pytest.fixture(autouse = True)
def cleanup_report():
    """
    Fixture to remove all previously generated CSV & PDF reports before running tests

    Ensures that no old report files interfere with test results
    """
    if os.path.exists(REPORTS_DIR):
        for file in os.listdir(REPORTS_DIR):
            if file.endswith(".csv") or file.endswith(".pdf"):
                os.remove(os.path.join(REPORTS_DIR, file))
