from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from db import db
from models import Student, Prediction, Action, User
from services.predictor import predict_risk
from services.shap_explain import explain_student
from services.recommender import generate_recommendations
import json


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

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

    @app.route("/predict", methods=["POST"])
    def predict():
        data = request.json
        risk = predict_risk(data)
        explanation = explain_student(data)
        recommendations = generate_recommendations(data, risk)

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
            "recommendations": recommendations
        })

    @app.route("/students/high-risk", methods=["GET"])
    def high_risk():
        preds = Prediction.query.order_by(Prediction.risk_score.desc()).limit(10).all()
        items = [
            {"student_id": p.student_id, "risk": p.risk_score, "created_at": p.created_at.isoformat()}
            for p in preds
        ]
        return jsonify({"students": items})

    @app.route("/actions", methods=["POST"])
    def create_action():
        data = request.json
        action = Action(**data)
        db.session.add(action)
        db.session.commit()
        return jsonify({"id": action.id})

    @app.route("/monitoring", methods=["GET"])
    def monitoring():
        actions = Action.query.order_by(Action.created_at.desc()).all()
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
    app.run(debug=True)
