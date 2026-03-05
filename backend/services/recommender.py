def generate_recommendations(data, risk_score):
    recs = []

    if data["family_income"] < 200000 and data["scholarship_status"].lower() == "no":
        recs.append("Scholarship recommendation (financial support).")

    if data["attendance_pct"] < 70:
        recs.append("Parent meeting due to attendance issues.")

    low_grades = [v for k, v in data.items() if k.startswith("grade_") and v < 50]
    if low_grades or data["backlogs"] > 0:
        recs.append("Enroll in remedial classes for academic improvement.")

    if risk_score > 0.7:
        recs.append("Schedule counselor intervention within 1 week.")

    return recs
