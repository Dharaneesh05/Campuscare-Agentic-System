"""
CampusCare AI - Model Context Protocol (MCP) Tool Server.
Exposes tools for:
  1. save_complaint: Persists complaint to data/complaints.json
  2. get_department_contact: Queries data/departments.json
  3. prepare_notification: Prepares email/webhook payload
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional
from mcp.server.mcpserver import MCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CampusCare.MCP")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMPLAINTS_FILE = os.path.join(BASE_DIR, "data", "complaints.json")
DEPARTMENTS_FILE = os.path.join(BASE_DIR, "data", "departments.json")

mcp_server = MCPServer("CampusCareTools")


def _read_json_file(file_path: str, default: Any) -> Any:
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return default


def _write_json_file(file_path: str, data: Any) -> bool:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error writing to {file_path}: {e}")
        return False


# MCP Tool 1: save_complaint
@mcp_server.tool()
def save_complaint(
    student_name: str,
    student_email: str,
    class_department: str,
    complaint: str,
    category: str,
    priority: str,
    department: str,
    location: str,
    summary: str,
    suggested_action: str,
    response: str
) -> str:
    complaints = _read_json_file(COMPLAINTS_FILE, [])

    ticket_number = len(complaints) + 1
    ticket_id = f"CMP-{time.strftime('%Y%m%d')}-{ticket_number:04d}"

    record = {
        "ticket_id": ticket_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "student_name": student_name,
        "student_email": student_email,
        "class_department": class_department,
        "complaint": complaint,
        "category": category,
        "priority": priority,
        "department": department,
        "location": location,
        "summary": summary,
        "suggested_action": suggested_action,
        "response": response,
        "status": "LOGGED_AND_ROUTED"
    }

    complaints.append(record)
    success = _write_json_file(COMPLAINTS_FILE, complaints)

    if success:
        logger.info(f"[MCP Tool: save_complaint] Saved complaint {ticket_id} for {student_name}")
        return json.dumps({
            "status": "success",
            "ticket_id": ticket_id,
            "message": f"Complaint successfully recorded with ID {ticket_id}."
        })
    else:
        return json.dumps({
            "status": "error",
            "message": "Failed to persist complaint to JSON storage."
        })


# MCP Tool 2: get_department_contact
@mcp_server.tool()
def get_department_contact(department_name: str) -> str:
    departments = _read_json_file(DEPARTMENTS_FILE, {})

    dept_info = departments.get(department_name)
    if not dept_info:
        for name, info in departments.items():
            if department_name.lower() in name.lower() or name.lower() in department_name.lower():
                dept_info = info
                department_name = name
                break

    if dept_info:
        logger.info(f"[MCP Tool: get_department_contact] Retrieved contact for {department_name}")
        return json.dumps({
            "status": "found",
            "department": department_name,
            "contact": dept_info
        })
    else:
        logger.warning(f"[MCP Tool: get_department_contact] Department '{department_name}' not found.")
        return json.dumps({
            "status": "not_found",
            "department": department_name,
            "contact": {
                "head": "General Helpdesk",
                "email": "helpdesk@campuscare.edu",
                "phone": "+91-9876500000",
                "location": "Administrative Block",
                "sla_hours": 24
            }
        })


# MCP Tool 3: prepare_notification
@mcp_server.tool()
def prepare_notification(
    ticket_id: str,
    recipient_type: str,
    student_name: str,
    student_email: str,
    department: str,
    category: str,
    priority: str,
    location: str,
    summary: str
) -> str:
    dept_contact_res = json.loads(get_department_contact(department_name=department))
    dept_email = dept_contact_res.get("contact", {}).get("email", "admin@campuscare.edu")

    if recipient_type.lower() == "department":
        subject = f"[{priority} PRIORITY] New Campus Complaint - {ticket_id}: {category}"
        body = (
            f"Dear {department} Team,\n\n"
            f"A new student complaint has been classified and forwarded to your department.\n\n"
            f"Ticket ID: {ticket_id}\n"
            f"Priority: {priority}\n"
            f"Category: {category}\n"
            f"Location: {location}\n"
            f"Summary: {summary}\n"
            f"Student: {student_name} ({student_email})\n\n"
            f"Please take prompt action per your SLA.\n"
            f"- CampusCare AI System"
        )
        target_email = dept_email
    else:
        subject = f"CampusCare AI: Complaint Confirmation [{ticket_id}]"
        body = (
            f"Dear {student_name},\n\n"
            f"Your complaint regarding '{category}' at {location} has been successfully registered.\n\n"
            f"Ticket ID: {ticket_id}\n"
            f"Priority: {priority}\n"
            f"Assigned Department: {department} ({dept_email})\n\n"
            f"The responsible department has been alerted.\n"
            f"- CampusCare Automated Support"
        )
        target_email = student_email

    logger.info(f"[MCP Tool: prepare_notification] Notification prepared for {recipient_type} ({target_email})")
    return json.dumps({
        "status": "ready",
        "ticket_id": ticket_id,
        "recipient_type": recipient_type,
        "to": target_email,
        "subject": subject,
        "body": body
    })


if __name__ == "__main__":
    mcp_server.run()
