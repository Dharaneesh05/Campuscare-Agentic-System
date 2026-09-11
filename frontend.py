"""
CampusCare AI - Student Complaint Portal (Gradio Frontend)
Clean, professional complaint submission portal with real-time agentic AI analysis,
department routing, email notification preview, and n8n automation status.
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
    Processes the complaint via FastAPI backend or local LangGraph + MCP fallback.
    Returns structured results including department email and staff routing.
    """
    if not complaint_text or not complaint_text.strip():
        return (
            "⚠️ Error",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "Please enter a valid complaint description.",
            "Please provide details regarding the issue.",
            "Submission blocked: Empty complaint field."
        )

    student_name = student_name.strip() or "dharaneesh"
    student_email = student_email.strip() or "dharaneeshc2006@gmail.com"
    class_dept = class_dept.strip() or "CSE"

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
                    data.get("department_email", "dharaneeshc2006@gmail.com"),
                    data.get("department_head", "Lead Officer"),
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
    dept_info = agent_output.get("department_contact", {})
    dept_email = dept_info.get("email", "dharaneeshc2006@gmail.com")
    dept_head = dept_info.get("head", "Department Officer")
    location = agent_output.get("location", "Campus Premises")
    summary = agent_output.get("summary", "")
    response = agent_output.get("response", "")
    automation_status = (
        f"✅ Ticket #{ticket_id} logged via MCP tool. "
        f"Routed to {department} (Priority: {priority}). "
        f"Alert dispatched to {dept_email} & Student Confirmation queued."
    )

    return (
        category,
        priority,
        department,
        dept_email,
        dept_head,
        location,
        summary,
        response,
        automation_status
    )


custom_css = """
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    max-width: 1200px !important;
    margin: 0 auto !important;
}
.header-box {
    text-align: center;
    padding: 24px;
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.header-box h1 {
    color: white !important;
    font-size: 2.2rem;
    margin-bottom: 8px;
    font-weight: 700;
}
.header-box p {
    color: #e0e7ff;
    font-size: 1.1rem;
}
.submit-btn {
    background: #2563eb !important;
    color: white !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    margin-top: 10px !important;
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
        with gr.Column(scale=5):
            gr.Markdown("### 📝 Submit College Complaint")
            student_name = gr.Textbox(
                label="Student Name",
                placeholder="Enter your name (e.g. dharaneesh)",
                value="dharaneesh"
            )
            student_email = gr.Textbox(
                label="Student Email",
                placeholder="Enter your email (e.g. dharaneeshc2006@gmail.com)",
                value="dharaneeshc2006@gmail.com"
            )
            class_dept = gr.Textbox(
                label="Class / Department",
                placeholder="Enter your class (e.g. CSE)",
                value="CSE"
            )
            complaint_text = gr.Textbox(
                label="Complaint Details",
                placeholder="Describe your issue in detail (e.g. water supply problem on the bathroom, Wi-Fi in Lab 3 is down, classroom projector not turning on)...",
                lines=6,
                value="water supply problem on the bathroom"
            )
            submit_btn = gr.Button("Submit Complaint 🚀", elem_classes=["submit-btn"], variant="primary")

        # Right Column: AI Analysis & Resolution Output
        with gr.Column(scale=6):
            gr.Markdown("### 🤖 Agentic AI Analysis & Resolution")
            with gr.Row():
                out_category = gr.Textbox(label="Identified Category", interactive=False)
                out_priority = gr.Textbox(label="Priority Level", interactive=False)

            with gr.Row():
                out_department = gr.Textbox(label="Responsible Department", interactive=False)
                out_location = gr.Textbox(label="Extracted Location", interactive=False)

            with gr.Row():
                out_dept_email = gr.Textbox(label="Dispatched Department Email", interactive=False)
                out_dept_head = gr.Textbox(label="Department Head / Contact", interactive=False)

            out_summary = gr.Textbox(label="Issue Summary", lines=2, interactive=False)
            out_response = gr.Textbox(label="Generated Response to Student", lines=3, interactive=False)
            out_status = gr.Textbox(label="Automation & Dispatch Status", lines=2, interactive=False)

    # Event Wireup
    submit_btn.click(
        fn=process_complaint_ui,
        inputs=[student_name, student_email, class_dept, complaint_text],
        outputs=[
            out_category,
            out_priority,
            out_department,
            out_dept_email,
            out_dept_head,
            out_location,
            out_summary,
            out_response,
            out_status
        ]
    )


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, css=custom_css, share=False)
