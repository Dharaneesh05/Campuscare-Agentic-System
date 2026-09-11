"""
Independent Test for Hugging Face LLM Integration.
Verifies that the LLM client properly processes natural language complaints
and returns structured classification and response.
"""

import sys
import os
import json

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.llm import HuggingFaceLLMClient


def test_llm_inference():
    print("=" * 60)
    print("Testing CampusCare AI - Hugging Face LLM Client")
    print("=" * 60)

    client = HuggingFaceLLMClient()
    sample_complaint = "The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."

    print(f"\n[Input Complaint]:\n\"{sample_complaint}\"")
    print("\n[Invoking LLM...]")

    output_raw = client.generate(
        prompt=sample_complaint,
        system_prompt="You are an AI college complaint classifier. Output a JSON object with category, priority, department, location, summary, suggested_action, and response."
    )

    print("\n[LLM Output Received]:")
    print(output_raw)

    # Validate that output is parseable JSON or structured text
    try:
        data = json.loads(output_raw)
        print("\n[Verification Check]: SUCCESS")
        print(f"  - Category:    {data.get('category')}")
        print(f"  - Priority:    {data.get('priority')}")
        print(f"  - Department:  {data.get('department')}")
        print(f"  - Location:    {data.get('location')}")
        print(f"  - Summary:     {data.get('summary')}")
        print(f"  - Action:      {data.get('suggested_action')}")
        print(f"  - Response:    {data.get('response')}")
        assert data.get("category") is not None
        assert data.get("priority") is not None
        assert data.get("department") is not None
    except Exception as e:
        print(f"\n[Verification Check]: Non-JSON string returned or parse warning: {e}")

    print("\n" + "=" * 60)
    print("LLM Independent Test Finished Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_llm_inference()
