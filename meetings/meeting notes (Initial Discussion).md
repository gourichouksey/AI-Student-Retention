# Initial Discussion: Architecture Planning - 2026-03-03

## Meeting Information

**Meeting Date/Time:** March 3, 2026 | 4:00 PM – 5:00 PM IST 

**Meeting Purpose:** Initial architecture discussion and planning for the Student Retention AI System

**Meeting Location:** Google Meet

**Note Takers:** Antra Gupta, Shourya Jain, Laxmi Sahu

---

## Repository

**Project Repository:**
https://github.com/gourichouksey/AI-Student-Retention

---

## Attendees

* **Gouri Chouksey** (Team Leader)
* **Antra Gupta** (Contributor)
* **Shourya Jain** (Contributor)
* **Laxmi Sahu** (Contributor)

---

## Meeting Context

This was the first architecture meeting for the **AI-Driven Student Retention & Adaptive Counseling System**.

The team is currently in the **design and implementation phase**, aiming to build a **full-stack prototype**.

The primary goal is to design a **clean, scalable, and readable architecture** that:

* Follows strong coding and folder structure practices
* Is easy for contributors to understand
* Keeps ML, backend, and frontend decoupled
* Supports explainability and actionable recommendations
* Enables long-term monitoring of outcomes

The long-term objective is to build a **school-ready system** that:

* Predicts student dropout risk
* Explains the reasons behind the prediction
* Recommends appropriate interventions
* Tracks the impact of those interventions

---

## High-Level System Overview

The system will implement a complete **Predictive + Explainable + Actionable pipeline**:

```
Student Data → ML Model → SHAP Explanation → Recommendation Engine → Dashboard → Monitoring
```

The architecture must also support:

* Batch predictions (multiple students)
* Single-student predictions
* Persistent storage for interventions and outcomes
* Scalable model updates
* Easy integration with school systems

---

## Core Components (Proposed)

| Component                  | Description                       |
| -------------------------- | --------------------------------- |
| Data Ingestion             | Collect and process student data  |
| ML Model                   | Predict dropout risk              |
| SHAP Explanation           | Explain why a student is at risk  |
| Recommendation Engine      | Suggest counseling actions        |
| Backend API (Flask)        | Serve predictions and data        |
| Database (SQLite)          | Store student and prediction data |
| Frontend Dashboard (React) | Interface for teachers/admins     |

---

## Technology Choices (Initial)

### Machine Learning

* Random Forest (initial model)
* XGBoost (planned alternative)

### Explainability

* SHAP (TreeExplainer)

### Backend

* Flask (REST API)

### Frontend

* React (Vite)

### Database

* SQLite (prototype)
* PostgreSQL planned for production

---

## Architecture Principles (Under Discussion)

* Modular design with clear service boundaries
* ML model isolated from the API layer
* Consistent data schema and validation
* All predictions must include **explanation + action**
* Monitoring is **mandatory, not optional**

---

## Weekly Plan (March 1 – March 7)

**Primary Goal:**
Build a working prototype with **prediction, explanation, recommendation, and monitoring**.

### Focus Areas

* Generate synthetic dataset
* Train baseline ML model
* Integrate SHAP explanations
* Build Flask APIs for prediction and monitoring
* Build React dashboard (input, risk, actions)

---

## Responsibilities

| Member         | Role              |
| -------------- | ----------------- |
| Gouri Chouksey | Team Leader       |
| Antra Gupta    | Contributor       |
| Laxmi Sahu     | Contributor       |
| Shourya Jain   | Contributor       |
---

## Workflow & Contribution Plan

* Daily updates and check-ins
* API contracts documented in `/docs`
* UI/UX iterations based on team feedback
* Database schema reviewed before changes
* Weekly end-to-end demo

---

## Action Items

| Done?  | Item                                      |
| -------| ----------------------------------------- |
| ☑      | Define schema for student + prediction    |
| ☑      | Build ML pipeline (training + prediction) |
| ⬜     | Implement SHAP explanations               |
| ⬜     | Build React dashboard UI                  |
| ⬜     | Integrate monitoring API into UI          |
| ⬜     | End-to-end demo                           |

---

## Other Notes

* The system must always return **Prediction + Explanation + Recommendation** together.
* Monitoring outcomes are required for evaluation and system improvement.

### Future Versions Should Include

* Model retraining
* Bias audits
* Performance monitoring
