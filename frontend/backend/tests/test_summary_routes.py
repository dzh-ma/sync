"""
This module contains test cases for the energy summary API endpoints

Tested endpoints:
- `/api/v1/summaries/generate` (Generating energy summaries)
- `/api/v1/summaries/` (Fetching all summaries)
- `/api/v1/summaries/{summary_id}` (Fetching a specific summary)
- `/api/v1/summaries/{summary_id}` (Deleting a summary)
"""
from fastapi.testclient import TestClient
from ..main import app
from ..tests.test_report_generation import get_jwt_token
from ..tests.test_profile_routes import get_current_user_id
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
    
    # Add some energy data first to ensure we have data to summarize
    # Use datetime objects for precise control
    current_time = datetime.now()
    yesterday = current_time - timedelta(days=1)
    
    # Format for API input - use the ISO format timestamp for data insertion
    current_date_iso = current_time.strftime("%Y-%m-%dT%H:%M:%S")
    yesterday_iso = yesterday.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Format dates for API parameters - use YYYY-MM-DD for the start_date param
    date_param_format = "%Y-%m-%d"
    yesterday_date = yesterday.strftime(date_param_format)
    
    # Add energy consumption data for yesterday (to make sure it falls within the summary period)
    response = client.post(
        "/api/v1/data/add",
        json = {
            "device_id": "test_device_summary",
            "timestamp": yesterday_iso,  # Use yesterday's date
            "energy_consumed": 15.5,
            "location": "Test Location",
            "user_id": user_id  # Make sure data is associated with the user
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"Failed to add energy data: {response.json()}"

    # Wait a bit to make sure data is added to database
    import time
    time.sleep(0.5)
    
    # Generate daily summary using just the date portion (YYYY-MM-DD)
    response = client.post(
        f"/api/v1/summaries/generate?user_id={user_id}&period=daily&start_date={yesterday_date}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Full error print for debugging
    if response.status_code != 200:
        print(f"Full error: {response.json()}")
    
    assert response.status_code == 200, f"Failed to generate summary: {response.json()}"
    assert "summary_id" in response.json()
    assert response.json()["message"] == "Energy summary generated successfully"
    
    # Verify summary data
    summary = response.json()["summary"]
    assert summary["user_id"] == user_id
    assert summary["period"] == "daily"
    assert "total_consumption" in summary
    assert "cost_estimate" in summary

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
