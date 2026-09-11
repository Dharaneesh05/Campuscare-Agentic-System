"""
CampusCare AI - Unified Application Launcher.
Mounts the Gradio Student Portal directly onto the FastAPI Backend,
providing a single command to run the complete system:
  - Web UI:      http://127.0.0.1:8000/
  - API Docs:    http://127.0.0.1:8000/docs
  - Healthcheck: http://127.0.0.1:8000/health
  - Endpoints:   http://127.0.0.1:8000/complaint
"""

import uvicorn
import gradio as gr
from main import app as fastapi_app
from frontend import demo as gradio_demo, custom_css

# Mount Gradio interface onto the FastAPI app
# Accessible at the root URL http://127.0.0.1:8000/
app = gr.mount_gradio_app(
    app=fastapi_app,
    blocks=gradio_demo,
    path="/"
)

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting CampusCare AI System...")
    print("👉 Gradio Web Portal:  http://127.0.0.1:8000/")
    print("👉 FastAPI Swagger UI: http://127.0.0.1:8000/docs")
    print("👉 Backend Healthcheck: http://127.0.0.1:8000/health")
    print("=" * 70)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
