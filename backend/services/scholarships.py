# pyright: ignore

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import asc, desc

from backend.models import Scholarship


def _avg_grade(student: Dict[str, Any]) -> Optional[float]:
    grades = []
    for key in ("grade_math", "grade_science", "grade_english"):
        val = student.get(key)
        if val is None:
            continue
        try:
            grades.append(float(val))
        except Exception:
            return None
    if not grades:
        return None
    return sum(grades) / len(grades)


def match_scholarships(student: Dict[str, Any], *, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        family_income = float(student.get("family_income"))
    except Exception:
        family_income = None

    avg = _avg_grade(student)
    state = student.get("state")

    q = Scholarship.query
    if family_income is not None:
        q = q.filter(Scholarship.income_limit >= family_income)
    if avg is not None:
        q = q.filter(Scholarship.min_marks_required <= avg)
    if isinstance(state, str) and state.strip():
        q = q.filter(Scholarship.state.ilike(state.strip()))

    q = q.order_by(desc(Scholarship.scholarship_amount), asc(Scholarship.deadline)).limit(int(limit))

    out: List[Dict[str, Any]] = []
    for s in q.all():
        out.append(
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
        )
    return out
