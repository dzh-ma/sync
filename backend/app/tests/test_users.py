import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.main import app
from app.db.database import users_collection

client = TestClient(app)

# Mock data
valid_user = {
    "email": "testuser@example.com",
    "password": "ValidPassword123"
}
duplicate_user = {
    "email": "testuser@example.com",
    "password": "ValidPassword123"
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
    """Clears the database before & after each test."""
    users_collection.delete_many({})
    yield
    users_collection.delete_many({})


def test_register_user_success():
    """Test successful registration of a new user."""
    response = client.post("/api/v1/users/register", json = valid_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == valid_user["email"]
    assert data["is_verified"] is False
    assert "id" in data
    assert "created_at" in data


def test_register_user_duplicate_email():
    """Test that registration fails for duplicate emails."""
    # Register 1st user
    client.post("/api/v1/users/register", json = valid_user)

    # Attempt to register again with the same email
    response = client.post("/api/v1/users/register", json = duplicate_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Registration failed. Please try again."


def test_register_user_invalid_email():
    """"Test that invalid email formats are rejected."""
    response = client.post("/api/v1/users/register", json = invalid_email_user)
    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.text


@patch("app.db.database.users_collection.insert_one", side_effect = Exception("Database Error"))
def test_register_user_db_failure(_):
    """Test graceful handling of database insertion failures."""
    response = client.post("/api/v1/users/register", json = valid_user)
    assert response.status_code == 500
    assert response.json()["detail"].startswith("Failed to register user.")


def test_register_user_response_format():
    """"Test the response format for successful completions."""
    response = client.post("/api/v1/users/register", json = valid_user)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["id"], str)
    assert isinstance(data["created_at"], str)
    assert datetime.fromisoformat(data["created_at"]) <= datetime.now(timezone.utc)
