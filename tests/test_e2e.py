"""
End-to-End Workflow Verification for CampusCare AI.
Tests the complete integration pipeline:
  Student Input
  -> FastAPI Backend (/complaint)
  -> LangGraph Multi-Agent Workflow
  -> Model Context Protocol (MCP) Tool Persistence
  -> n8n Webhook Dispatch & Acknowledgment
  -> Final Gradio Response Payload
"""

import sys
import os
import json
import threading
import time
from fastapi.testclient import TestClient

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from n8n.mock_n8n_server import run_mock_n8n


def start_background_n8n():
    """Starts the n8n webhook listener in a background thread."""
    t = threading.Thread(target=run_mock_n8n, kwargs={"port": 5678}, daemon=True)
    t.start()
    time.sleep(1)
    return t


def test_end_to_end_pipeline():
    print("=" * 75)
    print("🎓 CampusCare AI: End-to-End System Verification")
    print("=" * 75)

    # 1. Start n8n webhook listener
    print("\n[Step 1: Initializing n8n Webhook Automation Listener...]")
    start_background_n8n()

    # 2. Prepare student complaint submission
    client = TestClient(app)
    student_payload = {
        "student_name": "Arun Kumar",
        "student_email": "arun@example.edu",
        "class_department": "CSE - 4th Year",
        "complaint": "The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."
    }

    print("\n[Step 2: Student Submits Complaint via Portal]")
    print(f"  Name:       {student_payload['student_name']}")
    print(f"  Email:      {student_payload['student_email']}")
    print(f"  Class:      {student_payload['class_department']}")
    print(f"  Complaint:  \"{student_payload['complaint']}\"")

    # 3. Post to FastAPI /complaint
    print("\n[Step 3: Executing FastAPI Backend & LangGraph Agent Graph...]")
    response = client.post("/complaint", json=student_payload)

    print(f"\n[Step 4: Checking Response Status Code]: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    print("\n[Step 5: Inspecting Structured AI Result]:")
    print("-" * 75)
    print(f"  Ticket ID:           {data.get('ticket_id')}")
    print(f"  Category:            {data.get('category')}")
    print(f"  Priority:            {data.get('priority')}")
    print(f"  Assigned Department: {data.get('department')}")
    print(f"  Detected Location:   {data.get('location')}")
    print(f"  Summary:             {data.get('summary')}")
    print(f"  Suggested Action:    {data.get('suggested_action')}")
    print(f"  Student Response:    {data.get('response')}")
    print(f"  MCP Tool Status:     {data.get('mcp_status')}")
    print(f"  Automation Status:   {data.get('automation_status')}")
    print("-" * 75)

    # 4. Assertions on AI output
    assert data.get("category") == "Wi-Fi / Network"
    assert data.get("priority") in ["HIGH", "URGENT"]
    assert data.get("department") == "IT Support"
    assert "Lab 3" in data.get("location")
    assert "CMP-" in data.get("ticket_id")
    assert "Acknowledged by n8n workflow" in data.get("automation_status") or "live_n8n" in data.get("automation_status") or "Dispatched" in data.get("automation_status") or "Ticket #" in data.get("automation_status")

    # 5. Check persistent storage in data/complaints.json
    print("\n[Step 6: Verifying JSON Storage Integrity (data/complaints.json)...]")
    complaints_path = os.path.join(os.path.dirname(__file__), "..", "data", "complaints.json")
    with open(complaints_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    latest_record = records[-1]
    print(f"  Total Complaints Stored: {len(records)}")
    print(f"  Latest Logged Ticket:    {latest_record.get('ticket_id')}")
    print(f"  Saved Department:        {latest_record.get('department')}")
    print(f"  Saved Priority:          {latest_record.get('priority')}")

    assert latest_record.get("ticket_id") == data.get("ticket_id")
    assert latest_record.get("student_name") == "Arun Kumar"
    assert latest_record.get("department") == "IT Support"

    print("\n" + "=" * 75)
    print("🎉 ALL END-TO-END VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_end_to_end_pipeline()
