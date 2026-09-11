"""
Independent Test for Gradio Frontend logic.
Verifies the process_complaint_ui handler:
- Input validation (empty text handled)
- AI Analysis extraction
- Priority & department routing
- Status generation
"""

import sys
import os

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend import process_complaint_ui


def test_gradio_ui_logic():
    print("=" * 70)
    print("Testing CampusCare AI - Gradio Frontend Interface Logic")
    print("=" * 70)

    # 1. Test empty complaint validation
    print("\n[1. Testing Empty Input Handling]")
    err_res = process_complaint_ui("Arun", "arun@example.edu", "CSE", "")
    print(f"Empty Complaint Output: {err_res[0]} | {err_res[4]}")
    assert "Error" in err_res[0]

    # 2. Test valid complaint submission
    print("\n[2. Testing Real Complaint Processing]")
    category, priority, department, location, summary, response, status = process_complaint_ui(
        student_name="Arun Kumar",
        student_email="arun@example.edu",
        class_dept="CSE",
        complaint_text="The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."
    )

    print("-" * 70)
    print(f"Category:          {category}")
    print(f"Priority:          {priority}")
    print(f"Department:        {department}")
    print(f"Location:          {location}")
    print(f"Summary:           {summary}")
    print(f"Student Response:  {response}")
    print(f"Automation Status: {status}")
    print("-" * 70)

    assert category == "Wi-Fi / Network"
    assert priority in ["HIGH", "URGENT"]
    assert department == "IT Support"
    assert "Lab 3" in location
    assert len(response) > 15
    assert len(status) > 10

    print("\n[Gradio Frontend Independent Test Passed Successfully!]")
    print("=" * 70)


if __name__ == "__main__":
    test_gradio_ui_logic()
