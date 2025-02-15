import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)
REPORTS_DIR = "generated_reports"

def get_jwt_token():
    """
    Helper function to get a valid JWT token for testing.
    """
    response = client.post(
        "/api/v1/users/token",
        data={"username": "test_user", "password": "TestPassword123!"}
    )
    assert response.status_code == 200, f"Failed to get token: {response.json()}"
    return response.json().get("access_token")

@pytest.fixture(autouse=True)
def cleanup_generated_reports():
    """
    Fixture to clean up generated reports after each test.
    """
    yield
    if os.path.exists(REPORTS_DIR):
        for file in os.listdir(REPORTS_DIR):
            if file.endswith(".csv") or file.endswith(".pdf"):
                os.remove(os.path.join(REPORTS_DIR, file))

def test_generate_csv_report():
    """
    Test the generation of a CSV report.
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
    Test the generation of a PDF report.
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
    Test generating a report with date range filtering.
    """
    token = get_jwt_token()
    response = client.post(
        "/api/v1/reports/report?format=csv&start_date=2025-02-01&end_date=2025-02-02",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Failed to generate filtered CSV report: {response.json()}"
    assert response.headers["content-type"] == "application/octet-stream"

    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".csv")]
    assert len(files) == 1, "Filtered CSV report wasn't generated."
