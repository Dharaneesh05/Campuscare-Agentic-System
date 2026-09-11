#!/usr/bin/env python3
"""
CampusCare AI - Unified Application Launcher.
Mounts the Gradio Student Portal directly onto the FastAPI Backend,
providing a single command to run the complete system:
  - Web UI:      http://127.0.0.1:8000/
  - API Docs:    http://127.0.0.1:8000/docs
  - Healthcheck: http://127.0.0.1:8000/health
  - Endpoints:   http://127.0.0.1:8000/complaint
"""

import os
import sys

# Dynamically add matching site-packages for the current running Python version
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PY_VER = f"python{sys.version_info.major}.{sys.version_info.minor}"
VENV_PACKAGES = os.path.join(CURRENT_DIR, ".venv", "lib", PY_VER, "site-packages")
if os.path.exists(VENV_PACKAGES) and VENV_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_PACKAGES)

try:
    import uvicorn
    import gradio as gr
    from main import app as fastapi_app
    from frontend import demo as gradio_demo
except ImportError as e:
    print("\n" + "=" * 60)
    print("⚠️ Missing Dependencies for this Python version!")
    print(f"Current Python: {sys.executable} (Version {sys.version.split()[0]})")
    print(f"Error details: {e}")
    print("\nPlease run this command to install dependencies for your terminal:")
    print("  python3 -m pip install -r requirements.txt")
    print("=" * 60 + "\n")
    sys.exit(1)

# Mount Gradio interface onto FastAPI root
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
