import os
import sys
import shap
import joblib
import numpy as np
import pandas as pd
from pathlib import Path


# Load feature engineering
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "training"))
try:
    from feature_engineering import build_features
    _use_features = True
except Exception:
    _use_features = False


MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "training", "artifacts", "model.pkl"
)

_pipeline     = joblib.load(MODEL_PATH)
_model        = _pipeline.named_steps["model"]
_preprocessor = _pipeline.named_steps["preprocessor"]


def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: x[0] if isinstance(x, (list, np.ndarray)) and len(x) > 0 else x
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.fillna(0)


def explain_student(input_dict):
    try:
        # Step 1 — build DataFrame
        df = pd.DataFrame([input_dict])

        # Step 2 — apply feature engineering
        if _use_features:
            try:
                df = build_features(df)
            except Exception as e:
                print(f"[shap] Feature engineering failed: {e}")

        # Step 3 — clean data
        df = _clean_dataframe(df)

        # Step 4 — align columns with model
        try:
            expected_cols = _preprocessor.feature_names_in_
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = 0.0
            df = df[expected_cols]
        except Exception:
            pass

        # Step 5 — transform and explain
        X_trans = _preprocessor.transform(df)
        explainer = shap.TreeExplainer(_model)
        shap_values = explainer.shap_values(X_trans)
        feature_names = _preprocessor.get_feature_names_out()

        # Step 6 — extract correct SHAP values
        if isinstance(shap_values, list) and len(shap_values) > 1:
            values = shap_values[1][0]
        else:
            values = shap_values[0]
            if hasattr(values, "ndim") and values.ndim > 1:
                values = values[0]

        # Step 7 — get top features
        contribs = dict(zip(feature_names, values.tolist()))
        top = sorted(contribs.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

        return {
            "top_features": [{"name": k, "impact": v} for k, v in top]
        }

    except Exception as e:
        print(f"[shap] Explanation failed: {e}")
        return {"top_features": []}