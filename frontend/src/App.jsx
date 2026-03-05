import React, { useEffect, useState } from "react";
import { predictStudent, fetchHighRisk, fetchMonitoring, createAction, signup, login } from "./api";
import RiskCard from "./components/RiskCard";
import ShapPlot from "./components/ShapPlot";
import Recommendations from "./components/Recommendations";
import HighRiskList from "./components/HighRiskList";
import MonitoringTable from "./components/MonitoringTable";
import "./styles.css";

export default function App() {
  const [result, setResult] = useState(null);
  const [highRisk, setHighRisk] = useState([]);
  const [monitoring, setMonitoring] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState("dark");
  const [authMode, setAuthMode] = useState("login");
  const [user, setUser] = useState(null);
  const [auth, setAuth] = useState({ name: "", email: "", password: "" });
  const [activeTab, setActiveTab] = useState("predict");
  const [stage, setStage] = useState("auth");

  const [form, setForm] = useState({
    student_id: 1,
    attendance_pct: 58,
    backlogs: 2,
    family_income: 120000,
    parents_edu: "school",
    scholarship_status: "no",
    grade_math: 42,
    grade_science: 55,
    grade_english: 60,
  });

  async function runDemo() {
    setLoading(true);
    setError("");
    try {
      const res = await predictStudent(form);
      setResult(res);
      if (res?.recommendations?.length) {
        await createAction({
          student_id: form.student_id,
          action: res.recommendations[0],
          status: "planned",
          outcome: "Pending",
        });
      }
      const hr = await fetchHighRisk();
      setHighRisk(hr.students || []);
      const mon = await fetchMonitoring();
      setMonitoring(mon.actions || []);
    } catch (err) {
      setError("Request failed. Check backend at http://127.0.0.1:5000");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    runDemo();
  }, []);

  function updateField(e) {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "parents_edu" || name === "scholarship_status" ? value : Number(value)
    }));
  }

  function updateAuth(e) {
    const { name, value } = e.target;
    setAuth((prev) => ({ ...prev, [name]: value }));
  }

  async function handleAuth() {
    setError("");
    try {
      if (authMode === "login") {
        const res = await login({ email: auth.email, password: auth.password });
        if (res.error) throw new Error(res.error);
        setUser(res);
        setStage("intro");
      } else {
        const res = await signup({ name: auth.name, email: auth.email, password: auth.password });
        if (res.error) throw new Error(res.error);
        setUser(res);
        setStage("intro");
      }
    } catch (err) {
      setError(err.message || "Auth failed");
    }
  }

  return (
    <div className={`page ${theme} full`}>
      <header className="hero">
        <div>
          <div className="eyebrow reveal">AI Student Retention</div>
          <h1 className="reveal">Early Warning & Counseling</h1>
          <p className="reveal">
            Spot risk early, understand the reason, and take the right action fast.
          </p>
        </div>
        <div className="hero-actions">
          <div className="auth">
            <button className="ghost" onClick={() => setAuthMode("login")}>Login</button>
            <button className="ghost" onClick={() => setAuthMode("signup")}>Sign up</button>
          </div>
          <button
            className="toggle"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? "Light mode" : "Dark mode"}
          </button>
          {user && (
            <button className="btn" onClick={runDemo} disabled={loading}>
              {loading ? "Running..." : "Refresh Demo"}
            </button>
          )}
        </div>
      </header>

      {!user ? (
        <section className="auth-shell fullscreen">
          <div className="card auth-card">
            <div className="card-header">
              <h3>{authMode === "login" ? "Login" : "Sign up"}</h3>
              <span className="hint">Secure local demo access</span>
            </div>
            <div className="form-grid">
              {authMode === "signup" && (
                <label>
                  Name
                  <input name="name" type="text" value={auth.name} onChange={updateAuth} />
                </label>
              )}
              <label>
                Email
                <input name="email" type="email" value={auth.email} onChange={updateAuth} />
              </label>
              <label>
                Password
                <input name="password" type="password" value={auth.password} onChange={updateAuth} />
              </label>
            </div>
            <div className="form-actions">
              <button className="btn" onClick={handleAuth}>
                {authMode === "login" ? "Login" : "Create Account"}
              </button>
              <span className="hint">No external auth, stored locally for demo.</span>
            </div>
            {error && <div className="error">{error}</div>}
          </div>
          <div className="auth-story">
            <h2 className="reveal">Welcome to early intervention</h2>
            <p className="reveal">
              A single dashboard that predicts dropout risk, explains the cause, recommends actions,
              and tracks outcomes so schools can respond before it is too late.
            </p>
          </div>
        </section>
      ) : stage === "intro" ? (
        <section className="slide">
          <h2>Why this platform exists</h2>
          <p>
            Schools often see dropout signals too late. This system finds the risk early, explains the
            drivers, and recommends immediate actions that staff can track.
          </p>
          <div className="feature-list">
            <div className="feature-card">
              <div className="icon">P</div>
              <div>
                <h4>Prediction</h4>
                <p>Reliable risk scoring using Random Forest/XGBoost patterns.</p>
              </div>
            </div>
            <div className="feature-card">
              <div className="icon">E</div>
              <div>
                <h4>Explanation</h4>
                <p>SHAP reveals what increases or decreases risk for each student.</p>
              </div>
            </div>
            <div className="feature-card">
              <div className="icon">A</div>
              <div>
                <h4>Action</h4>
                <p>Auto‑recommended interventions for financial, academic, and attendance issues.</p>
              </div>
            </div>
            <div className="feature-card">
              <div className="icon">M</div>
              <div>
                <h4>Monitoring</h4>
                <p>Track interventions and outcomes across time.</p>
              </div>
            </div>
          </div>
          <div className="form-actions bottom">
            <button className="btn" onClick={() => setStage("dashboard")}>Continue to Dashboard</button>
            <span className="hint">You can return to this from the top tabs anytime.</span>
          </div>
        </section>
      ) : (
        <>
          <section className="tabs">
            <button
              className={activeTab === "predict" ? "tab active" : "tab"}
              onClick={() => setActiveTab("predict")}
            >
              Predict
            </button>
            <button
              className={activeTab === "monitoring" ? "tab active" : "tab"}
              onClick={() => setActiveTab("monitoring")}
            >
              Monitoring
            </button>
            <button
              className={activeTab === "insights" ? "tab active" : "tab"}
              onClick={() => setActiveTab("insights")}
            >
              Insights
            </button>
          </section>

          <section className="card form">
            <div className="card-header">
              <h3>Student Data Input</h3>
              <span className="hint">Fill in values and click Predict</span>
            </div>
            <div className="form-grid">
              <label>
                Student ID
                <input name="student_id" type="number" value={form.student_id} onChange={updateField} />
              </label>
              <label>
                Attendance %
                <input name="attendance_pct" type="number" value={form.attendance_pct} onChange={updateField} />
              </label>
              <label>
                Backlogs
                <input name="backlogs" type="number" value={form.backlogs} onChange={updateField} />
              </label>
              <label>
                Family Income
                <input name="family_income" type="number" value={form.family_income} onChange={updateField} />
              </label>
              <label>
                Parents Education
                <select name="parents_edu" value={form.parents_edu} onChange={updateField}>
                  <option value="none">None</option>
                  <option value="school">School</option>
                  <option value="college">College</option>
                  <option value="postgrad">Postgrad</option>
                </select>
              </label>
              <label>
                Scholarship
                <select name="scholarship_status" value={form.scholarship_status} onChange={updateField}>
                  <option value="yes">Yes</option>
                  <option value="no">No</option>
                </select>
              </label>
              <label>
                Math Grade
                <input name="grade_math" type="number" value={form.grade_math} onChange={updateField} />
              </label>
              <label>
                Science Grade
                <input name="grade_science" type="number" value={form.grade_science} onChange={updateField} />
              </label>
              <label>
                English Grade
                <input name="grade_english" type="number" value={form.grade_english} onChange={updateField} />
              </label>
            </div>
            <div className="form-actions">
              <button className="btn" onClick={runDemo} disabled={loading}>
                {loading ? "Predicting..." : "Predict"}
              </button>
              <span className="hint">Model runs locally, no external calls.</span>
            </div>
            {error && <div className="error">{error}</div>}
          </section>

          {activeTab === "predict" && (
            <section className="grid">
              <RiskCard score={result?.risk_score} />
              <ShapPlot data={result?.explanation} />
              <Recommendations items={result?.recommendations || []} />
              <HighRiskList students={highRisk} />
            </section>
          )}

          {activeTab === "monitoring" && (
            <section className="grid">
              <MonitoringTable actions={monitoring} />
              <HighRiskList students={highRisk} />
            </section>
          )}

          {activeTab === "insights" && (
            <section className="grid">
              <ShapPlot data={result?.explanation} />
              <RiskCard score={result?.risk_score} />
              <Recommendations items={result?.recommendations || []} />
            </section>
          )}

        </>
      )}
    </div>
  );
}
