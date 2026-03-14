# pyright: ignore
import os
from datetime import date
from typing import Dict, Optional, Tuple

import pandas as pd

from backend.db import db
from backend.models import Scholarship


REQUIRED_SCHOLARSHIP_COLUMNS: Tuple[str, ...] = (
    "scholarship_id",
    "scholarship_name",
    "provider",
    "category",
    "education_level",
    "min_marks_required",
    "income_limit",
    "scholarship_amount",
    "state",
    "deadline",
    "application_mode",
)


def validate_scholarship_dataframe(df: pd.DataFrame) -> None:
    cols = [str(c).strip().lstrip("\ufeff") for c in df.columns.tolist()]
    missing = [c for c in REQUIRED_SCHOLARSHIP_COLUMNS if c not in cols]
    if missing:
        raise ValueError(f"Scholarship CSV missing columns: {missing}")

    unexpected = [c for c in cols if c not in REQUIRED_SCHOLARSHIP_COLUMNS]
    if unexpected:
        raise ValueError(
            "Scholarship CSV has unexpected columns: "
            f"{unexpected}. Expected exactly: {list(REQUIRED_SCHOLARSHIP_COLUMNS)}"
        )


def _coerce_deadline(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce")
    if dt.isna().any():
        bad = series[dt.isna()].head(5).tolist()
        raise ValueError(f"Invalid deadline values (examples): {bad}")
    return dt.dt.date


def _to_float(series: pd.Series, field: str) -> pd.Series:
    out = pd.to_numeric(series, errors="coerce")
    if out.isna().any():
        bad = series[out.isna()].head(5).tolist()
        raise ValueError(f"Invalid numeric values for {field} (examples): {bad}")
    return out.astype(float)


def _to_int(series: pd.Series, field: str) -> pd.Series:
    out = pd.to_numeric(series, errors="coerce")
    if out.isna().any():
        bad = series[out.isna()].head(5).tolist()
        raise ValueError(f"Invalid integer values for {field} (examples): {bad}")
    return out.astype(int)


def load_scholarships_from_csv(csv_path: str, *, replace_existing: bool = False) -> int:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Scholarship CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    # Normalize headers to avoid "validated but not accessible" issues.
    df = df.rename(columns=lambda c: str(c).strip().lstrip("\ufeff"))
    validate_scholarship_dataframe(df)
    df["scholarship_id"] = _to_int(df["scholarship_id"], "scholarship_id")
    df["min_marks_required"] = _to_float(df["min_marks_required"], "min_marks_required")
    df["income_limit"] = _to_float(df["income_limit"], "income_limit")
    df["scholarship_amount"] = _to_float(df["scholarship_amount"], "scholarship_amount")
    df["deadline"] = _coerce_deadline(df["deadline"])

    if replace_existing:
        db.session.query(Scholarship).delete()
        db.session.commit()

    upserted = 0
    for row in df.to_dict(orient="records"):
        existing = db.session.get(Scholarship, int(row["scholarship_id"]))
        if existing is None:
            existing = Scholarship(scholarship_id=int(row["scholarship_id"]))
            db.session.add(existing)

        existing.scholarship_name = str(row["scholarship_name"]).strip()
        existing.provider = str(row["provider"]).strip()
        existing.category = str(row["category"]).strip()
        existing.education_level = str(row["education_level"]).strip()
        existing.min_marks_required = float(row["min_marks_required"]) 
        existing.income_limit = float(row["income_limit"]) 
        existing.scholarship_amount = float(row["scholarship_amount"]) 
        existing.state = str(row["state"]).strip()
        existing.deadline = row["deadline"] if isinstance(row["deadline"], date) else pd.to_datetime(row["deadline"]).date()
        existing.application_mode = str(row["application_mode"]).strip()
        upserted += 1

    db.session.commit()
    return upserted


def ensure_scholarships_loaded(
    *,
    csv_path: Optional[str] = None,
) -> Dict[str, object]:
    default_path = os.path.join(os.path.dirname(__file__), "..", "training", "scholarship_dataset.csv.csv")
    resolved_path = csv_path or os.getenv("SCHOLARSHIP_CSV_PATH") or default_path

    existing_count = Scholarship.query.count()
    if existing_count > 0:
        return {"loaded": False, "count": existing_count, "csv_path": resolved_path}

    count = load_scholarships_from_csv(resolved_path)
    return {"loaded": True, "count": count, "csv_path": resolved_path}
