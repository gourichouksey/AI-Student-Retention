# AI-Student-Retention

# What is it
An AI-Driven Student Retention & Adaptive Counseling System that predicts dropout risk, highlights likely reasons, recommends actions, and helps track interventions over time.

# Why it exists
Schools often recognize risk only after a student has already disengaged. This system helps detect early warning signs, explain the root causes, and enable timely support.

# Core principles
- Early detection over late reaction
- Transparent, explainable AI
- Actionable insights, not just scores
- Human-centered interventions
- Continuous monitoring and improvement

# How it works
1) Student data is collected (attendance, marks, behavior, scholarship, and related profile indicators).
2) Backend ML logic predicts dropout risk probability.
3) Risk drivers and trends are surfaced through analytics/dashboard views.
4) Recommendation logic provides intervention guidance.
5) Dashboard and student views support ongoing monitoring and follow-up.

Languages used in this flow:
- Frontend and UI: JavaScript (React + Vite)
- Backend API and ML pipeline: Python (Flask, scikit-learn, SHAP)
- Styling: CSS/SCSS

```text
How It Works

	 ┌───────────────────────────────────────────────────────────┐
	 │                                                           │
	 ▼                                                           │
   Student data entered                                          │
	 │                                                           │
	 ▼                                                           │
   ┌──────────────┐                                              │
   │   Frontend   │ ─── React form + dashboard input (JavaScript)│
   │ (React/Vite) │                                              │
   └───┬──────────┘                                              │
	   │                                                         │
	   ▼                                                         │
   ┌──────────────┐                                              │
   │   Backend    │ ─── Flask API receives student data (Python) │
   │   /predict   │                                              │
   └───┬──────────┘                                              │
	   │                                                         │
	   ▼                                                         │
   ┌──────────────┐                                              │
   │  ML Model    │ ─── Predicts dropout risk score (Python)     │
   └───┬──────────┘                                              │
	   │                                                         │
	   ▼                                                         │
   ┌──────────────┐                                              │
   │    SHAP      │ ─── Explains top risk factors (Python)       │
   └───┬──────────┘                                              │
	   │                                                         │
	   ▼                                                         │
   ┌───────────────┐                                             │
   │ Recommendation│ ─── Suggests intervention actions           │
   │   Engine      │                                             │
   └───┬───────────┘                                             │
	   │                                                         │
	   ▼                                                         │
   ┌──────────────┐                                              │
   │  Dashboard   │ ─── Shows risk + reasons + next actions      │
   │   Output     │                                              │
   └───┬──────────┘                                              │
	   │                                                         │
	   ▼                                                         │
   Counselor acts ───► Follow-up result? ────────────────────────┘
	   │
	   ▼
   Continue support,
   monitor progress,
   update decisions
```

# Features
- Dropout risk prediction (probability score)
- SHAP explanations (top contributing factors)
- Automatic counseling suggestions
- High-risk student list
- Intervention monitoring and outcomes
- Login/Sign-up (demo mode)


# Setup (Easy Local Setup)

> Run all commands from the project root (`fosshack`) unless noted.

## Prerequisites
- Python 3.11+
- Node.js 18+
- npm

## 1) Clone and open project

```bash
git clone <your-repo-url>
cd fosshack
```

## 2) Install backend dependencies

```powershell
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r backend\requirements.txt
```
If `py` is not available, use `python -m venv .venv` instead.

## 3) Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

## 4) Add environment files
<<<<<<< HEAD
=======

- Create `frontend/.env.local` with:
   ```
   VITE_API_BASE_URL=http://127.0.0.1:5000
   ```
- Create `backend/.env` with:
   ```
   GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com
   ```
>>>>>>> 13fe9b1 (data files)

- Create `frontend/.env.local` with:
   ```
   VITE_API_BASE_URL=http://127.0.0.1:5000
   ```
- Create `backend/.env` with:
   ```
   GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com
   ```
   
## Quick Troubleshooting
- If `.venv\Scripts\activate` fails, use direct Python path commands shown above.
- If OAuth shows `origin_mismatch`, ensure the origin is exactly `http://localhost:5300`.
- If frontend cannot reach backend, start backend first and verify `/health`.
- If `npm run backend` says Python is missing, install Python 3.11+ and re-run the setup steps.

<<<<<<< HEAD
=======

>>>>>>> 13fe9b1 (data files)
# Use cases
- Academic advisors prioritizing at-risk students
- Teachers identifying class-level risk drivers
- Counselors tracking intervention impact
- Administrators monitoring retention programs

# Vision
To give educators a reliable, explainable, and actionable system that improves student retention through early support and measurable interventions.

## License

This project is licensed under the [MIT License](LICENSE).

**Made with ❤️**
