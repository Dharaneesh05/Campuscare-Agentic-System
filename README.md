# CampusCare AI
### An Agentic AI-Based College Complaint Classification & Automated Resolution System

## 1. Project Overview

**CampusCare AI** is an intelligent, agentic grievance management system designed for educational institutions. In traditional colleges, student complaints regarding lab computers, power cuts, plumbing leaks, bus delays, hostel issues, or canteen food are often delayed due to manual paper forms, misrouting, and slow communication.

CampusCare AI solves this by introducing an autonomous **Multi-Agent AI Pipeline**:
1. Students submit complaints through a clean, modern **Gradio Web Portal**.
2. **LangGraph Multi-Agent Orchestrator** analyzes the complaint text, determines severity and SLA, identifies the specific college location, and routes it to the exact responsible department.
3. **Model Context Protocol (MCP)** tools record the ticket and format official notifications.
4. **n8n Automation Engine** coordinates the resolution workflow, triggers emergency escalation paths, and dispatches real-time HTML notifications directly to:
   - **The Department Lead** (for immediate field resolution).
   - **The Student** (official registration receipt and SLA timeline).
5. All records persist strictly in lightweight, human-readable **Pure JSON files** (zero external SQL/NoSQL/Vector databases required).

---

## 2. System Architecture

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
          │  Department Alert  |  Student Ack │
          └─────────────────────────────────────────┘
```

---

## 3. Tech Stack & Engineering Constraints

* **Frontend**: [Gradio](https://www.gradio.app/) — Mounted cleanly onto FastAPI root, providing an intuitive dual-panel interface (Submission Form on left, Real-time Resolution Card on right).
* **Backend**: [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn — High-performance asynchronous REST API.
* **Agentic Framework**: [LangGraph](https://python.langchain.com/docs/langgraph/) — Stateful multi-agent graph directing analysis from raw text to structured ticket.
* **LLM Engine**: Hugging Face Inference API (`router.huggingface.co`) + **Resilient Heuristic Fallback Engine** (guarantees 100% uptime even without cloud API credits or during network drops).
* **Tool Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — Decoupled tool layer for saving complaints and fetching department contacts.
* **Automation Workflow**: [n8n](https://n8n.io/) — Self-hosted automation platform for conditional routing, SLA tracking, and email dispatch.
* **Storage Constraint**: **Pure JSON Only** (`data/complaints.json` and `data/departments.json`). Strictly NO SQLite, PostgreSQL, MongoDB, Redis, or Vector Databases.
* **Email Protocol**: Modern **HTTPS Webhook API (Port 443)** using Google Apps Script / Resend, completely avoiding blocked legacy SMTP ports (`465`/`587`).

---

## 4. LangGraph Multi-Agent Pipeline

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
     - **URGENT**: Immediate hazards (sparks, floods, fire, gas, structural dangers).
     - **HIGH**: Critical academic blockers (exam tomorrow, lab test today, presentation).
     - **MEDIUM / LOW**: Routine maintenance and non-urgent repairs.
3. **Agent 3: Department Router**
   - Queries `data/departments.json` via MCP tools.
   - Matches the issue to the responsible college department and assigns the department head and contact info.
4. **Agent 4: Response Generator**
   - Drafts an empathetic, official acknowledgement message to the student detailing the resolution procedure and committed SLA.
5. **Agent 5: Action Decider & MCP Dispatcher**
   - Calls MCP tools to generate ticket IDs, persists the ticket into `data/complaints.json`, prepares dispatch payloads, and triggers n8n.

---

### Test Coverage:
* `tests/test_llm.py`: Keyword extraction, priority detection, and fallback resilience.
* `tests/test_workflow.py`: LangGraph multi-agent state transitions.
* `tests/test_mcp.py`: MCP tool registration and JSON persistence.
* `tests/test_api.py`: FastAPI `/health`, `/departments`, `/analyze`, and `/complaint` endpoints.
* `tests/test_frontend.py`: Gradio layout and prediction callbacks.
* `tests/test_e2e.py`: Complete submission $\to$ Agentic AI $\to$ MCP $\to$ n8n pipeline.

