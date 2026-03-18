# Initial Discussion: Architecture and Services - 2026-03-03

# Meeting Information
Meeting Date/Time: March 3, 2026 | 4:00 PM - 5:00 PM IST  
Meeting Purpose: Initial architecture discussion and planning for Student Retention AI system  
Meeting Location: Google Meet  
Note Taker: Antra Gupta, Shourya Jain, Laxmi Sahu

# Repository
Project Repository: https://github.com/gourichouksey/AI-Student-Retention

---
# Attendees
- Gouri Chouksey (Team Leader)
- Antra Gupta (Contributor)
- Shourya Jain (Contributor)
- Laxmi Sahu (Contributor)

---
# Meeting Context
This was the first architecture meeting for the AI-Driven Student Retention & Adaptive Counseling System.  
The team is in the design and implementation phase, aiming to build a full-stack prototype.
The primary goal is to design a clean, scalable, and readable architecture that:
- Follows strong coding and folder structure practices  
- Is easy for contributors to understand  
- Keeps ML, backend, and frontend decoupled  
- Supports explainability and actionable recommendations  
- Enables long-term monitoring of outcomes  
The long-term objective is to build a school-ready system that predicts dropout risk, explains the reasons, recommends interventions, and tracks impact.

---
# High-Level System Overview
The system will implement a full predictive + explainable + actionable pipeline:
Student Data -> ML Model -> SHAP Explanation -> Recommendation Engine -> Dashboard -> Monitoring
The architecture must also support:
- Batch and single-student predictions  
- Persistent storage for interventions and outcomes  
- Scalable model updates  
- Easy integration with school systems  

---
# Core Components (Proposed)
## Component
- Data Ingestion
- ML Model
- SHAP Explanation
- Recommendation Engine
- Backend API (Flask)
- Database (SQLite)
- Frontend Dashboard (React)

---
## Technology Choices (Initial)
### Machine Learning
- Random Forest (initial model)
- XGBoost (planned alternative)
### Explainability
- SHAP (TreeExplainer)
### Backend
- Flask (REST API)
### Frontend
- React (Vite)
### Database
- SQLite (prototype; Postgres planned for production)

---
# Architecture Principles (Under Discussion)
- Modular design with clear service boundaries  
- ML model isolated from API layer  
- Consistent data schema and validation  
- All predictions must include explanation + action  
- Monitoring is mandatory (not optional)  

---
# Weekly Plan (March 1 - March 7)
## Primary Goal:  
Build a working prototype with prediction + explanation + recommendation + monitoring.
### Focus Areas
- Generate synthetic dataset  
- Train baseline ML model  
- Integrate SHAP explanations  
- Build Flask APIs for predict + monitor  
- Build React dashboard (input + risk + actions)  

---
## Workflow & Contribution Plan
- Daily updates and check-ins  
- API contracts documented in `/docs`  
- UI/UX iterations based on feedback  
- Database schema reviewed before changes  
- Weekly demo of end-to-end flow

---
## Other Notes
- The system must always return **Prediction + Explanation + Recommendation** together.  
- Monitoring outcomes is required for evaluation and improvement.  
- Later versions should include model retraining and bias audits.

---

