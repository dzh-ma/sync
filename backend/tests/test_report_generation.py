"""
This module contains test cases for generating energy consumption reports

Tested functionality:
- Generating CSV & PDF reports
- Generating reports with date range filtering
- Ensuring reports are successfully created & contain valid data
"""
import pytest
from fastapi.testclient import TestClient
from ..main import app
import os

from app.tests.conftest import seed_energy_data

client = TestClient(app)
REPORTS_DIR = "generated_reports"

def get_jwt_token():
    """
    Helper function to get a valid JWT token for authentication in tests

    Returns:
        str: A valid access token

    Raises:
        AssertionError: If token retrieval fails
    """
    response = client.post(
        "/api/v1/users/token",
        data = {"username": "test_user@example.com", "password": "TestPassword123!"},
    )
    assert response.status_code == 200, f"Failed to get token: {response.json()}"
    return response.json().get("access_token")

@pytest.fixture(autouse=True)
def cleanup_generated_reports():
    """
    Fixture to remove all generated reports after each test

    Ensures that test-generated CSV & PDF reports don't persist between test runs
    """
    yield
    if os.path.exists(REPORTS_DIR):
        for file in os.listdir(REPORTS_DIR):
            if file.endswith(".csv") or file.endswith(".pdf"):
                os.remove(os.path.join(REPORTS_DIR, file))

def test_generate_csv_report():
    """
    Test the generation of an energy consumption CSV report

    - Sends a request to generate a CSV report
    - Verifies response status & content type
    - Ensures that the report is successfully created & contains valid data
    """
    token = get_jwt_token()
    response = client.post(
        "/api/v1/reports/report?format=csv",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Failed to generate CSV report: {response.json()}"
    assert response.headers["content-type"] == "application/octet-stream"

    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".csv")]
    assert len(files) == 1, "CSV report wasn't generated."

    with open(os.path.join(REPORTS_DIR, files[0]), "r") as f:
        content = f.read()
        assert "Device ID" in content, "CSV report content is invalid."

def test_generate_pdf_report():
    """
    Test the generation of an energy consumption PDF report

    - Sends a request to generate a PDF report
    - Verifies response status & content type
    - Ensures the report file is successfully created & isn't empty
    """
    token = get_jwt_token()
    response = client.post(
        "/api/v1/reports/report?format=pdf",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Failed to generate PDF report: {response.json()}"
    assert response.headers["content-type"] == "application/octet-stream"

    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".pdf")]
    assert len(files) == 1, "PDF report wasn't generated."

    pdf_file = os.path.join(REPORTS_DIR, files[0])
    assert os.path.getsize(pdf_file) > 100, "Generated PDF is too small, might be empty."

def test_generated_report_with_date_filter():
    """
    Test generating a report with date range filtering

    - Seeds test energy data before running
    - Sends a request to generate a filtered report
    - Verifies response status & content type
    - Ensure the report file is successfully created
    """
    seed_energy_data()
    token = get_jwt_token()
    response = client.post(
        "/api/v1/reports/report?format=csv&start_date=2025-02-01&end_date=2025-02-02",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Failed to generate filtered CSV report: {response.json()}"
    assert response.headers["content-type"] == "application/octet-stream"

    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".csv")]
    assert len(files) == 1, "Filtered CSV report wasn't generated."
