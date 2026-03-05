# Student Retention AI

Full-stack demo for dropout risk prediction, SHAP explanation, recommendations, and monitoring.

## What this does
- Prediction: dropout risk probability
- Explanation: SHAP drivers per student
- Action: automated counseling recommendations
- Monitoring: intervention tracking

## Tech stack
- Backend: Python (Flask)
- ML: scikit-learn, SHAP
- Frontend: React (Vite)
- Database: SQLite

## Prerequisites
- Python 3.11+
- Node.js 18+

## Run (PowerShell)
Backend (Terminal 1):
```
cd C:\Users\gouri\student-retention-ai\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python training\generate_data.py
python training\train.py
python app.py
```

Frontend (Terminal 2):
```
cd C:\Users\gouri\student-retention-ai\frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

## Run (Git Bash)
Backend (Terminal 1):
```
cd /c/Users/gouri/student-retention-ai/backend
./.venv/Scripts/python -m venv .venv
./.venv/Scripts/python -m pip install -r requirements.txt
./.venv/Scripts/python training/generate_data.py
./.venv/Scripts/python training/train.py
./.venv/Scripts/python app.py
```

Frontend (Terminal 2):
```
cd /c/Users/gouri/student-retention-ai/frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

## Notes
- Uses SQLite by default in `backend/db.sqlite3`.
- Training artifacts saved in `backend/training/artifacts/`.
# AI-Student-Retention
