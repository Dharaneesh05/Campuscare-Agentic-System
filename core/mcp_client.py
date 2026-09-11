"""
CampusCare AI - MCP Client Helper.
Provides a unified Python interface to invoke the MCP tools:
- save_complaint()
- get_department_contact()
- prepare_notification()
"""

import json
import logging
from typing import Dict, Any

from mcp_service.server import (
    save_complaint as mcp_save_complaint,
    get_department_contact as mcp_get_department_contact,
    prepare_notification as mcp_prepare_notification
)

logger = logging.getLogger("CampusCare.MCPClient")


class CampusCareMCPClient:
    """Client wrapper for calling registered MCP tools."""

    @staticmethod
    def save_complaint(record: Dict[str, Any]) -> Dict[str, Any]:
        """Calls the save_complaint MCP tool to persist to data/complaints.json."""
        res_str = mcp_save_complaint(
            student_name=record.get("student_name", "Anonymous"),
            student_email=record.get("student_email", "student@example.edu"),
            class_department=record.get("class_department", "General"),
            complaint=record.get("complaint", ""),
            category=record.get("category", "General"),
            priority=record.get("priority", "MEDIUM"),
            department=record.get("department", "General Administration"),
            location=record.get("location", "Campus"),
            summary=record.get("summary", ""),
            suggested_action=record.get("suggested_action", ""),
            response=record.get("response", "")
        )
        return json.loads(res_str)

    @staticmethod
    def get_department_contact(department_name: str) -> Dict[str, Any]:
        """Calls the get_department_contact MCP tool."""
        res_str = mcp_get_department_contact(department_name=department_name)
        return json.loads(res_str)

    @staticmethod
    def prepare_notification(ticket_id: str, recipient_type: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Calls the prepare_notification MCP tool."""
        res_str = mcp_prepare_notification(
            ticket_id=ticket_id,
            recipient_type=recipient_type,
            student_name=state.get("student_name", "Student"),
            student_email=state.get("student_email", "student@example.edu"),
            department=state.get("department", "General Administration"),
            category=state.get("category", "General"),
            priority=state.get("priority", "MEDIUM"),
            location=state.get("location", "Campus"),
            summary=state.get("summary", "")
        )
        return json.loads(res_str)


mcp_client = CampusCareMCPClient()
