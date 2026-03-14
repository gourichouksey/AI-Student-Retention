# Fresh Contribution

A full-stack proof-of-concept for risk prediction and monitoring.

## Project Structure

- `backend/` – Python services (model training, prediction, explainability)
  - `training/` – data processing + model training scripts
  - `services/` – prediction and SHAP explain endpoints
- `demo/` – sample data and other demo assets
- `frontend/` – web UI built with Vite + React

## Getting Started

### Backend (Python)

1. Create a virtual environment and install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. Run the predictor service (adjust as needed):

```bash
python backend/services/predictor.py
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## Notes

- Update `backend/services/predictor.py` to point at your trained model.
- The frontend calls the backend API via `src/api.js`.
## Contributors

| Name | Role | Contribution |
|------|------|-------------|
| Antra Gupta | DS/ML + Backend | Upgraded ML model from Random Forest to XGBoost, built feature engineering module (9→25 features), fixed SHAP explainer, improved recall to 89.4% |