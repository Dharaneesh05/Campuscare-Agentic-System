"""
CampusCare AI - Student Complaint Portal (Gradio Frontend)
Provides a clean, intuitive web interface for students to submit complaints,
and visualizes the agentic AI classification, department routing, response,
and n8n automation dispatch in real time.
"""

import os
import json
import logging
import httpx
import gradio as gr

from core.workflow import complaint_workflow
from core.mcp_client import mcp_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CampusCare.Frontend")

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/complaint")


def process_complaint_ui(student_name: str, student_email: str, class_dept: str, complaint_text: str):
    """
    Submits the complaint to the FastAPI backend.
    If the backend service is offline, automatically executes via the local
    LangGraph + MCP pipeline as a resilient fallback.
    """
    if not complaint_text or not complaint_text.strip():
        return (
            "⚠️ Error",
            "N/A",
            "N/A",
            "N/A",
            "Please enter a valid complaint description.",
            "Please provide details regarding the issue.",
            "Submission blocked: Empty complaint field."
        )

    student_name = student_name.strip() or "Anonymous Student"
    student_email = student_email.strip() or "student@campuscare.edu"
    class_dept = class_dept.strip() or "General Department"

    payload = {
        "student_name": student_name,
        "student_email": student_email,
        "class_department": class_dept,
        "complaint": complaint_text
    }

    # Attempt 1: Call FastAPI Backend
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(BACKEND_URL, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Received response from FastAPI backend for ticket: {data.get('ticket_id')}")
                return (
                    data.get("category", "General"),
                    data.get("priority", "MEDIUM"),
                    data.get("department", "Helpdesk"),
                    data.get("location", "Campus Premises"),
                    data.get("summary", ""),
                    data.get("response", ""),
                    data.get("automation_status", "Processed successfully.")
                )
    except Exception as e:
        logger.warning(f"FastAPI backend unavailable ({e}). Processing directly with LangGraph + MCP.")

    # Attempt 2: Direct Local Agentic Execution (Self-Healing Fallback)
    agent_output = complaint_workflow.invoke(payload)
    save_result = mcp_client.save_complaint(agent_output)
    ticket_id = save_result.get("ticket_id", "CMP-LOCAL-001")

    category = agent_output.get("category", "General")
    priority = agent_output.get("priority", "MEDIUM")
    department = agent_output.get("department", "General Administration")
    location = agent_output.get("location", "Campus Premises")
    summary = agent_output.get("summary", "")
    response = agent_output.get("response", "")
    automation_status = (
        f"✅ Ticket #{ticket_id} logged via MCP tool. "
        f"Routed to {department} (Priority: {priority}). "
        f"Simulated n8n alert sent to department & student."
    )

    return (
        category,
        priority,
        department,
        location,
        summary,
        response,
        automation_status
    )


# Custom CSS styling for a modern university portal
custom_css = """
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    max-width: 1100px !important;
    margin: 0 auto !important;
}
.header-box {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    border-radius: 12px;
    margin-bottom: 24px;
}
.header-box h1 {
    color: white !important;
    font-size: 2.2rem;
    margin-bottom: 8px;
}
.header-box p {
    color: #e0e7ff;
    font-size: 1.05rem;
}
.submit-btn {
    background: #2563eb !important;
    color: white !important;
    font-size: 1.1rem !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
}
"""

with gr.Blocks(title="CampusCare AI - College Complaint System") as demo:
    gr.HTML("""
    <div class="header-box">
        <h1>🎓 CampusCare AI</h1>
        <p>An Agentic AI-Based College Complaint Classification & Automated Resolution System</p>
    </div>
    """)

    with gr.Row():
        # Left Column: Student Submission Form
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Submit College Complaint")
            student_name = gr.Textbox(label="Student Name", placeholder="e.g., Arun Kumar", value="Arun Kumar")
            student_email = gr.Textbox(label="Student Email", placeholder="e.g., arun@example.edu", value="arun@example.edu")
            class_dept = gr.Textbox(label="Class / Department", placeholder="e.g., CSE - 4th Year", value="CSE")
            complaint_text = gr.Textbox(
                label="Complaint Details",
                placeholder="Describe your issue in detail (e.g. Wi-Fi in Lab 3 is not working and we have an exam tomorrow)...",
                lines=5,
                value="The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."
            )
            submit_btn = gr.Button("Submit Complaint 🚀", elem_classes=["submit-btn"], variant="primary")

            gr.Markdown("#### 💡 Quick Demo Examples (Click to test)")
            example_wifi = gr.Button("1. Wi-Fi Down Before Exam (High Priority)")
            example_water = gr.Button("2. Water Leak in Hostel Washroom")
            example_projector = gr.Button("3. Projector Not Working in Room 204")
            example_power = gr.Button("4. Power Blackout in Block C")

        # Right Column: AI Analysis & Resolution Card
        with gr.Column(scale=1):
            gr.Markdown("### 🤖 Agentic AI Analysis & Resolution")
            with gr.Row():
                out_category = gr.Textbox(label="Identified Category", interactive=False)
                out_priority = gr.Textbox(label="Priority Level", interactive=False)
            with gr.Row():
                out_department = gr.Textbox(label="Responsible Department", interactive=False)
                out_location = gr.Textbox(label="Extracted Location", interactive=False)

            out_summary = gr.Textbox(label="Issue Summary", lines=2, interactive=False)
            out_response = gr.Textbox(label="Generated Response to Student", lines=3, interactive=False)
            out_status = gr.Textbox(label="Automation & Dispatch Status", lines=2, interactive=False)

    # Event Wireup
    submit_btn.click(
        fn=process_complaint_ui,
        inputs=[student_name, student_email, class_dept, complaint_text],
        outputs=[out_category, out_priority, out_department, out_location, out_summary, out_response, out_status]
    )

    # Quick Example Button Handlers
    example_wifi.click(
        fn=lambda: ("Arun Kumar", "arun@example.edu", "CSE", "The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."),
        inputs=[],
        outputs=[student_name, student_email, class_dept, complaint_text]
    )
    example_water.click(
        fn=lambda: ("Priya Sharma", "priya@example.edu", "ECE", "Water is leaking heavily from the pipe in Hostel Block B washroom."),
        inputs=[],
        outputs=[student_name, student_email, class_dept, complaint_text]
    )
    example_projector.click(
        fn=lambda: ("Karthik S.", "karthik@example.edu", "Mechanical", "The classroom projector in Room 204 is displaying a flickering blue screen during lectures."),
        inputs=[],
        outputs=[student_name, student_email, class_dept, complaint_text]
    )
    example_power.click(
        fn=lambda: ("Sneha R.", "sneha@example.edu", "Civil", "Complete electricity blackout in Block C first floor labs, sparks seen near the main switchboard."),
        inputs=[],
        outputs=[student_name, student_email, class_dept, complaint_text]
    )


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, css=custom_css, share=False)

