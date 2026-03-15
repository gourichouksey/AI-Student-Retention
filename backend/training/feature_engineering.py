# =============================================================
# Author: Antra Gupta
# GitHub: https://github.com/guptaantra6405-creator
# Contribution: Feature Engineering Module for Student Retention AI
# Date: March 2026
# Description: Transforms 9 raw columns into 25 engineered ML features
# =============================================================
"""
feature_engineering.py
=======================
This file turns raw student data into meaningful ML features.

The model is only as good as its features.
Raw data has 10 columns. After this file runs → 25+ columns.
More meaningful columns = better predictions.

How to use:
    from feature_engineering import build_features
    df_enriched = build_features(df_raw)
"""

import pandas as pd
import numpy as np


# ─────────────────────────────────────────────────────────
# SECTION 1 — TREND FEATURES
# Is the student getting WORSE over time?
# A drop from 80% to 55% is more dangerous than stable 55%
# ─────────────────────────────────────────────────────────

def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "attendance_sem1" in df.columns and "attendance_sem2" in df.columns:
        # Negative number = attendance is falling (dangerous)
        df["attendance_trend"] = df["attendance_sem2"] - df["attendance_sem1"]

        # Average attendance across both semesters
        df["attendance_avg"] = (df["attendance_sem1"] + df["attendance_sem2"]) / 2

        # Flag: is attendance below 75%? (AICTE minimum requirement in India)
        df["attendance_low_flag"] = (df["attendance_avg"] < 75).astype(int)

        # Is the drop accelerating? (more than 15% drop = alarm)
        df["attendance_alarm"] = (df["attendance_trend"] < -15).astype(int)

    if "gpa_sem1" in df.columns and "gpa_sem2" in df.columns:
        # Negative = grades are falling
        df["gpa_trend"] = df["gpa_sem2"] - df["gpa_sem1"]

        # Average GPA
        df["gpa_avg"] = (df["gpa_sem1"] + df["gpa_sem2"]) / 2

        # Flag: GPA below 5.0 on 10-point scale
        df["gpa_low_flag"] = (df["gpa_avg"] < 5.0).astype(int)

        # Both falling at same time = very dangerous
        if "attendance_trend" in df.columns:
            df["both_falling"] = (
                (df["gpa_trend"] < 0) & (df["attendance_trend"] < 0)
            ).astype(int)

    return df


# ─────────────────────────────────────────────────────────
# SECTION 2 — ACADEMIC STRESS FEATURES
# How much academic pressure is the student under?
# ─────────────────────────────────────────────────────────

def add_academic_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "backlogs" in df.columns and "total_subjects" in df.columns:
        # Ratio is smarter than raw count
        # 2 backlogs out of 6 = 33% is worse than 2 out of 10 = 20%
        df["backlog_ratio"] = (
            df["backlogs"] / df["total_subjects"].replace(0, 1)
        )

        # Flag: more than 25% subjects have backlogs
        df["high_backlog_flag"] = (df["backlog_ratio"] > 0.25).astype(int)

    # Academic distress score (0, 1, 2, or 3 — how many things are wrong)
    distress_cols = []
    if "gpa_low_flag" in df.columns:
        distress_cols.append("gpa_low_flag")
    if "attendance_low_flag" in df.columns:
        distress_cols.append("attendance_low_flag")
    if "high_backlog_flag" in df.columns:
        distress_cols.append("high_backlog_flag")

    if distress_cols:
        df["academic_distress_score"] = df[distress_cols].sum(axis=1)

        # Dual risk: both GPA AND attendance are low simultaneously
        if "gpa_low_flag" in df.columns and "attendance_low_flag" in df.columns:
            df["dual_academic_risk"] = (
                (df["gpa_low_flag"] == 1) & (df["attendance_low_flag"] == 1)
            ).astype(int)

    return df


# ─────────────────────────────────────────────────────────
# SECTION 3 — SOCIOECONOMIC FEATURES
# Financial background strongly predicts dropout in India
# ─────────────────────────────────────────────────────────

def add_socioeconomic_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Convert scholarship_status text to number if needed
    if "scholarship_status" in df.columns:
        if df["scholarship_status"].dtype == object:
            df["scholarship_status"] = df["scholarship_status"].apply(
                lambda x: 1 if str(x).strip().lower() in 
                ["yes", "1", "true", "y"] else 0
            )
        df["scholarship_status"] = pd.to_numeric(
            df["scholarship_status"], errors="coerce"
        ).fillna(0).astype(int)

    if "family_income" in df.columns:
        # Normalize income to 0-1 scale
        # Use 95th percentile to avoid one rich outlier skewing everything
        max_income = df["family_income"].quantile(0.95)
        max_income = max(max_income, 1)  # avoid divide by zero
        df["income_normalized"] = (df["family_income"] / max_income).clip(0, 1)

        # Financial vulnerability (1 - income score, higher = more vulnerable)
        df["financial_vulnerability"] = 1 - df["income_normalized"]

        # Bottom 30% income = low income family
        low_income_threshold = df["family_income"].quantile(0.30)
        df["low_income_flag"] = (
            df["family_income"] < low_income_threshold
        ).astype(int)

    if "parent_education" in df.columns:
        # Convert text to number if needed
        edu_map = {
            "none": 0, "no education": 0,
            "primary": 1, "middle": 1,
            "school": 2, "secondary": 2, "high school": 2, "matric": 2,
            "graduate": 3, "college": 3, "bachelor": 3,
            "postgraduate": 4, "master": 4, "phd": 4,
        }
        if df["parent_education"].dtype == object:
            df["parent_education"] = df["parent_education"].apply(
                lambda x: edu_map.get(str(x).strip().lower(), 1)
                if isinstance(x, str) else x
            )
        # Normalize to 0-1
        df["parent_edu_normalized"] = (df["parent_education"] / 4.0).clip(0, 1)

    # Financial stress flag: poor family + no scholarship = highest risk
    if "low_income_flag" in df.columns and "scholarship_status" in df.columns:
        df["financial_stress_flag"] = (
            (df["low_income_flag"] == 1) &
            (df["scholarship_status"] == 0)
        ).astype(int)

    # Composite SES score (higher = better socioeconomic status)
    ses_parts = []
    if "income_normalized" in df.columns:
        ses_parts.append(df["income_normalized"] * 0.5)
    if "parent_edu_normalized" in df.columns:
        ses_parts.append(df["parent_edu_normalized"] * 0.3)
    if "scholarship_status" in df.columns:
        ses_parts.append(df["scholarship_status"] * 0.2)

    if ses_parts:
        df["ses_score"] = sum(ses_parts)

    return df


# ─────────────────────────────────────────────────────────
# SECTION 4 — BEHAVIORAL / ENGAGEMENT FEATURES
# Digital engagement is an early warning signal
# Students who stop logging in are about to drop out
# ─────────────────────────────────────────────────────────

def add_behavioral_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    engagement_parts = []

    if "login_frequency" in df.columns:
        max_login = max(df["login_frequency"].quantile(0.95), 1)
        df["login_norm"] = (df["login_frequency"] / max_login).clip(0, 1)
        engagement_parts.append(df["login_norm"])

    if "quiz_participation" in df.columns:
        df["quiz_norm"] = df["quiz_participation"].clip(0, 1)
        engagement_parts.append(df["quiz_norm"])

    if "time_on_platform_hrs" in df.columns:
        max_time = max(df["time_on_platform_hrs"].quantile(0.95), 1)
        df["time_norm"] = (df["time_on_platform_hrs"] / max_time).clip(0, 1)
        engagement_parts.append(df["time_norm"])

    if "assignment_submission_rate" in df.columns:
        df["assignment_norm"] = df["assignment_submission_rate"].clip(0, 1)
        engagement_parts.append(df["assignment_norm"])

    # Composite engagement score (average of all available signals)
    if engagement_parts:
        df["engagement_score"] = sum(engagement_parts) / len(engagement_parts)

        # Flag: very low engagement
        df["low_engagement_flag"] = (df["engagement_score"] < 0.35).astype(int)

        # Flag: sudden disengagement (login very low AND assignments missing)
        if "login_norm" in df.columns and "assignment_norm" in df.columns:
            df["disengagement_flag"] = (
                (df["login_norm"] < 0.2) & (df["assignment_norm"] < 0.5)
            ).astype(int)

    return df


# ─────────────────────────────────────────────────────────
# SECTION 5 — COMPOSITE RISK FEATURES
# Combinations are more powerful than individual signals
# ─────────────────────────────────────────────────────────

def add_composite_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Academic + Financial double risk
    if "dual_academic_risk" in df.columns and "financial_stress_flag" in df.columns:
        df["acad_financial_risk"] = (
            (df["dual_academic_risk"] == 1) & (df["financial_stress_flag"] == 1)
        ).astype(int)

    # Disengaged + absent = very high dropout signal
    if "disengagement_flag" in df.columns and "attendance_low_flag" in df.columns:
        df["disengaged_absent_risk"] = (
            (df["disengagement_flag"] == 1) & (df["attendance_low_flag"] == 1)
        ).astype(int)

    # Overall risk index (0 to 10 scale — shown on dashboard)
    risk_parts = []
    weights = {
        "dual_academic_risk":    2.0,   # both GPA and attendance low
        "financial_stress_flag": 1.5,   # poor + no scholarship
        "disengagement_flag":    1.5,   # stopped using platform
        "attendance_low_flag":   1.0,   # below 75%
        "gpa_low_flag":          1.0,   # below 5.0
        "high_backlog_flag":     1.0,   # many failed subjects
        "attendance_alarm":      0.5,   # falling fast
    }

    total_weight = 0
    for col, weight in weights.items():
        if col in df.columns:
            risk_parts.append(df[col] * weight)
            total_weight += weight

    if risk_parts:
        raw_risk = sum(risk_parts)
        # Normalize to 0-10 scale
        df["risk_index"] = (raw_risk / total_weight * 10).clip(0, 10)

    return df


# ─────────────────────────────────────────────────────────
# MASTER FUNCTION — call this one function from train.py
# It runs all 5 sections in the correct order
# ─────────────────────────────────────────────────────────

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Master pipeline — works with THIS project's actual columns:
    attendance_pct, backlogs, family_income, parents_edu,
    scholarship_status, grade_math, grade_science, grade_english
    """
    df = df.copy()

    # ── STEP 1: Rename columns to match feature engineering ──
    rename_map = {
        "attendance_pct": "attendance_avg",
        "parents_edu":    "parent_education",
    }
    df = df.rename(columns=rename_map)

    # ── STEP 2: Create GPA average from 3 subject grades ──
    grade_cols = []
    for col in ["grade_math", "grade_science", "grade_english"]:
        if col in df.columns:
            grade_cols.append(col)

    if grade_cols:
        # Average of all subject grades = overall GPA
        df["gpa_avg"] = df[grade_cols].mean(axis=1)

        # Normalize to 0-10 scale if grades are out of 100
        if df["gpa_avg"].max() > 10:
            df["gpa_avg"] = df["gpa_avg"] / 10

        # Flag: average grade below 50% = failing
        df["gpa_low_flag"] = (df["gpa_avg"] < 5.0).astype(int)

        # Individual subject failure flags
        for col in grade_cols:
            threshold = 50 if df[col].max() > 10 else 5
            df[f"{col}_fail"] = (df[col] < threshold).astype(int)

        # Failing 2+ subjects simultaneously
        fail_cols = [f"{col}_fail" for col in grade_cols]
        df["multi_subject_fail"] = (
            df[fail_cols].sum(axis=1) >= 2
        ).astype(int)

    # ── STEP 3: Attendance features ──
    if "attendance_avg" in df.columns:
        df["attendance_low_flag"] = (
            df["attendance_avg"] < 75
        ).astype(int)

        df["attendance_critical"] = (
            df["attendance_avg"] < 60
        ).astype(int)

        # Normalize to 0-1
        df["attendance_norm"] = (df["attendance_avg"] / 100).clip(0, 1)

    # ── STEP 4: Backlog features ──
    if "backlogs" in df.columns:
        df["has_backlog"] = (df["backlogs"] > 0).astype(int)
        df["high_backlog"] = (df["backlogs"] >= 2).astype(int)

    # ── STEP 5: Socioeconomic features ──
    if "family_income" in df.columns:
        max_income = max(df["family_income"].quantile(0.95), 1)
        df["income_normalized"] = (
            df["family_income"] / max_income
        ).clip(0, 1)
        df["financial_vulnerability"] = 1 - df["income_normalized"]
        low_income_thresh = df["family_income"].quantile(0.30)
        df["low_income_flag"] = (
            df["family_income"] < low_income_thresh
        ).astype(int)

    if "parent_education" in df.columns:
        edu_map = {
            "none": 0, "no education": 0,
            "primary": 1, "middle": 1,
            "school": 2, "secondary": 2,
            "high school": 2, "matric": 2,
            "graduate": 3, "college": 3,
            "postgraduate": 4, "phd": 4,
        }
        if df["parent_education"].dtype == object:
            df["parent_education"] = df["parent_education"].apply(
                lambda x: edu_map.get(
                    str(x).strip().lower(), 1
                ) if isinstance(x, str) else x
            )
        df["parent_edu_normalized"] = (
            df["parent_education"] / 4.0
        ).clip(0, 1)

    if "scholarship_status" in df.columns:
        if df["scholarship_status"].dtype == object:
            df["scholarship_status"] = df["scholarship_status"].apply(
                lambda x: 1 if str(x).strip().lower()
                in ["yes", "1", "true"] else 0
            )
        df["scholarship_status"] = pd.to_numeric(
            df["scholarship_status"], errors="coerce"
        ).fillna(0).astype(int)

    # Financial stress: poor + no scholarship
    if "low_income_flag" in df.columns and "scholarship_status" in df.columns:
        df["financial_stress_flag"] = (
            (df["low_income_flag"] == 1) &
            (df["scholarship_status"] == 0)
        ).astype(int)

    # ── STEP 6: Composite risk score ──
    risk_parts = []
    weights = {
        "gpa_low_flag":          2.0,
        "multi_subject_fail":    2.0,
        "attendance_low_flag":   1.5,
        "attendance_critical":   2.0,
        "financial_stress_flag": 1.5,
        "high_backlog":          1.5,
        "low_income_flag":       1.0,
    }
    total_weight = 0
    for col, w in weights.items():
        if col in df.columns:
            risk_parts.append(df[col] * w)
            total_weight += w

    if risk_parts:
        df["risk_index"] = (
            sum(risk_parts) / total_weight * 10
        ).clip(0, 10)

    # ── FINAL CLEANUP ──
    # Convert all text columns to numbers
    for col in df.select_dtypes(
        include=["object", "category"]
    ).columns:
        df[col] = pd.factorize(df[col])[0]

    # Convert booleans to int
    for col in df.select_dtypes(include=["bool"]).columns:
        df[col] = df[col].astype(int)

    # Fill missing values
    df = df.fillna(0)

    return df

# ─────────────────────────────────────────────────────────
# FEATURE EXPLANATIONS
# Used by the SHAP explainer to show human-readable text
# on the dashboard instead of code variable names
# ─────────────────────────────────────────────────────────

FEATURE_EXPLANATIONS = {
    "attendance_trend":       "Attendance change this semester",
    "attendance_avg":         "Average attendance across semesters",
    "attendance_low_flag":    "Attendance below 75% minimum",
    "attendance_alarm":       "Attendance dropped more than 15%",
    "gpa_trend":              "GPA change this semester",
    "gpa_avg":                "Average GPA across semesters",
    "gpa_low_flag":           "GPA below passing threshold",
    "both_falling":           "Both GPA and attendance declining",
    "backlog_ratio":          "Fraction of subjects with backlogs",
    "high_backlog_flag":      "More than 25% subjects have backlogs",
    "academic_distress_score":"Number of academic risk factors present",
    "dual_academic_risk":     "Both GPA and attendance are critically low",
    "income_normalized":      "Family income level (normalized)",
    "financial_vulnerability":"Financial hardship level",
    "low_income_flag":        "Family income in bottom 30%",
    "financial_stress_flag":  "Low income with no scholarship",
    "ses_score":              "Overall socioeconomic status score",
    "engagement_score":       "Overall platform engagement level",
    "low_engagement_flag":    "Very low platform engagement",
    "disengagement_flag":     "Sudden drop in logins and submissions",
    "risk_index":             "Overall multi-factor risk score (0-10)",
    "acad_financial_risk":    "Academic and financial stress combined",
    "disengaged_absent_risk": "Absent from class and disengaged online",
}


# ─────────────────────────────────────────────────────────
# QUICK TEST — run this file directly to verify it works
# python backend/training/feature_engineering.py
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Create one fake student to test
    sample = pd.DataFrame([{
        "student_id":                "S001",
        "attendance_sem1":           80,
        "attendance_sem2":           55,
        "gpa_sem1":                  7.2,
        "gpa_sem2":                  5.1,
        "backlogs":                  2,
        "total_subjects":            6,
        "family_income":             150000,
        "parent_education":          "school",
        "scholarship_status":        0,
        "login_frequency":           3,
        "quiz_participation":        0.3,
        "time_on_platform_hrs":      1.5,
        "assignment_submission_rate": 0.55,
        "age":                       20,
        "dropout":                   1,
    }])

    result = build_features(sample)

    print("=== Engineered features for sample student ===\n")
    # Show only the new columns we added
    original_cols = list(sample.columns)
    new_cols = [c for c in result.columns if c not in original_cols]

    for col in new_cols:
        val = result[col].iloc[0]
        explanation = FEATURE_EXPLANATIONS.get(col, "")
        print(f"  {col:30s} = {val:6.3f}   ({explanation})")

    print(f"\nTotal new features added: {len(new_cols)}")
    print(f"Original features: {len(original_cols)}")
    print(f"Total features now: {len(result.columns)}")