# Student Retention AI

Full-stack demo for student dropout risk prediction + SHAP explanation + recommended interventions + monitoring.

Includes scholarship matching + eligibility scoring using your scholarship CSV columns:
`scholarship_id, scholarship_name, provider, category, education_level, min_marks_required, income_limit, scholarship_amount, state, deadline, application_mode`.

## Tech stack
- Backend: Flask + SQLite
- ML: scikit-learn + SHAP
- Frontend: React (Vite)

## Prerequisites (any PC)
- Windows / macOS / Linux
- Python 3.11+
- Node.js 18+

Important: do NOT copy/share your `.venv/` folder. Virtual environments contain machine-specific paths.

## Quick start (local on one PC)

Tip: If you run `npm run dev` from the repo root, it now starts the frontend correctly (it runs Vite from `frontend/`).

### 1) Backend (PowerShell)
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

# one-time: generate demo dataset + train model
python backend\training\generate_data.py
python backend\training\train.py

python backend\app.py
```

Backend runs on `http://127.0.0.1:5000` by default.

### 2) Frontend (PowerShell)
```
cd frontend
npm install
npm run dev
```

VS Code note (fixes red squiggles):
- Open Command Palette → `Python: Select Interpreter` → choose `.venv` in the repo root.

Open: `http://localhost:5173`

Alternative (from repo root):
```
npm install
npm run dev
```

Login options:
- Demo email/password: `demo@retention.ai` / `demo123`
- Google login: see `GOOGLE_CLIENT_ID` in the Config section

## Run on a different PC (setup checklist)
1) Copy/clone the repo
2) Create a new venv on that PC and install backend requirements:
	- `python -m venv backend/.venv`
	- activate it
	- `pip install -r backend/requirements.txt`
3) Install frontend dependencies:
	- `cd frontend`
	- `npm install`
4) Train once (or copy `backend/training/artifacts/` if you already trained):
	- `python backend/training/generate_data.py`
	- `python backend/training/train.py`

## Share on the same LAN (everyone on same Wi‑Fi)

### 1) Start backend so other devices can reach it
On the host PC (the one running the backend):
```
cd backend
$env:HOST="0.0.0.0"
$env:PORT="5000"
$env:FLASK_DEBUG="1"
python app.py
```

Find the host PC IPv4:
```
ipconfig
```
Use the value shown as `IPv4 Address` (example: `10.174.32.186`).

### 2) Start frontend and point it at that backend
Recommended (run frontend on the same host PC):
```
cd frontend
$env:VITE_API_BASE_URL="http://<YOUR_IPV4_ADDRESS>:5000"
npm run dev
```

Everyone opens in a browser: `http://<YOUR_IPV4_ADDRESS>:5173`

Firewall note: allow inbound ports `5000` (backend) and `5173` (Vite dev server).

## Host online (simple approach)

### Backend
Deploy the Flask API to a Python-friendly host (Render/Fly.io/Railway/etc.). Set environment variables:
- `HOST=0.0.0.0`
- `PORT` (usually provided by the platform)
- optional: `DATABASE_URL`, `GOOGLE_CLIENT_ID`

### Frontend
Build and deploy the static site:
```
cd frontend
npm run build
```
Deploy `frontend/dist/` to Netlify/Vercel/static hosting.

Set `VITE_API_BASE_URL` in the frontend host environment to your backend URL (example: `https://your-api.example.com`).

## Data + storage
- SQLite DB default: `backend/instance/db.sqlite3`
- Training artifacts: `backend/training/artifacts/`

Scholarship dataset:
- Default CSV path: `backend/training/scholarship_dataset.csv.csv`
- Override with env var: `SCHOLARSHIP_CSV_PATH`

## Config (env vars)

See the example env files:
- `frontend/.env.example`
- `backend/.env.example`

Backend:
- `HOST` (default `127.0.0.1`, use `0.0.0.0` for LAN/hosting)
- `PORT` (default `5000`)
- `FLASK_DEBUG` (`1` or `0`)
- `DATABASE_URL` (optional)
- `GOOGLE_CLIENT_ID` (optional)

Frontend:
- `VITE_API_BASE_URL` (optional; overrides backend URL)

Google login (frontend):
- `VITE_GOOGLE_CLIENT_ID` (optional; defaults to demo client id)

## Troubleshooting

### “Failed to fetch” when logging in
Usually means the frontend is calling the wrong backend URL.

1) Confirm backend is listening:
```
netstat -ano | findstr ":5000"
```

2) Test backend locally (host PC):
```
$payload = @{ email = 'demo@retention.ai'; password = 'demo123' } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:5000/auth/login -Method Post -ContentType 'application/json' -Body $payload
```

3) If using LAN: make sure `VITE_API_BASE_URL` uses the host PC IPv4 from `ipconfig`.

### Google sign-in fails on LAN IP
Google Identity often requires a secure origin (HTTPS), except for `http://localhost`.
- For dev, prefer opening the frontend at `http://localhost:5173`.
- If you must use a LAN URL (like `http://172.20.10.4:5173`), create your own OAuth client and configure:
	- `VITE_GOOGLE_CLIENT_ID` in the frontend
	- `GOOGLE_CLIENT_ID` in the backend
	- Authorized JavaScript origins in Google Cloud Console (include your dev URL)

