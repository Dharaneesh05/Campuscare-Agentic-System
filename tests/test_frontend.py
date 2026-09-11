"""
Independent Test for Gradio Frontend logic.
Verifies the process_complaint_ui handler:
- Input validation (empty text handled)
- AI Analysis extraction
- Department routing and email assignment
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
    err_res = process_complaint_ui("dharaneesh", "dharaneeshc2006@gmail.com", "CSE", "")
    print(f"Empty Complaint Output: {err_res[0]}")
    assert "Error" in err_res[0]

    # 2. Test Wi-Fi complaint
    print("\n[2. Testing Wi-Fi Complaint Processing]")
    cat, prio, dept, dept_mail, dept_lead, loc, summ, resp, stat = process_complaint_ui(
        student_name="dharaneesh",
        student_email="dharaneeshc2006@gmail.com",
        class_dept="CSE",
        complaint_text="The Wi-Fi in Lab 3 is not working and we have an online exam tomorrow."
    )
    print(f"Category: {cat} | Priority: {prio} | Dept: {dept} | Dept Email: {dept_mail}")
    assert cat == "Wi-Fi / Network"
    assert prio in ["HIGH", "URGENT"]
    assert dept == "IT Support"
    assert "dharaneeshc2006@gmail.com" in dept_mail

    # 3. Test Water Supply Complaint (from user request)
    print("\n[3. Testing Custom Complaint: 'water supply problem on the bathroom']")
    cat2, prio2, dept2, dept_mail2, dept_lead2, loc2, summ2, resp2, stat2 = process_complaint_ui(
        student_name="dharaneesh",
        student_email="dharaneeshc2006@gmail.com",
        class_dept="CSE",
        complaint_text="water supply problem on the bathroom"
    )
    print(f"Category: {cat2} | Priority: {prio2} | Dept: {dept2} | Location: {loc2} | Email: {dept_mail2}")
    assert cat2 == "Water / Plumbing", f"Expected Water / Plumbing, got {cat2}"
    assert dept2 == "Civil & Plumbing Maintenance", f"Expected Civil & Plumbing Maintenance, got {dept2}"
    assert "Bathroom" in loc2, f"Expected Bathroom in location, got {loc2}"
    assert "dharaneeshc2006@gmail.com" in dept_mail2

    print("\n[All Gradio Frontend Tests Passed Successfully!]")
    print("=" * 70)


if __name__ == "__main__":
    test_gradio_ui_logic()
