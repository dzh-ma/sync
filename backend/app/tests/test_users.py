"""
This module contains test cases for user registration

Tested functionality:
- Successful user registration
- Handling duplicate email registration
- Validation of invalid email formats
- Graceful handling of database failures
- Correct response format for successful registrations
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.main import app
from app.db.database import users_collection

client = TestClient(app)

# Mock user data for testing
valid_user = {
    "email": "testuser@example.com",
    "password": "ValidPassword123!"
}
duplicate_user = {
    "email": "testuser@example.com",
    "password": "ValidPassword123!"
}
invalid_email_user = {
    "email": "not-an-email",
    "password": "ValidPassword123"
}
invalid_password_user = {
    "email": "newuser@example.com",
    "password": "short"
}

@pytest.fixture(autouse = True)
def clear_db():
    """
    Fixture to clear the user collection before & after each test

    Ensures that each test starts with a clean database state
    """
    users_collection.delete_many({})
    yield
    users_collection.delete_many({})


def test_register_user_success():
    """
    Test successful registration of a new user

    - Sends a valid user registration request
    - Asserts response status & returned user data
    """
    response = client.post("/api/v1/users/register", json = valid_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == valid_user["email"]
    assert data["is_verified"] is False
    assert "id" in data
    assert "created_at" in data


def test_register_user_duplicate_email():
    """
    Test that registration fails when using a duplicate email

    - Registers a user
    - Attempts to register another user with the same email
    - Asserts that the request fails with status 400
    """
    # Register 1st user
    client.post("/api/v1/users/register", json = valid_user)

    # Attempt to register again with the same email
    response = client.post("/api/v1/users/register", json = duplicate_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Registration failed, please try again."


def test_register_user_invalid_email():
    """"
    Test that invalid email formats are rejected

    - Sends a registration request with an invalid email
    - Asserts that the response returns a 422 validation error
    """
    response = client.post("/api/v1/users/register", json = invalid_email_user)
    assert response.status_code == 422
    assert "value is not a valid email address" in response.text


@patch("app.db.database.users_collection.insert_one", side_effect = Exception("Database Error"))
def test_register_user_db_failure(_):
    """
    Test graceful handling of database insertion failures

    - Mocks a database insertion failure
    - Asserts that the response returns a 500 error with a relevant message
    """
    response = client.post("/api/v1/users/register", json = valid_user)
    assert response.status_code == 500
    assert response.json()["detail"].startswith("Failed to register user: Database Error")


def test_register_user_response_format():
    """
    test the response format for a successful registration

    - Sends a valid registration request
    - Asserts that the response contains correctly formatted fields
    """
    response = client.post("/api/v1/users/register", json = valid_user)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["id"], str)
    assert isinstance(data["created_at"], str)
    assert datetime.fromisoformat(data["created_at"]) <= datetime.now(timezone.utc)
