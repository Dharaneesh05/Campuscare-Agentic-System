"""
LangGraph Multi-Agent Workflow for CampusCare AI.
Orchestrates:
  1. Analyzer Agent (Issue Extraction & Location)
  2. Priority Agent (Urgency Assessment)
  3. Routing Agent (Department Matching)
  4. Response Agent (Professional Student Communication)
  5. Action Decider Node (MCP Tool Payload Preparation)
"""

import os
import json
import logging
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END

from core.llm import llm_client

logger = logging.getLogger("CampusCare.Workflow")


# Define State Schema for LangGraph
class ComplaintState(TypedDict, total=False):
    # Student Inputs
    student_name: str
    student_email: str
    class_department: str
    complaint: str

    # 1. Analyzer Agent Outputs
    category: str
    location: str
    summary: str

    # 2. Priority Agent Outputs
    priority: str
    urgency_reason: str

    # 3. Routing Agent Outputs
    department: str
    suggested_action: str
    department_contact: Dict[str, Any]

    # 4. Response Agent Outputs
    response: str

    # 5. Action Decider Outputs
    tool_action: str
    status: str


def _load_departments() -> Dict[str, Any]:
    """Loads department data from JSON."""
    dept_file = os.path.join(os.path.dirname(__file__), "..", "data", "departments.json")
    try:
        with open(dept_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load departments.json: {e}")
        return {}


# -------------------------------------------------------------
# Agent 1: Analyzer Agent
# -------------------------------------------------------------
def analyzer_agent(state: ComplaintState) -> Dict[str, Any]:
    complaint_text = state.get("complaint", "")
    logger.info(f"[Agent 1: Analyzer] Analyzing: '{complaint_text[:50]}...'")

    prompt = (
        f"Analyze the following student college complaint:\n"
        f"Complaint: \"{complaint_text}\"\n\n"
        f"Return a JSON with:\n"
        f"- category: (e.g. Wi-Fi / Network, Classroom AV / Projector, Lab Computers, Electricity / Power, Water / Plumbing, Hostel Maintenance, Transport, Library Services, Canteen / Food)\n"
        f"- location: (Specific room, lab, floor, or hostel mentioned)\n"
        f"- summary: (Concise 1-sentence issue description)"
    )

    llm_output = llm_client.generate(prompt=prompt)
    try:
        data = json.loads(llm_output)
        return {
            "category": data.get("category", "General Campus Infrastructure"),
            "location": data.get("location", "Campus Premises"),
            "summary": data.get("summary", complaint_text)
        }
    except Exception:
        return {
            "category": "General Campus Infrastructure",
            "location": "Campus Premises",
            "summary": complaint_text
        }


# -------------------------------------------------------------
# Agent 2: Priority Agent
# -------------------------------------------------------------
def priority_agent(state: ComplaintState) -> Dict[str, Any]:
    complaint_text = state.get("complaint", "")
    category = state.get("category", "")
    summary = state.get("summary", "")

    logger.info(f"[Agent 2: Priority] Assessing priority for category: {category}")

    prompt = (
        f"Evaluate the urgency of this college issue:\n"
        f"Category: {category}\n"
        f"Summary: {summary}\n"
        f"Full Complaint: \"{complaint_text}\"\n\n"
        f"Return a JSON with:\n"
        f"- priority: (LOW, MEDIUM, HIGH, or URGENT)\n"
        f"- urgency_reason: (Short explanation why this priority was assigned)"
    )

    llm_output = llm_client.generate(prompt=prompt)
    try:
        data = json.loads(llm_output)
        priority = data.get("priority", "MEDIUM").upper()
        if priority not in ["LOW", "MEDIUM", "HIGH", "URGENT"]:
            priority = "MEDIUM"
        return {
            "priority": priority,
            "urgency_reason": data.get("urgency_reason", "Assigned based on complaint context.")
        }
    except Exception:
        text_lower = complaint_text.lower()
        p = "HIGH" if any(w in text_lower for w in ["exam", "test", "urgent", "hazard", "spark", "flood"]) else "MEDIUM"
        return {
            "priority": p,
            "urgency_reason": "Evaluated based on critical academic/facility timeline."
        }


# -------------------------------------------------------------
# Agent 3: Department Routing Agent
# -------------------------------------------------------------
def routing_agent(state: ComplaintState) -> Dict[str, Any]:
    category = state.get("category", "")
    departments = _load_departments()
    logger.info(f"[Agent 3: Routing] Routing complaint category: {category}")

    mapping = {
        "Wi-Fi / Network": "IT Support",
        "Classroom AV / Projector": "IT Support",
        "Lab Computers / Software": "IT Support",
        "Electricity / Power": "Electrical Maintenance",
        "Water / Plumbing": "Civil & Plumbing Maintenance",
        "Hostel Maintenance": "Hostel Administration",
        "Transport": "Transport Department",
        "Library Services": "Library Administration",
        "Canteen / Food": "Canteen & Food Services"
    }

    dept_name = mapping.get(category, "General Administration")
    dept_info = departments.get(dept_name, {
        "head": "Helpdesk Supervisor",
        "email": "helpdesk@campuscare.edu",
        "phone": "+91-9876500000",
        "location": "Central Administration",
        "sla_hours": 24
    })

    action = f"Immediately notify {dept_name} ({dept_info.get('head', 'Lead')}) at {dept_info.get('location')}."

    return {
        "department": dept_name,
        "department_contact": dept_info,
        "suggested_action": action
    }


# -------------------------------------------------------------
# Agent 4: Response Agent
# -------------------------------------------------------------
def response_agent(state: ComplaintState) -> Dict[str, Any]:
    student_name = state.get("student_name", "Student")
    category = state.get("category", "General")
    priority = state.get("priority", "MEDIUM")
    department = state.get("department", "Helpdesk")
    location = state.get("location", "Campus")

    logger.info(f"[Agent 4: Response] Generating response for {student_name}")

    prompt = (
        f"Write a professional college complaint acknowledgment response to:\n"
        f"Student Name: {student_name}\n"
        f"Issue: {category} at {location}\n"
        f"Priority: {priority}\n"
        f"Assigned Department: {department}\n\n"
        f"Tone: Courteous, reassuring, clear. Keep it within 2-3 sentences."
    )

    llm_output = llm_client.generate(prompt=prompt)
    try:
        data = json.loads(llm_output)
        response_text = data.get("response", llm_output)
    except Exception:
        response_text = (
            f"Dear {student_name}, thank you for reporting the {category} issue at {location}. "
            f"Your complaint has been assigned {priority} priority and dispatched to {department}. "
            f"Our team is addressing the matter swiftly."
        )

    return {"response": response_text}


# -------------------------------------------------------------
# Agent 5: Action Decider Node (MCP / Automation Prep)
# -------------------------------------------------------------
def action_decision_node(state: ComplaintState) -> Dict[str, Any]:
    priority = state.get("priority", "MEDIUM")
    department = state.get("department", "General Administration")

    logger.info(f"[Agent 5: Action Decider] Determining tool actions for {priority} ticket.")

    tool_action = f"save_complaint_and_notify_{department.lower().replace(' ', '_')}"
    status = f"Ready for MCP tool execution and n8n webhook dispatch to {department} (Priority: {priority})."

    return {
        "tool_action": tool_action,
        "status": status
    }


# -------------------------------------------------------------
# Graph Builder Function
# -------------------------------------------------------------
def build_complaint_graph():
    workflow = StateGraph(ComplaintState)

    workflow.add_node("analyzer_agent", analyzer_agent)
    workflow.add_node("priority_agent", priority_agent)
    workflow.add_node("routing_agent", routing_agent)
    workflow.add_node("response_agent", response_agent)
    workflow.add_node("action_decider", action_decision_node)

    workflow.set_entry_point("analyzer_agent")
    workflow.add_edge("analyzer_agent", "priority_agent")
    workflow.add_edge("priority_agent", "routing_agent")
    workflow.add_edge("routing_agent", "response_agent")
    workflow.add_edge("response_agent", "action_decider")
    workflow.add_edge("action_decider", END)

    return workflow.compile()


complaint_workflow = build_complaint_graph()
