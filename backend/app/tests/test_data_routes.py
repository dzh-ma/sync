"""
This module contains test cases for the energy data API endpoints

Tested endpoints:
- `/api/v1/data/add` (Adding energy data)
- `/api/v1/data/aggregate` (Fetching aggregated energy data)
- Aggregation with different intervals (hourly, daily, weekly)
"""
from fastapi.testclient import TestClient
from app.main import app
from app.tests.test_report_generation import get_jwt_token        # Import FastAPI instance from main.py

client = TestClient(app)

def test_add_energy_data():
    """
    Test adding new energy consumption data.

    - Uses an authenticated request
    - Sends a JSON payload with device energy data
    - Asserts successful insertion response
    """
    token = get_jwt_token()
    response = client.post(
        "/api/v1/data/add",
        json = {
            "device_id": "test_device",
            "timestamp": "2025-02-06T10:00:00",
            "energy_consumed": 10.5,
            "location": "London"
        },
        headers = {"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, f"Failed to add energy  data {response.json()}"          # Asserting success
    assert response.json() == {"message": "Energy data added successfully"}

def test_get_aggregated_data():
    """
    Test fetching aggregated energy data

    - Requests aggregated data without specifying an interval
    - Asserts successful response & presence of `aggregated_data` field
    """
    response = client.get("/api/v1/data/aggregate?start_date=2025-02-06&end_date=2025-02-06")

    assert response.status_code == 200          # Asserting success
    assert "aggregated_data" in response.json()

def test_get_aggregated_data_hourly():
    """
    Test hourly aggregation of energy data

    - Requests energy data aggregation using `interval=hour`
    - Asserts the response contains valid aggregated data
    """
    response = client.get("/api/v1/data/aggregate?start_date=2025-02-06&end_date=2025-02-06&interval=hour")
    assert response.status_code == 200
    data = response.json()
    assert "aggregated_data" in data
    assert isinstance(data["aggregated_data"], list)

def test_get_aggregated_data_daily():
    """
    Test daily aggregation of energy data

    - Requests energy data aggregation using `interval=day`
    - Asserts the response contains aggregated data
    """
    response = client.get("/api/v1/data/aggregate?start_date=2025-02-01&end_date=2025-02-07&interval=day")
    assert response.status_code == 200
    data = response.json()
    assert "aggregated_data" in data

def test_get_aggregated_data_weekly():
    """
    Test weekly aggregation of energy data

    - Requests energy data aggregation using `interval=week`
    - Asserts the response contains aggregated data
    """
    response = client.get("/api/v1/data/aggregate?start_date=2025-02-01&end_date=2025-02-07&interval=week")
    assert response.status_code == 200
    data = response.json()
    assert "aggregated_data" in data
