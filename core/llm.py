"""
Hugging Face LLM Client for CampusCare AI
Handles communication with Hugging Face Inference API with an intelligent local fallback.
"""

import os
import re
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CampusCare.LLM")


class HuggingFaceLLMClient:
    def __init__(self, token: Optional[str] = None, model: Optional[str] = None):
        self.token = token or os.getenv("HF_TOKEN")
        self.model = model or os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initializes the Hugging Face InferenceClient if a token is present."""
        if self.token and self.token.strip() and self.token != "your_huggingface_token_here":
            try:
                from huggingface_hub import InferenceClient
                self.client = InferenceClient(model=self.model, token=self.token)
                logger.info(f"Hugging Face InferenceClient initialized for model: {self.model}")
            except Exception as e:
                logger.warning(f"Could not initialize HF client: {e}. Fallback engine will be used.")
                self.client = None
        else:
            logger.info("No valid HF_TOKEN found in environment. Using resilient heuristic fallback engine.")
            self.client = None

    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_new_tokens: int = 512, temperature: float = 0.2) -> str:
        """
        Generates text using the Hugging Face Inference API, or falls back gracefully
        if the API is unavailable, offline, or rate-limited.
        """
        if self.client:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat_completion(
                    messages=messages,
                    max_tokens=max_new_tokens,
                    temperature=temperature
                )
                generated_text = response.choices[0].message.content
                logger.info("Successfully received generation from Hugging Face Inference API.")
                return generated_text.strip()
            except Exception as e:
                logger.warning(f"Hugging Face API call failed ({e}). Utilizing fallback engine.")

        return self._heuristic_fallback(prompt, system_prompt)

    def _heuristic_fallback(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Deterministic, rule-based fallback that parses complaint text to ensure
        the pipeline runs reliably even without internet or when HF rate limits hit.
        """
        # Extract only the actual complaint text so prompt instruction keywords do not cause false positives
        match = re.search(r'Complaint:\s*["\'](.*?)["\']', prompt, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1).lower()
        else:
            # Strip prompt template text before analyzing
            clean_prompt = prompt.split("Return a JSON")[0].split("e.g.")[0]
            text = clean_prompt.lower()

        # Category & Department Detection
        if any(w in text for w in ["canteen", "food", "hygiene", "meal", "snack"]):
            category = "Canteen / Food"
            department = "Canteen & Food Services"
            action = "Report to Canteen Inspection Committee."
        elif any(w in text for w in ["hostel", "warden", "curfew", "dorm", "hostel room", "mess hall", "bed"]):
            category = "Hostel Maintenance"
            department = "Hostel Administration"
            action = "Notify Hostel Warden office."
        elif any(w in text for w in ["bus", "transport", "driver", "route", "van"]):
            category = "Transport"
            department = "Transport Department"
            action = "Escalate to Transport Supervisor."
        elif any(w in text for w in ["library", "book", "id card", "fine", "journal"]):
            category = "Library Services"
            department = "Library Administration"
            action = "Contact Chief Librarian."
        elif any(w in text for w in ["projector", "screen", "mic", "speaker", "audio", "display"]):
            category = "Classroom AV / Projector"
            department = "IT Support"
            action = "Dispatch AV technician to inspect the classroom."
        elif any(w in text for w in ["wi-fi", "wifi", "internet", "lan", "network", "router", "connection"]):
            category = "Wi-Fi / Network"
            department = "IT Support"
            action = "Immediately notify IT Support network administrator."
        elif any(w in text for w in ["computer", "monitor", "keyboard", "mouse", "desktop", "software", "windows", "linux"]) or re.search(r"\b(pc|os)\b", text):
            category = "Lab Computers / Software"
            department = "IT Support"
            action = "Assign lab technician to repair system."
        elif any(w in text for w in ["electricity", "light", "fan", "power", "switch", "plug", "socket", "blackout", "wiring", "spark"]):
            category = "Electricity / Power"
            department = "Electrical Maintenance"
            action = "Alert campus electrician on duty."
        elif any(w in text for w in ["water", "tap", "leak", "pipe", "toilet", "washroom", "bathroom", "restroom", "flush", "drain", "plumbing", "sewage", "supply"]):
            category = "Water / Plumbing"
            department = "Civil & Plumbing Maintenance"
            action = "Dispatch emergency plumbing staff to inspect and fix the supply."
        else:
            category = "General Campus Infrastructure"
            department = "General Administration"
            action = "Forward ticket to Administrative Desk."

        urgency_markers = ["exam", "test", "urgent", "emergency", "immediately", "tomorrow", "dangerous", "spark", "flood", "now"]
        high_markers = ["today", "broken", "critical", "assignment", "presentation", "problem", "leak"]

        if any(marker in text for marker in urgency_markers):
            priority = "URGENT" if any(m in text for m in ["spark", "flood", "danger", "hazard"]) else "HIGH"
        elif any(marker in text for marker in high_markers):
            priority = "HIGH"
        else:
            priority = "MEDIUM"

        location = "Campus Facility"
        loc_patterns = [
            r"(?:in|at|on|near)\s+(?:the\s+)?([A-Za-z0-9\s]+(?:lab\s*\d+|room\s*\d+|block\s*[A-Za-z0-9]+|hostel\s*[A-Za-z0-9]+|hall\s*\d+|library|canteen|bathroom|washroom|restroom))",
            r"\b(lab\s*\d+|room\s*\d+|block\s*[a-z0-9]+|hostel\s*[a-z0-9]+|bathroom|washroom|restroom|canteen|library)\b"
        ]
        for pattern in loc_patterns:
            match_loc = re.search(pattern, text, re.IGNORECASE)
            if match_loc:
                location = match_loc.group(1).strip().title()
                break

        summary = f"Issue concerning {category.lower()} reported at {location}."
        if "exam" in text:
            summary += " Urgent attention requested due to impending examinations."

        response = (
            f"Dear Student, thank you for reporting the issue regarding '{category}' at {location}. "
            f"Your complaint has been logged and assigned {priority} priority. "
            f"It has been routed directly to the {department} for swift resolution."
        )

        return json.dumps({
            "category": category,
            "priority": priority,
            "department": department,
            "location": location,
            "summary": summary,
            "suggested_action": action,
            "response": response
        }, indent=2)


llm_client = HuggingFaceLLMClient()
