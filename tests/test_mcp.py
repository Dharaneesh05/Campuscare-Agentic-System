"""
Independent Test for Model Context Protocol (MCP) Tools.
Verifies:
  1. get_department_contact tool
  2. save_complaint tool (persisting to data/complaints.json)
  3. prepare_notification tool (for department and student)
  4. File integrity of data/complaints.json
"""

import sys
import os
import json

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.mcp_client import mcp_client


def test_mcp_tools():
    print("=" * 70)
    print("Testing CampusCare AI - Model Context Protocol (MCP) Tools")
    print("=" * 70)

    # 1. Test get_department_contact
    print("\n[Tool 1: get_department_contact]")
    dept_res = mcp_client.get_department_contact("IT Support")
    print(f"  Result: {json.dumps(dept_res, indent=2)}")
    assert dept_res.get("status") == "found"
    assert "email" in dept_res.get("contact", {})

    # 2. Test save_complaint
    print("\n[Tool 2: save_complaint]")
    sample_complaint = {
        "student_name": "Arun Kumar",
        "student_email": "arun@example.edu",
        "class_department": "CSE",
        "complaint": "The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow.",
        "category": "Wi-Fi / Network",
        "priority": "HIGH",
        "department": "IT Support",
        "location": "Lab 3",
        "summary": "Wi-Fi is unavailable in Lab 3 before an online examination.",
        "suggested_action": "Immediately notify IT Support.",
        "response": "Your complaint has been classified as high priority and forwarded to IT Support."
    }

    save_res = mcp_client.save_complaint(sample_complaint)
    print(f"  Result: {json.dumps(save_res, indent=2)}")
    assert save_res.get("status") == "success"
    ticket_id = save_res.get("ticket_id")
    assert ticket_id is not None
    print(f"  Generated Ticket ID: {ticket_id}")

    # 3. Test prepare_notification for Department
    print("\n[Tool 3a: prepare_notification (Department)]")
    dept_notif = mcp_client.prepare_notification(ticket_id, "department", sample_complaint)
    print(f"  Result: {json.dumps(dept_notif, indent=2)}")
    assert dept_notif.get("status") == "ready"
    assert "to" in dept_notif
    assert dept_notif.get("to") == "it-support@campuscare.edu"

    # 4. Test prepare_notification for Student
    print("\n[Tool 3b: prepare_notification (Student)]")
    student_notif = mcp_client.prepare_notification(ticket_id, "student", sample_complaint)
    print(f"  Result: {json.dumps(student_notif, indent=2)}")
    assert student_notif.get("status") == "ready"
    assert student_notif.get("to") == "arun@example.edu"

    # 5. Verify data/complaints.json persistence
    print("\n[Tool Persistence Verification: data/complaints.json]")
    complaints_file = os.path.join(os.path.dirname(__file__), "..", "data", "complaints.json")
    with open(complaints_file, "r") as f:
        stored = json.load(f)
    print(f"  Total records in data/complaints.json: {len(stored)}")
    latest = stored[-1]
    print(f"  Latest Record Ticket ID: {latest.get('ticket_id')}")
    print(f"  Student: {latest.get('student_name')} ({latest.get('student_email')})")
    print(f"  Category: {latest.get('category')} | Priority: {latest.get('priority')} | Department: {latest.get('department')}")

    assert latest.get("ticket_id") == ticket_id
    assert latest.get("student_name") == "Arun Kumar"

    print("\n[All MCP Tool Tests Passed Successfully!]")
    print("=" * 70)


if __name__ == "__main__":
    test_mcp_tools()
