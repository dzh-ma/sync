"""
Pytest configuration file for the smart home system tests.
"""
import sys
import pytest
from unittest.mock import patch, MagicMock
import mongomock
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import dependency before applying overrides
from app.core.auth import get_current_user
from app.models.user import UserDB

@pytest.fixture(scope="session", autouse=True)
def mock_mongodb_connection():
    """
    Mock the MongoDB connection for all tests.
    This helps avoid connecting to a real database during tests.
    """
    # Create a patcher for MongoClient
    mongo_patcher = patch('pymongo.MongoClient', mongomock.MongoClient)
    mongo_patcher.start()
    
    # Mock init_db function to avoid creating real indexes
    db_patcher = patch('app.db.data.init_db', MagicMock())
    db_patcher.start()
    
    yield
    
    # Stop the patchers after tests complete
    mongo_patcher.stop()
    db_patcher.stop()

# Mock the auth dependency for tests
@pytest.fixture(autouse=True)
def mock_auth_dependency():
    """
    Mock the authentication dependency for all tests.
    """
    # Create a test user
    mock_user = UserDB(
        id="test-user-id",
        username="test-user",
        email="test@example.com",
        hashed_password="hashed_password",
        role="admin"
    )
    
    # Import the application
    from app.main import app
    
    # Set up the dependency override
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    yield
    
    # Clear dependency overrides after tests
    app.dependency_overrides = {}
