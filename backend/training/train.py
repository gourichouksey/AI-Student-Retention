"""
train.py  —  UPGRADED VERSION
==============================
What changed vs old version:
  OLD: Random Forest, no CV, no imbalance handling, no threshold tuning
  NEW: XGBoost + SMOTE + 5-fold CV + auto threshold tuning + metrics saved
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
# Import advanced feature engineering
try:
    from feature_engineering import build_features
    ADVANCED_FEATURES = True
    print("   Advanced feature engineering loaded ✓")
except ImportError:
    ADVANCED_FEATURES = False

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score,
    confusion_matrix, classification_report, precision_recall_curve,
)
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

try:
    from xgboost import XGBClassifier
    USING_XGBOOST = True
except ImportError:
    print("XGBoost not found — falling back to Random Forest.")
    from sklearn.ensemble import RandomForestClassifier
    USING_XGBOOST = False

try:
    from imblearn.over_sampling import SMOTE
    USING_SMOTE = True
except ImportError:
    print("imbalanced-learn not found — skipping SMOTE.")
    USING_SMOTE = False

BASE_DIR       = os.path.dirname(__file__)
DATASET_PATH   = os.path.join(BASE_DIR, "dataset.csv")
ARTIFACTS_DIR  = os.path.join(BASE_DIR, "artifacts")
MODEL_PATH     = os.path.join(ARTIFACTS_DIR, "model.pkl")
THRESHOLD_PATH = os.path.join(ARTIFACTS_DIR, "threshold.json")
METRICS_PATH   = os.path.join(ARTIFACTS_DIR, "metrics.json")


def load_csv_dataset(path=DATASET_PATH, target_col="dropout"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {os.path.basename(path)}. Run generate_data.py first.")
    df = pd.read_csv(path)
    if target_col not in df.columns:
        raise ValueError(f"Dataset must include '{target_col}' column")
    y = df[target_col].astype(int)
    X = df.drop(columns=[target_col])
    return X, y


def load_data():
    source = os.getenv("TRAINING_SOURCE", "csv").strip().lower()
    if source == "access":
        from train_access import load_access_dataset
        return load_access_dataset()
    return load_csv_dataset()


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    if ADVANCED_FEATURES:
        return build_features(df)
    df = df.copy()
    # Convert text columns to numbers before SMOTE
    # parent_education: none=0, primary=1, school=2, graduate=3
    if "parent_education" in df.columns:
        edu_map = {
            "none": 0, "primary": 1, "middle": 1,
            "school": 2, "secondary": 2, "high school": 2,
            "graduate": 3, "college": 3, "university": 3,
            "postgraduate": 4, "phd": 4,
        }
        df["parent_education"] = df["parent_education"].apply(
            lambda x: edu_map.get(str(x).strip().lower(), 0)
            if isinstance(x, str) else x
        )

    # Convert any remaining text columns to numbers
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = pd.factorize(df[col])[0]
    if "attendance_sem1" in df.columns and "attendance_sem2" in df.columns:
        df["attendance_trend"]    = df["attendance_sem2"] - df["attendance_sem1"]
        df["attendance_avg"]      = (df["attendance_sem1"] + df["attendance_sem2"]) / 2
        df["attendance_low_flag"] = (df["attendance_avg"] < 75).astype(int)
    if "gpa_sem1" in df.columns and "gpa_sem2" in df.columns:
        df["gpa_trend"]    = df["gpa_sem2"] - df["gpa_sem1"]
        df["gpa_avg"]      = (df["gpa_sem1"] + df["gpa_sem2"]) / 2
        df["gpa_low_flag"] = (df["gpa_avg"] < 5.0).astype(int)
    if "backlogs" in df.columns and "total_subjects" in df.columns:
        df["backlog_ratio"] = df["backlogs"] / df["total_subjects"].replace(0, 1)
    if "family_income" in df.columns:
        max_income = df["family_income"].quantile(0.95).clip(1)
        df["income_normalized"] = (df["family_income"] / max_income).clip(0, 1)
        if "scholarship_status" in df.columns:
            low_income     = df["family_income"] < df["family_income"].quantile(0.30)
            no_scholarship = df["scholarship_status"] == 0
            df["financial_stress_flag"] = (low_income & no_scholarship).astype(int)
    engagement_cols = []
    if "login_frequency" in df.columns:
        max_login = df["login_frequency"].quantile(0.95).clip(1)
        df["login_norm"] = (df["login_frequency"] / max_login).clip(0, 1)
        engagement_cols.append("login_norm")
    if "assignment_submission_rate" in df.columns:
        df["assignment_norm"] = df["assignment_submission_rate"].clip(0, 1)
        engagement_cols.append("assignment_norm")
    if "quiz_participation" in df.columns:
        engagement_cols.append("quiz_participation")
    if engagement_cols:
        df["engagement_score"]    = df[engagement_cols].mean(axis=1)
        df["low_engagement_flag"] = (df["engagement_score"] < 0.35).astype(int)
    return df


def build_pipeline(X):
    numeric_features     = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()
    transformers = []
    if numeric_features:
        transformers.append(("num", StandardScaler(), numeric_features))
    if categorical_features:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features))
    preprocessor = ColumnTransformer(transformers=transformers)
    if USING_XGBOOST:
        classifier = XGBClassifier(
            n_estimators=200,
            max_depth=3,        # shallower trees = less overfitting
            learning_rate=0.1,  # faster learning on small dataset
            subsample=0.7,
            colsample_bytree=0.7,
            min_child_weight=5,  # higher = more conservative
            gamma=0.2,
            reg_alpha=0.5,       # stronger L1 regularization
            reg_lambda=2.0,      # stronger L2 regularization
            eval_metric="auc",
            random_state=42,
            n_jobs=-1,
)
        print("   Model: XGBoost")
    else:
        classifier = RandomForestClassifier(
            n_estimators=300, max_depth=10, random_state=42, class_weight="balanced"
        )
        print("   Model: Random Forest (fallback)")
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", classifier)])


def apply_smote(X_train, y_train):
    if not USING_SMOTE:
        return X_train, y_train
    dropout_rate = y_train.mean()
    if dropout_rate < 0.40:
        print(f"   Dropout rate {dropout_rate:.1%} — applying SMOTE...")
        smote = SMOTE(random_state=42, k_neighbors=5)
        X_arr = X_train.values if hasattr(X_train, "values") else X_train
        X_res, y_res = smote.fit_resample(X_arr, y_train)
        X_res = pd.DataFrame(X_res, columns=X_train.columns)
        print(f"   After SMOTE: {len(X_res)} rows")
        return X_res, y_res
    return X_train, y_train


def cross_validate_model(pipeline, X_train, y_train):
    print("   Running 5-fold cross-validation...")
    cv        = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    auc_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="roc_auc")
    f1_scores  = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1")
    print(f"\n   AUC-ROC : {auc_scores.mean():.4f} +/- {auc_scores.std():.4f}")
    print(f"   F1 Score: {f1_scores.mean():.4f} +/- {f1_scores.std():.4f}")
    auc = auc_scores.mean()
    if auc >= 0.90:   print("   Excellent model!")
    elif auc >= 0.80: print("   Good model.")
    elif auc >= 0.70: print("   Fair model.")
    else:             print("   Poor model — check your data.")
    return auc_scores.mean(), f1_scores.mean()


def find_best_threshold(pipeline, X_test, y_test):
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    precision_vals, recall_vals, thresholds = precision_recall_curve(y_test, y_proba)
    f1_scores  = 2 * precision_vals * recall_vals / (precision_vals + recall_vals + 1e-8)
    best_idx   = int(np.argmax(f1_scores))
    best_thresh = float(thresholds[best_idx]) if best_idx < len(thresholds) else 0.5
    print(f"   Best threshold: {best_thresh:.3f}  (default was 0.5)")
    return best_thresh, y_proba


def evaluate(pipeline, X_test, y_test, threshold):
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred  = (y_proba >= threshold).astype(int)
    auc       = roc_auc_score(y_test, y_proba)
    f1        = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall    = recall_score(y_test, y_pred, zero_division=0)
    cm        = confusion_matrix(y_test, y_pred)
    print(f"\n   AUC-ROC  : {auc:.4f}")
    print(f"   F1 Score : {f1:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall   : {recall:.4f}")
    print(f"\n   Confusion Matrix:")
    print(f"                  Predicted Safe   Predicted At-Risk")
    print(f"   Actually Safe:      {cm[0,0]:5d}            {cm[0,1]:5d}")
    print(f"   Actually At-Risk:   {cm[1,0]:5d}            {cm[1,1]:5d}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Safe','At-Risk'])}")
    return {"auc_roc": round(auc,4), "f1_score": round(f1,4),
            "precision": round(precision,4), "recall": round(recall,4),
            "threshold": round(threshold,4), "confusion_matrix": cm.tolist()}


if __name__ == "__main__":
    print("=" * 50)
    print(" Student Retention AI — Upgraded Training")
    print(" XGBoost + SMOTE + Cross-Validation")
    print("=" * 50)

    print("\n[1/6] Loading data...")
    X, y = load_data()
    print(f"   {len(X)} students | dropout rate: {y.mean():.1%}")

    print("\n[2/6] Engineering features...")
    X = engineer_features(X)
    print(f"   Features: {X.shape[1]}")

    print("\n[3/6] Splitting 80/20...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n[4/6] Handling class imbalance...")
    X_train, y_train = apply_smote(X_train, y_train)

    print("\n[5/6] Training + cross-validation...")
    pipeline = build_pipeline(X_train)
    cv_auc, cv_f1 = cross_validate_model(pipeline, X_train, y_train)
    pipeline.fit(X_train, y_train)

    print("\n[6/6] Evaluating on test set...")
    threshold, _ = find_best_threshold(pipeline, X_test, y_test)
    metrics      = evaluate(pipeline, X_test, y_test, threshold)

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    with open(THRESHOLD_PATH, "w") as f: json.dump({"threshold": threshold}, f, indent=2)
    with open(METRICS_PATH,   "w") as f: json.dump(metrics, f, indent=2)

    print("\n" + "=" * 50)
    print(f" DONE!  CV AUC={cv_auc:.4f}  Test F1={metrics['f1_score']:.4f}")
    print(" Saved: model.pkl  threshold.json  metrics.json")
    print("=" * 50)