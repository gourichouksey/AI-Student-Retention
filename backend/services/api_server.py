from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

try:
    from .predictor import predict_risk
except Exception:
    try:
        from predictor import predict_risk
    except Exception:
        predict_risk = None

try:
    from .shap_explain import explain_student
except Exception:
    try:
        from shap_explain import explain_student
    except Exception:
        explain_student = None


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_cors_origins(value: str | None) -> list[str] | None:
    if value is None or not value.strip() or value.strip() == "*":
        return None
    return [origin.strip() for origin in value.split(",") if origin.strip()]


app = Flask(__name__)
cors_origins = _parse_cors_origins(os.getenv("CORS_ORIGINS"))
if cors_origins:
    CORS(app, resources={r"/*": {"origins": cors_origins}})
else:
    CORS(app)


USERS: list[dict[str, Any]] = []
ACTIONS: list[dict[str, Any]] = []
RISK_LOG: list[dict[str, Any]] = []


DEFAULT_SCHOLARSHIPS = [
    {
        "scholarship_id": "NSP-01",
        "scholarship_name": "National Scholarship Portal",
        "provider": "Government of India",
        "state": "All India",
        "scholarship_amount": "₹10,000 - ₹50,000",
        "deadline": "2026-09-30",
    },
    {
        "scholarship_id": "MP-02",
        "scholarship_name": "MP State Scholarship",
        "provider": "Madhya Pradesh Govt",
        "state": "Madhya Pradesh",
        "scholarship_amount": "₹8,000 - ₹30,000",
        "deadline": "2026-10-15",
    },
    {
        "scholarship_id": "AICTE-03",
        "scholarship_name": "AICTE Pragati (Women)",
        "provider": "AICTE",
        "state": "All India",
        "scholarship_amount": "₹50,000",
        "deadline": "2026-08-31",
    },
]


def _safe_number(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return fallback


def _heuristic_risk(payload: dict[str, Any]) -> float:
    attendance = _safe_number(payload.get("attendance_pct"), 60)
    backlogs = _safe_number(payload.get("backlogs"), 0)
    grade_math = _safe_number(payload.get("grade_math"), 60)
    grade_science = _safe_number(payload.get("grade_science"), 60)
    grade_english = _safe_number(payload.get("grade_english"), 60)

    avg_grade = (grade_math + grade_science + grade_english) / 3
    risk = 0.15
    risk += max(0, (75 - attendance) / 100)
    risk += min(backlogs, 6) * 0.06
    risk += max(0, (55 - avg_grade) / 120)
    return max(0.01, min(0.99, risk))


def _derive_recommendations(payload: dict[str, Any], risk_probability: float) -> list[str]:
    recs: list[str] = []

    if _safe_number(payload.get("attendance_pct"), 100) < 70:
        recs.append("Start attendance counseling with weekly follow-up")
    if _safe_number(payload.get("backlogs"), 0) >= 2:
        recs.append("Assign remedial plan for backlog subjects")
    if _safe_number(payload.get("family_income"), 9999999) < 250000:
        recs.append("Check scholarship eligibility and fee support")
    avg = (
        _safe_number(payload.get("grade_math"), 60)
        + _safe_number(payload.get("grade_science"), 60)
        + _safe_number(payload.get("grade_english"), 60)
    ) / 3
    if avg < 55:
        recs.append("Add tutor support for low-performing subjects")

    if risk_probability >= 0.7:
        recs.insert(0, "Urgent mentor meeting within 48 hours")
    elif risk_probability >= 0.4:
        recs.insert(0, "Schedule advisor check-in this week")

    if not recs:
        recs = ["Continue regular monitoring and monthly review"]
    return recs


def _build_scholarships(payload: dict[str, Any]) -> list[dict[str, Any]]:
    income = _safe_number(payload.get("family_income"), 0)
    avg = (
        _safe_number(payload.get("grade_math"), 60)
        + _safe_number(payload.get("grade_science"), 60)
        + _safe_number(payload.get("grade_english"), 60)
    ) / 3

    scholarships = []
    for item in DEFAULT_SCHOLARSHIPS:
        income_score = 1.0 if income <= 250000 else 0.55 if income <= 500000 else 0.25
        marks_score = min(1.0, max(0.0, avg / 100.0))
        prob = round(0.65 * income_score + 0.35 * marks_score, 3)

        scholarships.append(
            {
                **item,
                "eligible": prob >= 0.5,
                "eligibility_probability": prob,
            }
        )

    scholarships.sort(key=lambda x: x["eligibility_probability"], reverse=True)
    return scholarships


def _predict_probability(payload: dict[str, Any]) -> float:
    if predict_risk is None:
        return _heuristic_risk(payload)
    try:
        probability = float(predict_risk(payload))
        return max(0.0, min(1.0, probability))
    except Exception:
        return _heuristic_risk(payload)


def _explain(payload: dict[str, Any]) -> dict[str, Any]:
    if explain_student is None:
        return {"top_features": []}
    try:
        data = explain_student(payload)
        if isinstance(data, dict) and "top_features" in data:
            return data
        return {"top_features": []}
    except Exception:
        return {"top_features": []}


@app.get("/health")
def health() -> Any:
    return jsonify({"ok": True, "service": "student-retention-api"})


@app.post("/predict")
def predict() -> Any:
    payload = request.get_json(silent=True) or {}
    probability = _predict_probability(payload)
    student_id = payload.get("student_id", "unknown")

    RISK_LOG.append(
        {
            "student_id": student_id,
            "risk": probability,
            "ts": datetime.utcnow().isoformat(),
        }
    )

    response = {
        "student_id": student_id,
        "risk_score": probability,
        "risk_level": "High" if probability >= 0.7 else "Medium" if probability >= 0.4 else "Low",
        "explanation": _explain(payload),
        "recommendations": _derive_recommendations(payload, probability),
        "scholarships": _build_scholarships(payload),
    }
    return jsonify(response)


@app.get("/students/high-risk")
def high_risk_students() -> Any:
    latest_by_student: dict[str, dict[str, Any]] = {}
    for row in RISK_LOG:
        latest_by_student[str(row["student_id"])] = row

    rows = [
        {
            "student_id": item["student_id"],
            "risk": item["risk"],
        }
        for item in latest_by_student.values()
        if item.get("risk", 0) >= 0.4
    ]
    rows.sort(key=lambda x: x["risk"], reverse=True)
    return jsonify({"students": rows[:20]})


@app.get("/monitoring")
def monitoring() -> Any:
    return jsonify({"actions": ACTIONS})


@app.post("/actions")
def create_action() -> Any:
    payload = request.get_json(silent=True) or {}
    action = {
        "student_id": payload.get("student_id", "unknown"),
        "action": payload.get("action", "Follow-up"),
        "status": payload.get("status", "Planned"),
        "outcome": payload.get("outcome", ""),
    }
    ACTIONS.append(action)
    return jsonify({"ok": True, "action": action})


@app.post("/auth/signup")
def signup() -> Any:
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    if not email:
        return jsonify({"error": "Email is required"}), 400

    existing = next((u for u in USERS if u["email"] == email), None)
    if existing:
        return jsonify({"error": "User already exists"}), 409

    user = {
        "name": payload.get("name") or "Student",
        "email": email,
    }
    USERS.append(user)
    return jsonify(user)


@app.post("/auth/login")
def login() -> Any:
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = next((u for u in USERS if u["email"] == email), None)
    if user is None:
        user = {"name": payload.get("name") or "Demo User", "email": email}
        USERS.append(user)
    return jsonify(user)


@app.post("/auth/google")
def auth_google() -> Any:
    payload = request.get_json(silent=True) or {}
    token = payload.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    return jsonify({"name": "Google User", "email": "google-user@example.com"})


@app.post("/chat")
def chat() -> Any:
    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages") or []
    last = ""
    if isinstance(messages, list) and messages:
        last_msg = messages[-1]
        if isinstance(last_msg, dict):
            last = str(last_msg.get("text", "")).lower()

    if "scholarship" in last:
        reply = (
            "Try National Scholarship Portal, MP Scholarship Portal, and AICTE Pragati. "
            "Check eligibility using income and recent grades."
        )
    elif "risk" in last or "dropout" in last:
        reply = "High attendance gaps and backlogs are strong risk drivers. Start weekly follow-up interventions."
    else:
        reply = "I can help with risk analysis, interventions, and scholarship guidance."

    return jsonify({"reply": reply})



if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = _parse_bool(os.getenv("FLASK_DEBUG"), default=False)
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
