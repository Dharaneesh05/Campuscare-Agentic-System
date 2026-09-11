"""
CampusCare AI - n8n Webhook Server Simulator.
Runs a lightweight HTTP server on port 5678 to simulate n8n:
  - Receives POST /webhook/campuscare-complaint
  - Evaluates priority & department routing
  - Logs notification dispatches
  - Returns structured acknowledgement JSON
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CampusCare.n8nSimulator")


class N8nWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode("utf-8"))
        except Exception:
            payload = {}

        ticket_id = payload.get("ticket_id", "CMP-SIMULATED")
        priority = payload.get("priority", "MEDIUM")
        department = payload.get("department", "General Administration")
        student = payload.get("student_name", "Student")
        dept_email = payload.get("department_notification", {}).get("to", "dept@campuscare.edu")
        student_email = payload.get("student_notification", {}).get("to", "student@campuscare.edu")

        print("=" * 60)
        print(f"⚡ [n8n Automation Engine] Webhook Triggered!")
        print(f"  🎟️ Ticket ID:           {ticket_id}")
        print(f"  🚨 Assessed Priority:    {priority}")
        print(f"  🏢 Routed Department:    {department}")
        print(f"  📧 Alert Email Sent To:  {dept_email}")
        print(f"  📩 Ack Email Sent To:    {student_email} ({student})")
        print("=" * 60)

        response_body = {
            "status": "success",
            "ticket_id": ticket_id,
            "assigned_department": department,
            "priority": priority,
            "acknowledged": True,
            "message": f"n8n automation successfully dispatched ticket {ticket_id} to {department} per SLA."
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode("utf-8"))

    def log_message(self, format, *args):
        # Clean logging
        return


def run_mock_n8n(port: int = 5678):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, N8nWebhookHandler)
    print(f"⚡ [n8n Simulator] Listening for webhooks at http://127.0.0.1:{port}/webhook/campuscare-complaint")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping n8n Simulator.")
        httpd.server_close()


if __name__ == "__main__":
    run_mock_n8n()
