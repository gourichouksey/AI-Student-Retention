from datetime import datetime
from db import db


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    attendance_pct = db.Column(db.Float, nullable=False)
    backlogs = db.Column(db.Integer, nullable=False)
    family_income = db.Column(db.Float, nullable=False)
    parents_edu = db.Column(db.String(120), nullable=False)
    scholarship_status = db.Column(db.String(30), nullable=False)
    grade_math = db.Column(db.Float, nullable=False)
    grade_science = db.Column(db.Float, nullable=False)
    grade_english = db.Column(db.Float, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="planned")
    outcome = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
