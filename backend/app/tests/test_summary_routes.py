"""
This module contains test cases for the energy summary API endpoints

Tested endpoints:
- `/api/v1/summaries/generate` (Generating energy summaries)
- `/api/v1/summaries/` (Fetching all summaries)
- `/api/v1/summaries/{summary_id}` (Fetching a specific summary)
- `/api/v1/summaries/{summary_id}` (Deleting a summary)
"""
from fastapi.testclient import TestClient
from app.main import app
from app.tests.test_report_generation import get_jwt_token
from app.tests.test_profile_routes import get_current_user_id
from datetime import datetime, timedelta
import time

client = TestClient(app)

def test_generate_energy_summary():
    """
    Test generating an energy consumption summary.
    
    - Uses an authenticated request
    - Sends summary generation parameters
    - Asserts successful generation response
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    
    # Generate a unique timestamp to avoid duplicate key errors
    import time
    unique_suffix = int(time.time() * 1000)
    
    # Add some energy data first to ensure we have data to summarize
    current_time = datetime.now()
    yesterday = current_time - timedelta(days=1)
    
    # Use unique device ID to prevent interference between test runs
    device_id = f"test_device_summary_{unique_suffix}"
    
    # Format for API input
    current_date_iso = current_time.strftime("%Y-%m-%dT%H:%M:%S")
    yesterday_iso = yesterday.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Format dates for API parameters
    date_param_format = "%Y-%m-%d"
    yesterday_date = yesterday.strftime(date_param_format)
    
    # Add energy consumption data
    response = client.post(
        "/api/v1/data/add",
        json = {
            "device_id": device_id,
            "timestamp": yesterday_iso,
            "energy_consumed": 15.5,
            "location": "Test Location",
            "user_id": user_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"Failed to add energy data: {response.json()}"

    # Wait for data to be processed
    time.sleep(1)
    
    # Generate unique summary with period + timestamp
    unique_period = f"daily_{unique_suffix}"
    
    # Generate summary
    response = client.post(
        f"/api/v1/summaries/generate?user_id={user_id}&period={unique_period}&start_date={yesterday_date}",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"Generate Summary Response: {response.json()}")
    
    assert response.status_code == 200, f"Failed to generate summary: {response.json()}"
    
    # Store the summary ID for other tests
    if "summary_id" in response.json():
        summary_id = response.json()["summary_id"]
        import builtins
        setattr(builtins, "last_created_summary_id", summary_id)
    
    # Verify response structure
    assert "message" in response.json()
    if "summary" in response.json():
        summary = response.json()["summary"]
        # Check basic fields if available
        if isinstance(summary, dict):
            assert summary.get("user_id") == user_id

def test_get_all_summaries():
    """
    Test fetching all energy summaries.
    
    - Uses an authenticated request
    - Asserts successful response with list of summaries
    """
    token = get_jwt_token()
    
    response = client.get(
        "/api/v1/summaries/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_summary_by_id():
    """
    Test fetching a specific energy summary by ID.
    
    - Uses an authenticated request
    - Asserts successful response with summary details
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    
    # First generate a summary to fetch
    generate_response = client.post(
        f"/api/v1/summaries/generate?user_id={user_id}&period=weekly",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    summary_id = generate_response.json()["summary_id"]
    
    # Now fetch the summary
    response = client.get(
        f"/api/v1/summaries/{summary_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["user_id"] == user_id
    assert response.json()["period"] == "weekly"

def test_delete_summary():
    """
    Test deleting an energy summary.
    
    - Uses an admin authenticated request
    - Asserts successful deletion response
    - Verifies the summary is no longer accessible
    """
    token = get_jwt_token()  # Assuming this returns an admin token
    user_id = get_current_user_id(token)
    
    # First generate a summary to delete
    generate_response = client.post(
        f"/api/v1/summaries/generate?user_id={user_id}&period=monthly",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    summary_id = generate_response.json()["summary_id"]
    
    # Now delete the summary
    response = client.delete(
        f"/api/v1/summaries/{summary_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Energy summary deleted successfully"
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/summaries/{summary_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == 404

def test_filter_summaries():
    """
    Test filtering energy summaries by different criteria.
    
    - Uses an authenticated request
    - Creates summaries with different properties
    - Filters by properties and verifies results
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    
    # Generate summaries for different periods
    periods = ["daily", "weekly", "monthly"]
    for period in periods:
        client.post(
            f"/api/v1/summaries/generate?user_id={user_id}&period={period}",
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Filter by period
    response = client.get(
        f"/api/v1/summaries/?period=weekly",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    summaries = response.json()
    weekly_summaries = [s for s in summaries if s["period"] == "weekly"]
    assert len(weekly_summaries) >= 1
    for summary in weekly_summaries:
        assert summary["period"] == "weekly"
    
    # Filter by user
    response = client.get(
        f"/api/v1/summaries/?user_id={user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    summaries = response.json()
    user_summaries = [s for s in summaries if s["user_id"] == user_id]
    assert len(user_summaries) >= 3  # Should have at least our 3 generated summaries
    for summary in user_summaries:
        assert summary["user_id"] == user_id
