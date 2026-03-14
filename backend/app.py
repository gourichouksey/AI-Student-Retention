# pyright: reportMissingImports=false, reportUndefinedVariable=false

import sys
from pathlib import Path

# Ensure repo root is on sys.path so `backend.*` imports work whether you run:
# - from repo root: `python -m backend.app`
# - from anywhere: `python backend/app.py`
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Load env vars from backend/.env if available (do not commit secrets).
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except Exception:
    pass

from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_cors import CORS
from backend.db import db
from backend.models import Student, Prediction, Action, User, Scholarship
from backend.services.predictor import predict_risk
from backend.services.shap_explain import explain_student
from backend.services.recommender import generate_recommendations
from backend.services.scholarship_loader import ensure_scholarships_loaded
from backend.services.scholarships import match_scholarships
from backend.services.eligibility_model import recommend_scholarships_ml
from backend.services.chat_ai import generate_chat_reply
from sqlalchemy import func
from datetime import datetime, timedelta
import json
import os


def create_app():
    app = Flask(__name__)
    CORS(app)

    base_dir = Path(__file__).resolve().parent
    instance_dir = base_dir / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)
    default_db_path = instance_dir / "db.sqlite3"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") or f"sqlite:///{default_db_path.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["GOOGLE_CLIENT_ID"] = os.getenv(
        "GOOGLE_CLIENT_ID",
        "886376637376-0v87tkcqkukg983r5kokqfcf2rit7e81.apps.googleusercontent.com",
    )

    db.init_app(app)

    with app.app_context():
        db.create_all()
        try:
            ensure_scholarships_loaded()
        except Exception as e:
            # Keep app usable even if scholarship CSV has issues.
            print(f"[scholarships] load failed: {e}")

        if not User.query.first():
            demo_user = User(
                name="Demo User",
                email="demo@retention.ai",
                password_hash=generate_password_hash("demo123")
            )
            db.session.add(demo_user)
            db.session.commit()

    @app.route("/students", methods=["POST"])
    def create_student():
        data = request.json
        student = Student(**data)
        db.session.add(student)
        db.session.commit()
        return jsonify({"id": student.id})

    @app.route("/auth/signup", methods=["POST"])
    def signup():
        data = request.json
        if User.query.filter_by(email=data.get("email")).first():
            return jsonify({"error": "Email already registered"}), 400
        user = User(
            name=data.get("name"),
            email=data.get("email"),
            password_hash=generate_password_hash(data.get("password"))
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"id": user.id, "name": user.name, "email": user.email})

    @app.route("/auth/login", methods=["POST"])
    def login():
        data = request.json
        user = User.query.filter_by(email=data.get("email")).first()
        if not user or not check_password_hash(user.password_hash, data.get("password")):
            return jsonify({"error": "Invalid credentials"}), 401
        return jsonify({"id": user.id, "name": user.name, "email": user.email})

    @app.route("/auth/google", methods=["POST"])
    def google_auth():
        token = request.json.get("token")
        try:
            info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                app.config["GOOGLE_CLIENT_ID"]
            )
        except Exception as e:
            if app.debug:
                return jsonify({"error": "Invalid Google token", "details": str(e)}), 401
            return jsonify({"error": "Invalid Google token"}), 401

        email = info.get("email")
        name = info.get("name", "Google User")
        if not email:
            return jsonify({"error": "Google account missing email"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash("google")
            )
            db.session.add(user)
            db.session.commit()

        return jsonify({"id": user.id, "name": user.name, "email": user.email})

    @app.route("/predict", methods=["POST"])
    def predict():
        data = request.json
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400

        risk = predict_risk(data)
        explanation = explain_student(data)
        recommendations = generate_recommendations(data, risk)
        scholarships = recommend_scholarships_ml(data, limit=5)

        pred = Prediction(
            student_id=data.get("student_id", 0),
            risk_score=risk,
            explanation=json.dumps(explanation)
        )
        db.session.add(pred)
        db.session.commit()

        return jsonify({
            "risk_score": risk,
            "explanation": explanation,
            "recommendations": recommendations,
            "scholarships": scholarships,
        })

    @app.route("/scholarships", methods=["GET"])
    def list_scholarships():
        items = Scholarship.query.order_by(Scholarship.deadline.asc()).limit(500).all()
        return jsonify(
            {
                "scholarships": [
                    {
                        "scholarship_id": s.scholarship_id,
                        "scholarship_name": s.scholarship_name,
                        "provider": s.provider,
                        "category": s.category,
                        "education_level": s.education_level,
                        "min_marks_required": float(s.min_marks_required),
                        "income_limit": float(s.income_limit),
                        "scholarship_amount": float(s.scholarship_amount),
                        "state": s.state,
                        "deadline": s.deadline.isoformat(),
                        "application_mode": s.application_mode,
                    }
                    for s in items
                ]
            }
        )

    @app.route("/scholarships/match", methods=["POST"])
    def scholarships_match():
        data = request.json or {}
        limit = int(data.get("limit", 5))
        student = data.get("student") if isinstance(data.get("student"), dict) else data
        return jsonify({"scholarships": match_scholarships(student, limit=limit)})

    @app.route("/scholarships/recommend", methods=["POST"])
    def scholarships_recommend():
        data = request.json or {}
        limit = int(data.get("limit", 5))
        student = data.get("student") if isinstance(data.get("student"), dict) else data
        return jsonify({"scholarships": recommend_scholarships_ml(student, limit=limit)})

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.json
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON payload"}), 400

        messages = data.get("messages")
        if isinstance(messages, list):
            safe_messages = []
            for m in messages[-20:]:
                if not isinstance(m, dict):
                    continue
                role = (m.get("role") or "").strip()
                text = (m.get("text") or "").strip()
                if not text:
                    continue
                safe_messages.append({"role": role, "text": text})
        else:
            text = (data.get("message") or "").strip()
            safe_messages = [{"role": "user", "text": text}] if text else []

        if not safe_messages:
            return jsonify({"error": "Missing message(s)"}), 400

        try:
            reply = generate_chat_reply(safe_messages)
        except Exception as e:
            # Don't leak secrets; return a useful error.
            return jsonify({"error": "Chat service unavailable", "details": str(e)}), 503

        return jsonify({"reply": reply})

    @app.route("/students/high-risk", methods=["GET"])
    def high_risk():
        latest_per_student = (
            db.session.query(
                Prediction.student_id.label("student_id"),
                func.max(Prediction.created_at).label("max_created_at"),
            )
            .group_by(Prediction.student_id)
            .subquery()
        )

        preds = (
            db.session.query(Prediction)
            .join(
                latest_per_student,
                (Prediction.student_id == latest_per_student.c.student_id)
                & (Prediction.created_at == latest_per_student.c.max_created_at),
            )
            .order_by(Prediction.risk_score.desc())
            .limit(10)
            .all()
        )
        items = [
            {"student_id": p.student_id, "risk": p.risk_score, "created_at": p.created_at.isoformat()}
            for p in preds
        ]
        return jsonify({"students": items})

    @app.route("/actions", methods=["POST"])
    def create_action():
        data = request.json
        student_id = data.get("student_id")
        action_text = (data.get("action") or "").strip()

        if student_id is not None and action_text:
            recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
            existing = (
                Action.query.filter_by(student_id=student_id, action=action_text)
                .filter(Action.created_at >= recent_cutoff)
                .order_by(Action.created_at.desc())
                .first()
            )
            if existing:
                return jsonify({"id": existing.id, "deduped": True})

        action = Action(**data)
        db.session.add(action)
        db.session.commit()
        return jsonify({"id": action.id, "deduped": False})

    @app.route("/monitoring", methods=["GET"])
    def monitoring():
        actions = Action.query.order_by(Action.created_at.desc()).limit(200).all()
        items = [
            {
                "student_id": a.student_id,
                "action": a.action,
                "status": a.status,
                "outcome": a.outcome,
                "created_at": a.created_at.isoformat()
            }
            for a in actions
        ]
        return jsonify({"actions": items})

    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
