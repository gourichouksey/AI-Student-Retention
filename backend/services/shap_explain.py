import os
import shap
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
_model = _pipeline.named_steps["model"]
_preprocessor = _pipeline.named_steps["preprocessor"]


def explain_student(input_dict):
    df = pd.DataFrame([input_dict])
    X_trans = _preprocessor.transform(df)

    explainer = shap.TreeExplainer(_model)
    shap_values = explainer.shap_values(X_trans)

    feature_names = _preprocessor.get_feature_names_out()
    if isinstance(shap_values, list) and len(shap_values) > 1:
        values = shap_values[1][0]
    else:
        values = shap_values[0]
        if hasattr(values, "ndim") and values.ndim > 1:
            values = values[0]

    contribs = dict(zip(feature_names, values.tolist()))

    top = sorted(contribs.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

    return {
        "top_features": [{"name": k, "impact": v} for k, v in top]
    }
