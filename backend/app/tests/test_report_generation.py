import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

REPORTS_DIR = "generated_reports"

@pytest.fixture(autouse = True)
def cleanup_generated_reports():
    """
    Fixture to clean up generated reports after each test.
    """
    yield
    for file in os.listdir(REPORTS_DIR):
        if file.endswith(".csv") or file.endswith(".pdf"):
            os.remove(os.path.join(REPORTS_DIR, file))

def test_generate_csv_report():
    """
    Test the generation of a CSV report.
    """
    response = client.post("/api/v1/reports/report?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"

    # Check that the file was generated in the reports
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".csv")]
    assert len(files) == 1, "CSV report wasn't generated."

    # Check the file content
    with open(os.path.join(REPORTS_DIR, files[0]), "r") as f:
        content = f.read()
        assert "Device ID" in content   # Ensure header row is present

def test_generate_pdf_report():
    """
    Test the generation of a PDF report.
    """
    response = client.post("/api/v1/reports/report?format=pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"

    # Check that the file was generated in the reports
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".pdf")]
    assert len(files) == 1, "PDF report wasn't generated."

    # Ensure the PDF isn't empty
    pdf_file = os.path.join(REPORTS_DIR, files[0])
    assert os.path.getsize(pdf_file) > 100, "Generated PDF is too small, might be empty"

def test_generated_report_with_date_filter():
    """
    Test generating a report with date range filtering.
    """
    response = client.post("/api/v1/reports/report?format=csv&start_date=2025-02-01&end_date=2025-02-02")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"

    # Check that the file was generated
    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".csv")]
    assert len(files) == 1, "Filtered CSV report wasn't generated."
