# AI-Student-Retention

# What is it  
An AI‑Driven Student Retention & Adaptive Counseling System that predicts dropout risk, explains the reasons, recommends actions, and tracks interventions over time.

# Why it exists  
Schools often recognize risk only after a student has already disengaged. This system helps detect early warning signs, explain the root causes, and enable timely support.

# Core principles  
- Early detection over late reaction  
- Transparent, explainable AI  
- Actionable insights, not just scores  
- Human‑centered interventions  
- Continuous monitoring and improvement

# How it works  
1) Student data is collected (attendance, grades, backlogs, income, parents’ education, scholarship status).  
2) A ML model predicts dropout probability.  
3) SHAP explains key contributors for each student.  
4) Rules generate counseling recommendations.  
5) The dashboard shows risk, reasons, actions, and intervention status.

# Features  
- Dropout risk prediction (probability score)  
- SHAP explanations (top contributing factors)  
- Automatic counseling suggestions  
- High‑risk student list  
- Intervention monitoring and outcomes  
- Login/Sign‑up (demo mode)

# Run locally

## Backend (API)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
python backend/services/api_server.py
```

## Frontend
Open a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on port 5173 and calls backend on port 5000.

# Use cases  
- Academic advisors prioritizing at‑risk students  
- Teachers identifying class‑level risk drivers  
- Counselors tracking intervention impact  
- Administrators monitoring retention programs

# Vision  
To give educators a reliable, explainable, and actionable system that improves student retention through early support and measurable interventions.
Contributing  
- Fork the repo  
- Create a feature branch  
- Commit your changes  
- Open a pull request with a clear description

## License

This project is licensed under the [MIT License](LICENSE).

