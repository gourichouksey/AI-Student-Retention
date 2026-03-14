# pyright: ignore

import os
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.models import Scholarship


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "training",
    "artifacts",
    "eligibility_model.pkl",
)


def _student_avg_marks(student: Dict[str, Any]) -> float:
    vals = []
    for k in ("grade_math", "grade_science", "grade_english"):
        if k in student and student[k] is not None:
            vals.append(float(student[k]))
    if not vals:
        return float("nan")
    return float(sum(vals) / len(vals))


def _features(student: Dict[str, Any], sch: Scholarship) -> np.ndarray:
    income = float(student.get("family_income", np.nan))
    avg = _student_avg_marks(student)

    income_delta = float(sch.income_limit) - income
    marks_delta = avg - float(sch.min_marks_required)

    # Also include raw values so the model can learn scale.
    return np.array(
        [
            income,
            avg,
            float(sch.income_limit),
            float(sch.min_marks_required),
            income_delta,
            marks_delta,
        ],
        dtype=float,
    )


def _generate_training_data() -> Tuple[np.ndarray, np.ndarray]:
    scholarships = Scholarship.query.all()
    if not scholarships:
        raise RuntimeError("No scholarships found in DB to train eligibility model")

    rng = np.random.default_rng(42)
    X_rows: List[np.ndarray] = []
    y_rows: List[int] = []

    # Synthetic training: sample students around each scholarship's thresholds.
    for sch in scholarships:
        income_limit = float(sch.income_limit)
        min_marks = float(sch.min_marks_required)

        for _ in range(120):
            income = float(rng.normal(loc=income_limit, scale=max(20000.0, income_limit * 0.15)))
            income = max(0.0, income)

            avg = float(rng.normal(loc=min_marks, scale=12.0))
            avg = float(np.clip(avg, 0.0, 100.0))

            # Build a fake student dict.
            student = {
                "family_income": income,
                "grade_math": avg,
                "grade_science": avg,
                "grade_english": avg,
            }

            feats = _features(student, sch)
            eligible = 1 if (income <= income_limit and avg >= min_marks) else 0

            X_rows.append(feats)
            y_rows.append(eligible)

    X = np.vstack(X_rows)
    y = np.array(y_rows, dtype=int)
    return X, y


def train_or_load_model() -> Pipeline:
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)

    X, y = _generate_training_data()

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model


def predict_eligibility_probability(student: Dict[str, Any], sch: Scholarship) -> float:
    model = train_or_load_model()
    x = _features(student, sch).reshape(1, -1)
    proba = float(model.predict_proba(x)[0][1])
    return proba


def recommend_scholarships_ml(student: Dict[str, Any], *, limit: int = 5) -> List[Dict[str, Any]]:
    scholarships = Scholarship.query.all()
    if not scholarships:
        return []

    avg = _student_avg_marks(student)
    income = student.get("family_income")
    try:
        income_f = float(income)
    except Exception:
        income_f = float("nan")

    ranked: List[Dict[str, Any]] = []
    for sch in scholarships:
        proba = predict_eligibility_probability(student, sch)
        # Hard-criteria eligibility (explainable check)
        hard_ok = True
        if not np.isnan(income_f) and income_f > float(sch.income_limit):
            hard_ok = False
        if not np.isnan(avg) and avg < float(sch.min_marks_required):
            hard_ok = False

        ranked.append(
            {
                "scholarship_id": sch.scholarship_id,
                "scholarship_name": sch.scholarship_name,
                "provider": sch.provider,
                "category": sch.category,
                "education_level": sch.education_level,
                "min_marks_required": float(sch.min_marks_required),
                "income_limit": float(sch.income_limit),
                "scholarship_amount": float(sch.scholarship_amount),
                "state": sch.state,
                "deadline": sch.deadline.isoformat(),
                "application_mode": sch.application_mode,
                "eligibility_probability": proba,
                "eligible": bool(hard_ok),
            }
        )

    ranked.sort(key=lambda r: (r["eligibility_probability"], r["scholarship_amount"]), reverse=True)
    return ranked[: int(limit)]
