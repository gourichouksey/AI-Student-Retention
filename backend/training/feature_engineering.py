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


def add_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "attendance_sem1" in df.columns and "attendance_sem2" in df.columns:
        df["attendance_trend"] = df["attendance_sem2"] - df["attendance_sem1"]
        df["attendance_avg"] = (df["attendance_sem1"] + df["attendance_sem2"]) / 2
        df["attendance_low_flag"] = (df["attendance_avg"] < 75).astype(int)
        df["attendance_alarm"] = (df["attendance_trend"] < -15).astype(int)
    if "gpa_sem1" in df.columns and "gpa_sem2" in df.columns:
        df["gpa_trend"] = df["gpa_sem2"] - df["gpa_sem1"]
        df["gpa_avg"] = (df["gpa_sem1"] + df["gpa_sem2"]) / 2
        df["gpa_low_flag"] = (df["gpa_avg"] < 5.0).astype(int)
        if "attendance_trend" in df.columns:
            df["both_falling"] = (
                (df["gpa_trend"] < 0) & (df["attendance_trend"] < 0)
            ).astype(int)
    return df


def add_academic_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "backlogs" in df.columns and "total_subjects" in df.columns:
        df["backlog_ratio"] = df["backlogs"] / df["total_subjects"].replace(0, 1)
        df["high_backlog_flag"] = (df["backlog_ratio"] > 0.25).astype(int)
    distress_cols = []
    if "gpa_low_flag" in df.columns:
        distress_cols.append("gpa_low_flag")
    if "attendance_low_flag" in df.columns:
        distress_cols.append("attendance_low_flag")
    if "high_backlog_flag" in df.columns:
        distress_cols.append("high_backlog_flag")
    if distress_cols:
        df["academic_distress_score"] = df[distress_cols].sum(axis=1)
        if "gpa_low_flag" in df.columns and "attendance_low_flag" in df.columns:
            df["dual_academic_risk"] = (
                (df["gpa_low_flag"] == 1) & (df["attendance_low_flag"] == 1)
            ).astype(int)
    return df


def add_socioeconomic_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "scholarship_status" in df.columns:
        if df["scholarship_status"].dtype == object:
            df["scholarship_status"] = df["scholarship_status"].apply(
                lambda x: 1 if str(x).strip().lower() in ["yes", "1", "true", "y"] else 0
            )
        df["scholarship_status"] = pd.to_numeric(
            df["scholarship_status"], errors="coerce"
        ).fillna(0).astype(int)
    if "family_income" in df.columns:
        max_income = max(df["family_income"].quantile(0.95), 1)
        df["income_normalized"] = (df["family_income"] / max_income).clip(0, 1)
        df["financial_vulnerability"] = 1 - df["income_normalized"]
        df["low_income_flag"] = (
            df["family_income"] < df["family_income"].quantile(0.30)
        ).astype(int)
    if "parent_education" in df.columns:
        edu_map = {
            "none": 0, "no education": 0, "primary": 1, "middle": 1,
            "school": 2, "secondary": 2, "high school": 2, "matric": 2,
            "graduate": 3, "college": 3, "bachelor": 3,
            "postgraduate": 4, "master": 4, "phd": 4,
        }
        if df["parent_education"].dtype == object:
            df["parent_education"] = df["parent_education"].apply(
                lambda x: edu_map.get(str(x).strip().lower(), 1)
                if isinstance(x, str) else x
            )
        df["parent_edu_normalized"] = (df["parent_education"] / 4.0).clip(0, 1)
    if "low_income_flag" in df.columns and "scholarship_status" in df.columns:
        df["financial_stress_flag"] = (
            (df["low_income_flag"] == 1) & (df["scholarship_status"] == 0)
        ).astype(int)
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
    if engagement_parts:
        df["engagement_score"] = sum(engagement_parts) / len(engagement_parts)
        df["low_engagement_flag"] = (df["engagement_score"] < 0.35).astype(int)
        if "login_norm" in df.columns and "assignment_norm" in df.columns:
            df["disengagement_flag"] = (
                (df["login_norm"] < 0.2) & (df["assignment_norm"] < 0.5)
            ).astype(int)
    return df


def add_composite_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "dual_academic_risk" in df.columns and "financial_stress_flag" in df.columns:
        df["acad_financial_risk"] = (
            (df["dual_academic_risk"] == 1) & (df["financial_stress_flag"] == 1)
        ).astype(int)
    if "disengagement_flag" in df.columns and "attendance_low_flag" in df.columns:
        df["disengaged_absent_risk"] = (
            (df["disengagement_flag"] == 1) & (df["attendance_low_flag"] == 1)
        ).astype(int)
    risk_parts = []
    weights = {
        "dual_academic_risk": 2.0, "financial_stress_flag": 1.5,
        "disengagement_flag": 1.5, "attendance_low_flag": 1.0,
        "gpa_low_flag": 1.0, "high_backlog_flag": 1.0, "attendance_alarm": 0.5,
    }
    total_weight = 0
    for col, weight in weights.items():
        if col in df.columns:
            risk_parts.append(df[col] * weight)
            total_weight += weight
    if risk_parts:
        df["risk_index"] = (sum(risk_parts) / total_weight * 10).clip(0, 10)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rename_map = {"attendance_pct": "attendance_avg", "parents_edu": "parent_education"}
    df = df.rename(columns=rename_map)
    grade_cols = [c for c in ["grade_math", "grade_science", "grade_english"] if c in df.columns]
    if grade_cols:
        df["gpa_avg"] = df[grade_cols].mean(axis=1)
        if df["gpa_avg"].max() > 10:
            df["gpa_avg"] = df["gpa_avg"] / 10
        df["gpa_low_flag"] = (df["gpa_avg"] < 5.0).astype(int)
        for col in grade_cols:
            threshold = 50 if df[col].max() > 10 else 5
            df[f"{col}_fail"] = (df[col] < threshold).astype(int)
        df["multi_subject_fail"] = (
            df[[f"{c}_fail" for c in grade_cols]].sum(axis=1) >= 2
        ).astype(int)
    if "attendance_avg" in df.columns:
        df["attendance_low_flag"] = (df["attendance_avg"] < 75).astype(int)
        df["attendance_critical"] = (df["attendance_avg"] < 60).astype(int)
        df["attendance_norm"] = (df["attendance_avg"] / 100).clip(0, 1)
    if "backlogs" in df.columns:
        df["has_backlog"] = (df["backlogs"] > 0).astype(int)
        df["high_backlog"] = (df["backlogs"] >= 2).astype(int)
    if "family_income" in df.columns:
        max_income = max(df["family_income"].quantile(0.95), 1)
        df["income_normalized"] = (df["family_income"] / max_income).clip(0, 1)
        df["financial_vulnerability"] = 1 - df["income_normalized"]
        df["low_income_flag"] = (
            df["family_income"] < df["family_income"].quantile(0.30)
        ).astype(int)
    if "parent_education" in df.columns:
        edu_map = {
            "none": 0, "primary": 1, "middle": 1, "school": 2,
            "secondary": 2, "high school": 2, "graduate": 3,
            "college": 3, "postgraduate": 4, "phd": 4,
        }
        if df["parent_education"].dtype == object:
            df["parent_education"] = df["parent_education"].apply(
                lambda x: edu_map.get(str(x).strip().lower(), 1)
                if isinstance(x, str) else x
            )
        df["parent_edu_normalized"] = (df["parent_education"] / 4.0).clip(0, 1)
    if "scholarship_status" in df.columns:
        if df["scholarship_status"].dtype == object:
            df["scholarship_status"] = df["scholarship_status"].apply(
                lambda x: 1 if str(x).strip().lower() in ["yes", "1", "true"] else 0
            )
        df["scholarship_status"] = pd.to_numeric(
            df["scholarship_status"], errors="coerce"
        ).fillna(0).astype(int)
    if "low_income_flag" in df.columns and "scholarship_status" in df.columns:
        df["financial_stress_flag"] = (
            (df["low_income_flag"] == 1) & (df["scholarship_status"] == 0)
        ).astype(int)
    risk_parts = []
    weights = {
        "gpa_low_flag": 2.0, "multi_subject_fail": 2.0,
        "attendance_low_flag": 1.5, "attendance_critical": 2.0,
        "financial_stress_flag": 1.5, "high_backlog": 1.5, "low_income_flag": 1.0,
    }
    total_weight = 0
    for col, w in weights.items():
        if col in df.columns:
            risk_parts.append(df[col] * w)
            total_weight += w
    if risk_parts:
        df["risk_index"] = (sum(risk_parts) / total_weight * 10).clip(0, 10)
    for col in df.select_dtypes(include=["object", "category"]).columns:
        df[col] = pd.factorize(df[col])[0]
    for col in df.select_dtypes(include=["bool"]).columns:
        df[col] = df[col].astype(int)
    df = df.fillna(0)
    return df


FEATURE_EXPLANATIONS = {
    "attendance_trend": "Attendance change this semester",
    "attendance_avg": "Average attendance across semesters",
    "attendance_low_flag": "Attendance below 75% minimum",
    "gpa_trend": "GPA change this semester",
    "gpa_avg": "Average GPA across semesters",
    "gpa_low_flag": "GPA below passing threshold",
    "backlog_ratio": "Fraction of subjects with backlogs",
    "financial_stress_flag": "Low income with no scholarship",
    "engagement_score": "Overall platform engagement level",
    "risk_index": "Overall multi-factor risk score (0-10)",
}