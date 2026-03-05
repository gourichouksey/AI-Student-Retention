import os
import random
import pandas as pd

random.seed(42)

def gen_student():
    attendance = random.randint(40, 100)
    backlogs = random.randint(0, 6)
    family_income = random.randint(50000, 800000)
    parents_edu = random.choice(["none", "school", "college", "postgrad"])
    scholarship = random.choice(["yes", "no"])

    grade_math = random.randint(30, 100)
    grade_science = random.randint(30, 100)
    grade_english = random.randint(30, 100)

    risk_factor = 0
    if attendance < 60:
        risk_factor += 0.3
    if backlogs > 2:
        risk_factor += 0.2
    if family_income < 150000 and scholarship == "no":
        risk_factor += 0.2
    if min(grade_math, grade_science, grade_english) < 45:
        risk_factor += 0.2

    dropout = 1 if random.random() < risk_factor else 0

    return {
        "attendance_pct": attendance,
        "backlogs": backlogs,
        "family_income": family_income,
        "parents_edu": parents_edu,
        "scholarship_status": scholarship,
        "grade_math": grade_math,
        "grade_science": grade_science,
        "grade_english": grade_english,
        "dropout": dropout,
    }


def main():
    data = [gen_student() for _ in range(1200)]
    df = pd.DataFrame(data)
    out_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
    df.to_csv(out_path, index=False)
    print("dataset.csv generated at", out_path)


if __name__ == "__main__":
    main()
