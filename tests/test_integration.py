"""
Integration Test for FastAPI + Gradio Connected System.
Verifies:
  1. Gradio UI is mounted and accessible at GET /
  2. FastAPI health check at GET /health
  3. POST /complaint generates ticket and response
  4. End-to-end UI logic flow matches expected output structure
"""

import sys
import os
import json
from fastapi.testclient import TestClient

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_app import app
from frontend import process_complaint_ui

client = TestClient(app)


def test_fastapi_gradio_integration():
    print("=" * 70)
    print("Testing CampusCare AI - FastAPI + Gradio Integration")
    print("=" * 70)

    # 1. Test GET /health
    print("\n[1. Testing FastAPI Backend Health]")
    res_health = client.get("/health")
    print(f"Status Code: {res_health.status_code}")
    print(f"Response:    {res_health.json()}")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # 2. Test GET / (Gradio UI Mount)
    print("\n[2. Testing Gradio UI Mounted on FastAPI]")
    res_ui = client.get("/")
    print(f"Status Code: {res_ui.status_code}")
    assert res_ui.status_code == 200
    assert "text/html" in res_ui.headers.get("content-type", "")
    print("  Gradio HTML successfully served at root /")

    # 3. Test POST /complaint via FastAPI
    print("\n[3. Testing Backend Resolution Pipeline]")
    submission = {
        "student_name": "Arun Kumar",
        "student_email": "arun@example.edu",
        "class_department": "CSE",
        "complaint": "The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."
    }
    res_api = client.post("/complaint", json=submission)
    print(f"Status Code: {res_api.status_code}")
    data = res_api.json()
    print(f"Ticket ID:   {data.get('ticket_id')}")
    print(f"Category:    {data.get('category')}")
    print(f"Priority:    {data.get('priority')}")
    print(f"Department:  {data.get('department')}")
    assert res_api.status_code == 200
    assert data.get("ticket_id").startswith("CMP-")
    assert data.get("category") == "Wi-Fi / Network"

    # 4. Test Frontend UI Handler Logic
    print("\n[4. Testing Frontend UI Callback]")
    ui_out = process_complaint_ui(
        student_name=submission["student_name"],
        student_email=submission["student_email"],
        class_dept=submission["class_department"],
        complaint_text=submission["complaint"]
    )
    print(f"UI Outputs: Category={ui_out[0]}, Priority={ui_out[1]}, Dept={ui_out[2]}")
    assert ui_out[0] == "Wi-Fi / Network"
    assert ui_out[1] in ["HIGH", "URGENT"]
    assert ui_out[2] == "IT Support"

    print("\n[FastAPI + Gradio Integration Test Passed Successfully!]")
    print("=" * 70)


if __name__ == "__main__":
    test_fastapi_gradio_integration()
