# CampusCare AI
### An Agentic AI-Based College Complaint Classification & Automated Resolution System

![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)
![Framework](https://img.shields.io/badge/Backend-FastAPI-009688.svg)
![Frontend](https://img.shields.io/badge/Frontend-Gradio-orange.svg)
![Agentic Orchestration](https://img.shields.io/badge/Agents-LangGraph-purple.svg)
![Tool Protocol](https://img.shields.io/badge/Tools-MCP%20Protocol-green.svg)
![Automation](https://img.shields.io/badge/Workflow-n8n-red.svg)
![Storage](https://img.shields.io/badge/Storage-Pure%20JSON%20(No%20SQL)-yellow.svg)

---

## 📌 1. Project Overview

**CampusCare AI** is an intelligent, agentic grievance management system designed for educational institutions. In traditional colleges, student complaints regarding lab computers, power cuts, plumbing leaks, bus delays, hostel issues, or canteen food are often delayed due to manual paper forms, misrouting, and slow communication.

CampusCare AI solves this by introducing an autonomous **Multi-Agent AI Pipeline**:
1. Students submit complaints through a clean, modern **Gradio Web Portal**.
2. **LangGraph Multi-Agent Orchestrator** analyzes the complaint text, determines severity and SLA, identifies the specific college location, and routes it to the exact responsible department.
3. **Model Context Protocol (MCP)** tools record the ticket and format official notifications.
4. **n8n Automation Engine** coordinates the resolution workflow, triggers emergency escalation paths, and dispatches real-time HTML notifications directly to:
   - 🚨 **The Department Lead** (for immediate field resolution).
   - 🎓 **The Student** (official registration receipt and SLA timeline).
5. All records persist strictly in lightweight, human-readable **Pure JSON files** (zero external SQL/NoSQL/Vector databases required).

---

## 🏛️ 2. System Architecture

```
[ Student / User ]
        │
        ▼ (Submits Grievance via Web UI)
┌─────────────────────────────────────────────────────────────┐
│                 Gradio Frontend Portal                      │
│                  (http://127.0.0.1:8000/)                   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (REST API Call)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Core Backend Engine                 │
│                   - Healthcheck & Routing                   │
│                   - Swagger UI (/docs)                      │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼ (Agentic Execution)           ▼ (Tools Execution)
┌──────────────────────────────┐ ┌─────────────────────────────┐
│     LangGraph Multi-Agent    │ │    MCP Server & Client      │
│  1. Complaint Analyzer       │ │  - save_complaint()         │
│  2. Priority Classifier      │ │  - get_department_contact() │
│  3. Department Router        │ │  - prepare_notification()   │
│  4. Response Generator       │ └──────────────┬──────────────┘
│  5. Action Decider           │                │
└──────────────┬───────────────┘                ▼
               │                    ┌──────────────────────────┐
               │                    │    Pure JSON Storage     │
               │                    │  - data/complaints.json  │
               │                    │  - data/departments.json │
               │                    └──────────────────────────┘
               ▼ (Webhook Trigger)
┌─────────────────────────────────────────────────────────────┐
│                  n8n Workflow Automation Engine             │
│                    (http://localhost:5678)                  │
│                                                             │
│   [Webhook Receiver] ──► [Priority Router]                  │
│                                ├──► [Urgent Escalation]     │
│                                └──► [Standard Dispatch]    │
│                                             │               │
│   [Respond to Webhook] ◄── [Student Email] ◄┴─ [Dept Alert] │
└──────────────────────────────┬──────────────────────────────┘
                               │ (HTTPS Port 443)
                               ▼
          ┌─────────────────────────────────────────┐
          │     Real-Time Email Notifications       │
          │  🚨 Department Alert  |  🎓 Student Ack │
          └─────────────────────────────────────────┘
```

---

## 🛠️ 3. Tech Stack & Engineering Constraints

* **Frontend**: [Gradio](https://www.gradio.app/) — Mounted cleanly onto FastAPI root, providing an intuitive dual-panel interface (Submission Form on left, Real-time Resolution Card on right).
* **Backend**: [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn — High-performance asynchronous REST API.
* **Agentic Framework**: [LangGraph](https://python.langchain.com/docs/langgraph/) — Stateful multi-agent graph directing analysis from raw text to structured ticket.
* **LLM Engine**: Hugging Face Inference API (`router.huggingface.co`) + **Resilient Heuristic Fallback Engine** (guarantees 100% uptime even without cloud API credits or during network drops).
* **Tool Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — Decoupled tool layer for saving complaints and fetching department contacts.
* **Automation Workflow**: [n8n](https://n8n.io/) — Self-hosted automation platform for conditional routing, SLA tracking, and email dispatch.
* **Storage Constraint**: **Pure JSON Only** (`data/complaints.json` and `data/departments.json`). Strictly NO SQLite, PostgreSQL, MongoDB, Redis, or Vector Databases.
* **Email Protocol**: Modern **HTTPS Webhook API (Port 443)** using Google Apps Script / Resend, completely avoiding blocked legacy SMTP ports (`465`/`587`).

---

## 🤖 4. LangGraph Multi-Agent Pipeline

The resolution pipeline consists of **5 autonomous agents** running sequentially:

```
[Agent 1: Analyzer] ──► [Agent 2: Priority] ──► [Agent 3: Routing] ──► [Agent 4: Response] ──► [Agent 5: Action Decider]
```

1. **Agent 1: Complaint Analyzer**
   - Parses student narrative.
   - Extracts the core grievance category (e.g. `Electricity / Power`, `Water / Plumbing`, `Transport`, `Wi-Fi / Network`).
   - Extracts the exact campus location (e.g., `Room 204 Near Block B`, `Lab 3`, `Seminar Hall 2`).
2. **Agent 2: Priority Classifier**
   - Assesses urgency and risk factors.
   - Assigns priority:
     - 🚨 **URGENT**: Immediate hazards (sparks, floods, fire, gas, structural dangers).
     - ⚠️ **HIGH**: Critical academic blockers (exam tomorrow, lab test today, presentation).
     - ℹ️ **MEDIUM / LOW**: Routine maintenance and non-urgent repairs.
3. **Agent 3: Department Router**
   - Queries `data/departments.json` via MCP tools.
   - Matches the issue to the responsible college department and assigns the department head and contact info.
4. **Agent 4: Response Generator**
   - Drafts an empathetic, official acknowledgement message to the student detailing the resolution procedure and committed SLA.
5. **Agent 5: Action Decider & MCP Dispatcher**
   - Calls MCP tools to generate ticket IDs, persists the ticket into `data/complaints.json`, prepares dispatch payloads, and triggers n8n.

---

## 🔄 5. Detailed n8n Workflow Breakdown

The n8n automation workflow (`CampusCare AI Automated Resolution Workflow`) is composed of **7 synchronized nodes**:

```
[Webhook Receiver] ──► [Priority Router]
                             ├──► [Emergency Escalation Unit]  ──┐
                             └──► [Standard Department Routing] ──┴─► [Notify Responsible Department]
                                                                                │
[Respond to CampusCare Portal] ◄── [Acknowledge Student Grievance] ◄────────────┘
```

### Node-by-Node Explanation:

| # | Node Name | Type | Function |
| :- | :--- | :--- | :--- |
| **1** | **`Webhook Receiver`** | `n8n-nodes-base.webhook` | **Entry Gate**: Listens on `POST /webhook/campuscare-complaint`. Receives full ticket data from FastAPI backend (ticket ID, student name, email, department, priority, issue summary, recommended actions). |
| **2** | **`Priority Router`** | `n8n-nodes-base.switch` | **Conditional Triage**: Evaluates `{{ $json.body.priority }}`:<br>• Branches `0` & `1`: Routes `URGENT` and `HIGH` complaints to Emergency Escalation.<br>• Branches `2` & `3`: Routes `MEDIUM` and `LOW` complaints to Standard Dispatch. |
| **3** | **`Emergency Escalation Unit`** | `n8n-nodes-base.set` | **Urgent Metadata Setter**: Attaches `CRITICAL_ESCALATION_TRIGGERED` flag, marks ticket for immediate priority dispatch, and triggers SMS alert simulation. |
| **4** | **`Standard Department Routing`** | `n8n-nodes-base.set` | **Routine Metadata Setter**: Attaches standard SLA routing tags and schedules standard resolution milestones. |
| **5** | **`Notify Responsible Department`** | `n8n-nodes-base.httpRequest` | **Department Dispatcher**: Sends rich HTML alert containing Ticket ID, room location, student info, raw complaint, and AI suggested action to the department email configured in `departments.json`. |
| **6** | **`Acknowledge Student Grievance`** | `n8n-nodes-base.httpRequest` | **Student Receipt Dispatcher**: Sends official confirmation receipt to the student's email with Ticket ID, assigned department, and resolution timeline. |
| **7** | **`Respond to CampusCare Portal`** | `n8n-nodes-base.respondToWebhook` | **Feedback Loop**: Returns HTTP 200 JSON acknowledgement to the backend so Gradio displays: `Automation: Acknowledged by n8n workflow.` |

---

## 📧 6. Email Notification Architecture (Why Port 443 HTTPS?)

### The Network Challenge with Traditional SMTP:
Most consumer cellular providers (Jio, Airtel, Vi) and college Wi-Fi routers block raw outgoing TCP connections on **Port 465 (SMTPS)** and **Port 587 (STARTTLS)** to prevent spam bots. This frequently causes errors like:
```text
connect ENETUNREACH 2404:6800:4000:1025::6d:465
Error: connect ETIMEDOUT 192.178.211.108:587
```

### The CampusCare Solution:
CampusCare AI routes email dispatch over **HTTPS (Port 443)**, which is **never blocked by any network or firewall**:
1. **Google Apps Script Webhook (Default)**:
   - Uses your personal Gmail to deliver real emails to **ANY email address in the world**.
   - Zero configuration or API keys needed from departments.
2. **Resend REST API (Alternative)**:
   - High-speed cloud transactional email engine (`https://api.resend.com/emails`) delivering in under 0.5 seconds.

---

## 🏫 7. College Department Directory (`data/departments.json`)

All department data is dynamically maintained in `data/departments.json`:

| Department | Department Head | Contact Email | Office Location | SLA (Hours) |
| :--- | :--- | :--- | :--- | :---: |
| **IT Support** | Prof. K. Senthil | `dharaneeshc2006@gmail.com` | Central Computing Facility, Room 102 | 4h |
| **Electrical Maintenance** | Er. M. Murugan | `s.dharwinsangamani@gmail.com` | Estate Office, Substation Block | 6h |
| **Civil & Plumbing** | Er. P. Saravanan | `dharaneeshc2006@gmail.com` | Estate Office, Maintenance Yard | 8h |
| **Hostel Administration** | Dr. R. Selvam (Chief Warden) | `dharaneeshc2006@gmail.com` | Hostel Affairs Building, Block A | 12h |
| **Transport Department** | Mr. S. Thangaraj (Transport Officer) | `dharaneeshc2006@gmail.com` | Transport Desk, Gate 2 | 24h |
| **Library Administration** | Dr. P. Sundaram (Librarian) | `dharaneeshc2006@gmail.com` | Central Library, Ground Floor | 24h |
| **Canteen & Food Services** | Mr. K. Manickam | `dharaneeshc2006@gmail.com` | Student Activity Centre, Food Court | 12h |
| **General Administration** | Dr. V. Natarajan (Registrar) | `dharaneeshc2006@gmail.com` | Administrative Block, Room 10 | 48h |

> **Note**: To change any department email, simply modify the `"email"` field in `data/departments.json`. No code changes or restarts are required!

---

## 📂 8. Project Directory Structure

```text
campuscare_ai/
├── core/
│   ├── llm.py                 # Hugging Face LLM client + Resilient Heuristic Fallback Engine
│   ├── mcp_client.py          # Client adapter interfacing with the MCP Server
│   └── workflow.py            # LangGraph multi-agent state graph pipeline
├── data/
│   ├── complaints.json        # Persistent complaints database (Pure JSON)
│   └── departments.json       # College department directory & contacts (Pure JSON)
├── mcp_service/
│   └── server.py              # MCP Server exposing save_complaint, get_department_contact, etc.
├── n8n/
│   ├── campuscare_workflow_google_script.json  # n8n workflow for Google Webhook (Port 443)
│   ├── campuscare_workflow_resend.json         # n8n workflow for Resend HTTPS API (Port 443)
│   ├── campuscare_workflow_smtp.json           # n8n workflow for direct SMTP
│   └── mock_n8n_server.py                      # Standalone mock webhook simulator for offline testing
├── scripts/
│   └── update_wf.py           # Utility script to sync workflow settings into local n8n SQLite
├── tests/
│   ├── test_api.py            # FastAPI endpoint tests
│   ├── test_e2e.py            # End-to-end integration tests
│   ├── test_frontend.py       # Gradio UI integration tests
│   ├── test_integration.py    # Pipeline connectivity tests
│   ├── test_llm.py            # Classification & fallback unit tests
│   ├── test_mcp.py            # MCP server tool verification tests
│   └── test_workflow.py       # LangGraph state transitions tests
├── .env                       # Environment configuration (Tokens, Webhook URLs)
├── .env.example               # Example template for environment variables
├── frontend.py                # Standalone Gradio UI definition
├── main.py                    # FastAPI application & REST routing
├── requirements.txt           # Python dependency specifications
├── run_app.py                 # Unified runner (mounts Gradio inside FastAPI server)
└── README.md                  # Comprehensive Project Documentation
```

---

## 🚀 9. Quickstart: How to Run the Project

### Prerequisites
* Python 3.10+ (Recommended: Python 3.12)
* Node.js v18+ (for n8n)

### Step 1: Clone or Navigate to Project
```bash
cd /home/dharane/Documents/campuscare_ai
```

### Step 2: Set Up Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the root directory:
```bash
# Optional: Hugging Face Token (system automatically uses fallback engine if omitted)
HF_TOKEN=your_huggingface_token_here

# n8n Webhook URL
N8N_WEBHOOK_URL=http://localhost:5678/webhook/campuscare-complaint
```

### Step 4: Start the n8n Automation Engine
In a separate terminal tab:
```bash
npx n8n
```
* Open `http://localhost:5678` in your browser.
* Import [`n8n/campuscare_workflow_google_script.json`](file:///home/dharane/Documents/campuscare_ai/n8n/campuscare_workflow_google_script.json).
* Click **Publish** (toggle should turn green).

### Step 5: Launch the CampusCare Unified Server
In your main terminal:
```bash
source .venv/bin/activate
python run_app.py
```

### Access URLs:
* 🌐 **Gradio Web Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* 📑 **FastAPI Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* 💓 **Backend Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
* ⚙️ **n8n Automation Console**: [http://localhost:5678](http://localhost:5678)

---

## 🧪 10. Sample Test Scenarios

Copy and paste these exact examples into the Gradio portal to test each department:

### ⚡ Scenario 1: Electrical Emergency (`URGENT`)
* **Student Name**: `Dharaneesh`
* **Student Email**: `cdharaneesh05@gmail.com`
* **Department**: `CSE`
* **Complaint**: `Dangerous spark and burning smell from main switchboard in Room 302 near Block A.`
* **Expected Output**: Routed to `Electrical Maintenance` (`Er. M. Murugan`), priority `URGENT`. Dispatches alert to `s.dharwinsangamani@gmail.com`.

### 📶 Scenario 2: Lab Wi-Fi Down (`HIGH`)
* **Student Name**: `Dharaneesh`
* **Student Email**: `cdharaneesh05@gmail.com`
* **Department**: `AI&DS`
* **Complaint**: `Campus Wi-Fi is disconnected in Lab 2 and our online coding test is scheduled tomorrow.`
* **Expected Output**: Routed to `IT Support` (`Prof. K. Senthil`), priority `HIGH`.

### 🚌 Scenario 3: College Bus Breakdown (`HIGH`)
* **Student Name**: `Dharaneesh`
* **Student Email**: `cdharaneesh05@gmail.com`
* **Department**: `Mech`
* **Complaint**: `Route 12 college bus driver did not arrive at Bus Stop and students are waiting today.`
* **Expected Output**: Routed to `Transport Department` (`Mr. S. Thangaraj`), priority `HIGH`.

### 🚰 Scenario 4: Bathroom Water Leak (`URGENT`)
* **Student Name**: `Dharaneesh`
* **Student Email**: `cdharaneesh05@gmail.com`
* **Department**: `Civil`
* **Complaint**: `Water tap leaking heavily and 2nd floor bathroom is flooded.`
* **Expected Output**: Routed to `Civil & Plumbing Maintenance` (`Er. P. Saravanan`), priority `URGENT`.

### 🏢 Scenario 5: Hostel Door Lock (`HIGH`)
* **Student Name**: `Dharaneesh`
* **Student Email**: `cdharaneesh05@gmail.com`
* **Department**: `ECE`
* **Complaint**: `Hostel Block A room 105 door lock is broken and warden office is closed.`
* **Expected Output**: Routed to `Hostel Administration` (`Dr. R. Selvam`), priority `HIGH`.

### 📚 Scenario 6: Library Overdue Fine Issue (`MEDIUM`)
* **Student Name**: `Dharaneesh`
* **Student Email**: `cdharaneesh05@gmail.com`
* **Department**: `IT`
* **Complaint**: `Reference book missing and overdue fine showing erroneously in Central Library.`
* **Expected Output**: Routed to `Library Administration` (`Dr. P. Sundaram`), priority `MEDIUM`.

### 🍲 Scenario 7: Canteen Food Hygiene (`HIGH`)
* **Student Name**: `Dharaneesh`
* **Student Email**: `cdharaneesh05@gmail.com`
* **Department**: `CSE`
* **Complaint**: `Uncooked food and cold meal served in college canteen today.`
* **Expected Output**: Routed to `Canteen & Food Services` (`Mr. K. Manickam`), priority `HIGH`.

---

## 🧪 11. Automated Test Suite

CampusCare AI includes a test suite covering LLM fallback, LangGraph state machine, MCP servers, REST APIs, and UI:

```bash
# Run all automated unit and integration tests
pytest tests/ -v
```

### Test Coverage:
* `tests/test_llm.py`: Keyword extraction, priority detection, and fallback resilience.
* `tests/test_workflow.py`: LangGraph multi-agent state transitions.
* `tests/test_mcp.py`: MCP tool registration and JSON persistence.
* `tests/test_api.py`: FastAPI `/health`, `/departments`, `/analyze`, and `/complaint` endpoints.
* `tests/test_frontend.py`: Gradio layout and prediction callbacks.
* `tests/test_e2e.py`: Complete submission $\to$ Agentic AI $\to$ MCP $\to$ n8n pipeline.

