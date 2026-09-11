"""
CampusCare AI - FastAPI Backend Application.
Provides REST endpoints for:
  - GET  /health: System status & uptime
  - GET  /departments: College department directory
  - GET  /complaints: View all stored complaints from JSON
  - POST /analyze: Agentic analysis via LangGraph (preview without save)
  - POST /complaint: Full agentic pipeline (LangGraph -> MCP -> n8n -> Response)
  - POST /webhook/mock-n8n: Local n8n receiver simulator
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import httpx
from dotenv import load_dotenv

from core.workflow import complaint_workflow
from core.mcp_client import mcp_client

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CampusCare.API")

app = FastAPI(
    title="CampusCare AI API",
    description="Agentic AI-Based College Complaint Classification and Automated Resolution System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/campuscare-complaint")


class ComplaintSubmission(BaseModel):
    student_name: str = Field(..., example="Arun Kumar")
    student_email: str = Field(..., example="arun@example.edu")
    class_department: str = Field(..., example="CSE")
    complaint: str = Field(..., example="The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow.")


class ComplaintResponse(BaseModel):
    ticket_id: Optional[str] = None
    student_name: str
    student_email: str
    class_department: str
    complaint: str
    category: str
    priority: str
    department: str
    location: str
    summary: str
    suggested_action: str
    response: str
    mcp_status: str
    automation_status: str


def trigger_n8n_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        logger.info(f"Triggering n8n webhook at: {N8N_WEBHOOK_URL}")
        with httpx.Client(timeout=3.0) as client:
            resp = client.post(N8N_WEBHOOK_URL, json=payload)
            if resp.status_code in [200, 201]:
                return {
                    "sent": True,
                    "mode": "live_n8n",
                    "status_code": resp.status_code,
                    "message": "Acknowledged by n8n workflow."
                }
    except Exception as e:
        logger.warning(f"Live n8n webhook connection failed ({e}). Using integrated automation simulator.")

    return {
        "sent": True,
        "mode": "simulated_n8n",
        "message": f"Simulated n8n workflow triggered: Alert dispatched to {payload.get('department')} & Student Confirmation queued."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "system": "CampusCare AI",
        "version": "1.0.0",
        "storage": "Pure JSON (No SQL / No Vector DB)"
    }


@app.get("/departments")
def get_departments():
    dept_file = os.path.join(os.path.dirname(__file__), "data", "departments.json")
    try:
        with open(dept_file, "r") as f:
            return json.load(f)
    except Exception:
        return {}


@app.get("/complaints")
def get_all_complaints():
    complaints_file = os.path.join(os.path.dirname(__file__), "data", "complaints.json")
    try:
        with open(complaints_file, "r") as f:
            return json.load(f)
    except Exception:
        return []


@app.post("/analyze")
def analyze_complaint(sub: ComplaintSubmission):
    initial_state = {
        "student_name": sub.student_name,
        "student_email": sub.student_email,
        "class_department": sub.class_department,
        "complaint": sub.complaint
    }
    final_state = complaint_workflow.invoke(initial_state)
    return final_state


@app.post("/complaint", response_model=ComplaintResponse)
def process_complaint(sub: ComplaintSubmission):
    state_input = {
        "student_name": sub.student_name,
        "student_email": sub.student_email,
        "class_department": sub.class_department,
        "complaint": sub.complaint
    }
    agent_output = complaint_workflow.invoke(state_input)

    save_result = mcp_client.save_complaint(agent_output)
    ticket_id = save_result.get("ticket_id", "CMP-UNKNOWN")

    dept_notif = mcp_client.prepare_notification(ticket_id, "department", agent_output)
    student_notif = mcp_client.prepare_notification(ticket_id, "student", agent_output)

    n8n_payload = {
        "ticket_id": ticket_id,
        "student_name": agent_output.get("student_name"),
        "student_email": agent_output.get("student_email"),
        "class_department": agent_output.get("class_department"),
        "complaint": agent_output.get("complaint"),
        "category": agent_output.get("category"),
        "priority": agent_output.get("priority"),
        "department": agent_output.get("department"),
        "location": agent_output.get("location"),
        "summary": agent_output.get("summary"),
        "suggested_action": agent_output.get("suggested_action"),
        "response": agent_output.get("response"),
        "department_notification": dept_notif,
        "student_notification": student_notif
    }

    n8n_res = trigger_n8n_webhook(n8n_payload)
    automation_status_msg = (
        f"Complaint logged as Ticket #{ticket_id}. "
        f"Assigned to {agent_output.get('department')} ({agent_output.get('priority')} Priority). "
        f"Automation: {n8n_res.get('message')}"
    )

    return ComplaintResponse(
        ticket_id=ticket_id,
        student_name=agent_output.get("student_name"),
        student_email=agent_output.get("student_email"),
        class_department=agent_output.get("class_department"),
        complaint=agent_output.get("complaint"),
        category=agent_output.get("category"),
        priority=agent_output.get("priority"),
        department=agent_output.get("department"),
        location=agent_output.get("location"),
        summary=agent_output.get("summary"),
        suggested_action=agent_output.get("suggested_action"),
        response=agent_output.get("response"),
        mcp_status=f"Saved via MCP tool: {ticket_id}",
        automation_status=automation_status_msg
    )


@app.post("/webhook/mock-n8n")
def mock_n8n_receiver(payload: Dict[str, Any]):
    ticket = payload.get("ticket_id")
    dept = payload.get("department")
    prio = payload.get("priority")
    logger.info(f"[Mock n8n Webhook] Received ticket {ticket} for {dept} with priority {prio}")
    return {
        "status": "success",
        "acknowledged": True,
        "ticket_id": ticket,
        "message": f"Mock n8n: Successfully routed {ticket} to {dept} with priority {prio}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
