from fastapi.testclient import TestClient
from app.main import app        # Import FastAPI instance from main.py

client = TestClient(app)

def test_add_energy_data():
    response = client.post("/api/v1/data/add", json = {
        "device_id": "test_device",
        "timestamp": "2025-02-06T10:00:00",
        "energy_consumed": 10.5,
        "location": "London"
    })

    assert response.status_code == 200          # Asserting success
    assert response.json() == {"message": "Energy data added successfully"}

def test_get_aggregated_data():
    response = client.get("/api/v1/data/aggregate?start_date=2025-02-06&end_date=2025-02-06")

    assert response.status_code == 200          # Asserting success
    assert "aggregated_data" in response.json()
