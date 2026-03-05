import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "training",
    "artifacts",
    "model.pkl"
)

_pipeline = joblib.load(MODEL_PATH)


def predict_risk(input_dict):
    df = pd.DataFrame([input_dict])
    proba = _pipeline.predict_proba(df)[0][1]
    return float(proba)
