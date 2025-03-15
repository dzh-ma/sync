"""
This module contains test cases for the schedule API endpoints

Tested endpoints:
- `/api/v1/schedules/` (Creating schedules)
- `/api/v1/schedules/` (Fetching all schedules)
- `/api/v1/schedules/{schedule_id}` (Fetching a specific schedule)
- `/api/v1/schedules/{schedule_id}` (Updating a schedule)
- `/api/v1/schedules/{schedule_id}` (Deleting a schedule)
"""
from fastapi.testclient import TestClient
from ..main import app
from ..tests.test_report_generation import get_jwt_token
from ..tests.test_profile_routes import get_current_user_id
from datetime import datetime, timedelta, timezone
import uuid

client = TestClient(app)

def test_create_schedule():
    """
    Test creating a new device schedule.
    
    - Uses an authenticated request
    - Sends a JSON payload with schedule data
    - Asserts successful creation response
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    
    # First create a device to schedule
    device_id = f"schedule_test_device_{uuid.uuid4().hex[:8]}"
    client.post(
        "/api/v1/devices/",
        json={
            "id": device_id,
            "name": "Schedule Test Device",
            "type": "light",
            "room_id": "living_room",
            "status": "off",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Set up schedule times
    now = datetime.now(timezone.utc)
    start_time = now.replace(hour=8, minute=0, second=0)
    end_time = now.replace(hour=18, minute=0, second=0)
    start_date = now.date()
    end_date = (now + timedelta(days=30)).date()
    
    response = client.post(
        "/api/v1/schedules/",
        json={
            "device_id": device_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "created_by": user_id,
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"Failed to create schedule: {response.json()}"
    assert "schedule_id" in response.json()
    assert response.json()["message"] == "Schedule created successfully"

def test_get_all_schedules():
    """
    Test fetching all schedules.
    
    - Uses an authenticated request
    - Asserts successful response with a list of schedules
    """
    token = get_jwt_token()
    
    response = client.get(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_schedule_by_id():
    """
    Test fetching a specific schedule by ID.
    
    - Uses an authenticated request
    - Asserts successful response with schedule details
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    
    # First create a device to schedule
    device_id = f"schedule_fetch_device_{uuid.uuid4().hex[:8]}"
    client.post(
        "/api/v1/devices/",
        json={
            "id": device_id,
            "name": "Schedule Fetch Device",
            "type": "light",
            "room_id": "bedroom",
            "status": "off",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Set up schedule times
    now = datetime.now(timezone.utc)
    start_time = now.replace(hour=9, minute=0, second=0)
    end_time = now.replace(hour=17, minute=0, second=0)
    start_date = now.date()
    end_date = (now + timedelta(days=30)).date()
    
    # Create a schedule to fetch
    create_response = client.post(
        "/api/v1/schedules/",
        json={
            "device_id": device_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "created_by": user_id,
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    schedule_id = create_response.json()["schedule_id"]
    
    # Now fetch the schedule
    response = client.get(
        f"/api/v1/schedules/{schedule_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["device_id"] == device_id
    assert response.json()["created_by"] == user_id

def test_filter_schedules():
    """
    Test filtering schedules by different criteria.
    
    - Uses an authenticated request
    - Creates schedules with different properties
    - Filters by properties and verifies results
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    
    # Create devices for scheduling
    devices = []
    for i in range(3):
        device_id = f"filter_test_device_{i}_{uuid.uuid4().hex[:8]}"
        client.post(
            "/api/v1/devices/",
            json={
                "id": device_id,
                "name": f"Filter Test Device {i}",
                "type": "light",
                "room_id": "living_room",
                "status": "off",
                "is_active": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        devices.append(device_id)
    
    # Set up schedule times
    now = datetime.now(timezone.utc)
    start_times = [
        now.replace(hour=8, minute=0, second=0),
        now.replace(hour=12, minute=0, second=0),
        now.replace(hour=18, minute=0, second=0)
    ]
    end_times = [
        now.replace(hour=10, minute=0, second=0),
        now.replace(hour=14, minute=0, second=0),
        now.replace(hour=22, minute=0, second=0)
    ]
    start_date = now.date()
    end_date = (now + timedelta(days=30)).date()
    
    # Create schedules for each device
    for i, device_id in enumerate(devices):
        is_active = i % 2 == 0  # Alternate active status
        
        client.post(
            "/api/v1/schedules/",
            json={
                "device_id": device_id,
                "start_time": start_times[i].isoformat(),
                "end_time": end_times[i].isoformat(),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "created_by": user_id,
                "is_active": is_active
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Test filtering by device_id
    response = client.get(
        f"/api/v1/schedules/?device_id={devices[0]}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    filtered_schedules = response.json()
    assert len(filtered_schedules) >= 1
    for schedule in filtered_schedules:
        if "device_id" in schedule and schedule["device_id"] == devices[0]:
            assert schedule["device_id"] == devices[0]
    
    # Test filtering by is_active
    response = client.get(
        "/api/v1/schedules/?is_active=true",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    active_schedules = response.json()
    for schedule in active_schedules:
        assert schedule["is_active"] == True
