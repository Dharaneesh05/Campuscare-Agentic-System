"""
Independent Test for LangGraph Multi-Agent Workflow.
Verifies state transitions through:
  Analyzer Agent -> Priority Agent -> Routing Agent -> Response Agent -> Action Decider
"""

import sys
import os
import json

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.workflow import complaint_workflow


def test_langgraph_pipeline():
    print("=" * 70)
    print("Testing CampusCare AI - LangGraph Multi-Agent Workflow")
    print("=" * 70)

    initial_input = {
        "student_name": "Arun Kumar",
        "student_email": "arun@example.edu",
        "class_department": "CSE",
        "complaint": "The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."
    }

    print(f"\n[Student Input]:")
    print(f"  Name:       {initial_input['student_name']}")
    print(f"  Email:      {initial_input['student_email']}")
    print(f"  Dept:       {initial_input['class_department']}")
    print(f"  Complaint:  \"{initial_input['complaint']}\"")

    print("\n[Executing LangGraph Agent Graph...]")
    final_state = complaint_workflow.invoke(initial_input)

    print("\n[LangGraph Execution Completed! Final State Content]:")
    print("-" * 70)
    print(f"1. Category:          {final_state.get('category')}")
    print(f"2. Location:          {final_state.get('location')}")
    print(f"3. Summary:           {final_state.get('summary')}")
    print(f"4. Priority:          {final_state.get('priority')}")
    print(f"5. Urgency Reason:    {final_state.get('urgency_reason')}")
    print(f"6. Department:        {final_state.get('department')}")
    print(f"7. Suggested Action:  {final_state.get('suggested_action')}")
    print(f"8. Department Email:  {final_state.get('department_contact', {}).get('email')}")
    print(f"9. Response Generated:{final_state.get('response')}")
    print(f"10. Tool Action:      {final_state.get('tool_action')}")
    print(f"11. Pipeline Status:  {final_state.get('status')}")
    print("-" * 70)

    assert final_state.get("category") == "Wi-Fi / Network"
    assert final_state.get("priority") in ["HIGH", "URGENT"]
    assert final_state.get("department") == "IT Support"
    assert "Lab 3" in final_state.get("location", "")
    assert len(final_state.get("response", "")) > 10

    print("\n[All LangGraph Agent Assertions Passed Successfully!]")
    print("=" * 70)


if __name__ == "__main__":
    test_langgraph_pipeline()
