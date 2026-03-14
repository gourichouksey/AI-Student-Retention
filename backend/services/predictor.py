import os
import json
import joblib
import pandas as pd
import sys
from pathlib import Path

# Make sure feature_engineering.py can be found
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "training"))

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "training", "artifacts", "model.pkl"
)
THRESHOLD_PATH = os.path.join(
    os.path.dirname(__file__), "..", "training", "artifacts", "threshold.json"
)

# Load model once when server starts
_pipeline = joblib.load(MODEL_PATH)

# Load your tuned threshold (e.g. 0.185 instead of wrong 0.5)
try:
    with open(THRESHOLD_PATH) as f:
        _threshold = json.load(f).get("threshold", 0.5)
    print(f"[predictor] Loaded threshold: {_threshold:.3f}")
except Exception:
    _threshold = 0.5
    print("[predictor] threshold.json not found — using 0.5")

# Load your feature engineering
try:
    from feature_engineering import build_features
    _use_features = True
    print("[predictor] Feature engineering loaded ✓")
except Exception:
    _use_features = False
    print("[predictor] Feature engineering not found — using raw columns")


def predict_risk(input_dict: dict) -> float:
    """
    Takes raw student data dict, returns dropout risk probability (0.0 - 1.0).

    Steps:
      1. Convert dict to DataFrame
      2. Apply feature engineering (adds 15+ new columns)
      3. Run through XGBoost pipeline
      4. Return probability score
    """
    # Step 1 — convert to DataFrame
    df = pd.DataFrame([input_dict])

    # Step 2 — apply your feature engineering
    if _use_features:
        try:
            df = build_features(df)
        except Exception as e:
            print(f"[predictor] Feature engineering failed: {e} — using raw data")

    # Step 3 — drop non-numeric columns that model can't use
    df = df.select_dtypes(include=["number"]).fillna(0)

    # Step 4 — predict probability
    try:
        proba = _pipeline.predict_proba(df)[0][1]
    except Exception as e:
        print(f"[predictor] Prediction error: {e}")
        # Try with raw input as fallback
        df_raw = pd.DataFrame([input_dict])
        df_raw = df_raw.select_dtypes(include=["number"]).fillna(0)
        proba = _pipeline.predict_proba(df_raw)[0][1]

    return float(proba)


def predict_risk_with_label(input_dict: dict) -> dict:
    """
    Extended version — returns probability + risk level label.
    Uses your tuned threshold instead of default 0.5.

    Returns:
        {
          "probability": 0.73,
          "risk_level": "High",    # High / Medium / Low
          "risk_score": 7.3,       # 0-10 for dashboard gauge
          "threshold_used": 0.185
        }
    """
    prob = predict_risk(input_dict)

    # Use YOUR tuned threshold
    if prob >= _threshold + 0.3:
        level = "High"
    elif prob >= _threshold:
        level = "Medium"
    else:
        level = "Low"

    return {
        "probability":     round(prob, 4),
        "risk_level":      level,
        "risk_score":      round(prob * 10, 1),
        "threshold_used":  _threshold,
    }