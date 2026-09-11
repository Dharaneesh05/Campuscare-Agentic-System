"""
Independent Test for Model Context Protocol (MCP) Tools.
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
    assert dept_res.get("status") == "found"

    # 2. Test save_complaint
    print("\n[Tool 2: save_complaint]")
    sample = {
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
    save_res = mcp_client.save_complaint(sample)
    assert save_res.get("status") == "success"
    ticket_id = save_res.get("ticket_id")

    # 3. Test prepare_notification
    print("\n[Tool 3: prepare_notification]")
    dept_notif = mcp_client.prepare_notification(ticket_id, "department", sample)
    assert dept_notif.get("status") == "ready"

    print("\n[All MCP Tests Passed Successfully!]")
    print("=" * 70)


if __name__ == "__main__":
    test_mcp_tools()
