"""
Independent Test for CampusCare AI FastAPI Backend.
Uses FastAPI TestClient to verify:
  - GET  /health
  - GET  /departments
  - POST /analyze
  - POST /complaint
  - GET  /complaints
"""

import sys
import os
import json
from fastapi.testclient import TestClient

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app

client = TestClient(app)


def test_api_endpoints():
    print("=" * 70)
    print("Testing CampusCare AI - FastAPI Backend Endpoints")
    print("=" * 70)

    # 1. Test GET /health
    print("\n[1. Testing GET /health]")
    res_health = client.get("/health")
    print(f"Status Code: {res_health.status_code}")
    print(f"Response:    {res_health.json()}")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # 2. Test GET /departments
    print("\n[2. Testing GET /departments]")
    res_depts = client.get("/departments")
    print(f"Status Code: {res_depts.status_code}")
    depts = res_depts.json()
    print(f"Departments Found: {list(depts.keys())}")
    assert res_depts.status_code == 200
    assert "IT Support" in depts

    # 3. Test POST /analyze
    print("\n[3. Testing POST /analyze]")
    payload = {
        "student_name": "Arun Kumar",
        "student_email": "arun@example.edu",
        "class_department": "CSE",
        "complaint": "The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."
    }
    res_analyze = client.post("/analyze", json=payload)
    print(f"Status Code: {res_analyze.status_code}")
    analyze_data = res_analyze.json()
    print(f"Analysis Output:\n{json.dumps(analyze_data, indent=2)}")
    assert res_analyze.status_code == 200
    assert analyze_data["category"] == "Wi-Fi / Network"
    assert analyze_data["department"] == "IT Support"
    assert analyze_data["priority"] in ["HIGH", "URGENT"]

    # 4. Test POST /complaint
    print("\n[4. Testing POST /complaint (Full Pipeline)]")
    res_complaint = client.post("/complaint", json=payload)
    print(f"Status Code: {res_complaint.status_code}")
    complaint_data = res_complaint.json()
    print(f"Complaint Resolution Output:\n{json.dumps(complaint_data, indent=2)}")
    assert res_complaint.status_code == 200
    assert complaint_data["ticket_id"].startswith("CMP-")
    assert complaint_data["category"] == "Wi-Fi / Network"
    assert complaint_data["department"] == "IT Support"
    assert "Saved via MCP tool" in complaint_data["mcp_status"]

    # 5. Test GET /complaints
    print("\n[5. Testing GET /complaints]")
    res_all = client.get("/complaints")
    assert res_all.status_code == 200
    all_complaints = res_all.json()
    print(f"Total Stored Complaints: {len(all_complaints)}")
    assert len(all_complaints) > 0

    print("\n[All FastAPI Backend Tests Passed Successfully!]")
    print("=" * 70)


if __name__ == "__main__":
    test_api_endpoints()
