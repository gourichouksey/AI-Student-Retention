import React, { useEffect, useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { API_BASE_URL, predictStudent, fetchHighRisk, signup, login, googleLogin, chatWithAi } from "./api";
import RiskCard from "./components/RiskCard";
import ShapPlot from "./components/ShapPlot";
import Recommendations from "./components/Recommendations";
import HighRiskList from "./components/HighRiskList";
import "./styles.css";

const flowSteps = [
  {
    code: "SD",
    title: "Student Data",
    desc: "Grades, attendance, income",
  },
  {
    code: "AI",
    title: "AI Model",
    desc: "Risk prediction + SHAP",
  },
  {
    code: "DR",
    title: "Dropout Risk",
    desc: "Explain why it is high",
  },
  {
    code: "EI",
    title: "Early Intervention",
    desc: "Targeted action plan",
  },
];

const featureCards = [
  {
    title: "Risk Prediction",
    bullets: ["Attendance analysis", "GPA evaluation", "Behavior patterns", "Risk score generation"],
    impact: "Flags risk early so counselors act before dropout happens.",
  },
  {
    title: "Analytics Dashboard",
    bullets: ["Dropout statistics", "Retention rate", "Department insights", "Attendance trends"],
    impact: "Shows trends at a glance for faster decision making.",
  },
  {
    title: "AI Recommendations",
    bullets: ["Academic counseling", "Attendance alerts", "Performance monitoring", "Personalized support"],
    impact: "Auto-suggests the next best action for each student.",
  },
  {
    title: "Monitoring",
    bullets: ["Intervention tracking", "Outcome logging", "Follow-up reminders", "Progress snapshots"],
    impact: "Tracks outcomes and closes the loop on interventions.",
  },
];

const faqItems = [
  {
    q: "How does the system predict risk?",
    a: "It analyzes attendance, grades, and context to estimate dropout probability with an AI model.",
  },
  {
    q: "What makes the prediction explainable?",
    a: "SHAP highlights the most influential factors for each student so decisions are transparent.",
  },
  {
    q: "Can schools act immediately?",
    a: "Yes. Recommended actions are generated with a monitoring trail for follow-up.",
  },
];

const scholarshipLinks = [
  {
    name: "National Scholarship Portal (India)",
    desc: "Central scholarships for UG/PG students",
    category: "SC/ST/OBC/General (varies by scheme)",
    url: "https://scholarships.gov.in/",
  },
  {
    name: "MP State Scholarship Portal",
    desc: "State-level scholarships and fee reimbursements",
    category: "SC/ST/OBC/General (state schemes)",
    url: "https://scholarshipportal.mp.nic.in/",
  },
  {
    name: "AICTE Pragati (Women)",
    desc: "Support for women in technical education",
    category: "Women (General/OBC/SC/ST)",
    url: "https://www.aicte-india.org/schemes/students-development-schemes/Pragati",
  },
  {
    name: "AICTE Saksham (PwD)",
    desc: "Scholarship for students with disabilities",
    category: "PwD (General/OBC/SC/ST)",
    url: "https://www.aicte-india.org/schemes/students-development-schemes/Saksham",
  },
  {
    name: "UGC Scholarships",
    desc: "Merit and special assistance programs",
    category: "General/Reserved (scheme-specific)",
    url: "https://ugc.ac.in/pg/scholarships.aspx",
  },
];

export default function App({ googleOauthEnabled = false }) {
  const [slide, setSlide] = useState(1);
  const [menuOpen, setMenuOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [user, setUser] = useState(null);
  const [auth, setAuth] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [featureIndex, setFeatureIndex] = useState(0);

  const [result, setResult] = useState(null);
  const [highRisk, setHighRisk] = useState([]);
  const [loading, setLoading] = useState(false);

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

  const [supportForm, setSupportForm] = useState({ name: "", email: "", question: "" });
  const [supportNote, setSupportNote] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState([
    { role: "ai", text: "Hi! Ask about risk, interventions, or scholarships." }
  ]);

  useEffect(() => {
    const timer = setInterval(() => {
      setFeatureIndex((prev) => (prev + 1) % featureCards.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!user) return;
    runDemo();
  }, [user]);

  async function runDemo() {
    setLoading(true);
    setError("");
    try {
      const res = await predictStudent(form);
      setResult(res);
      const hr = await fetchHighRisk();
      setHighRisk(hr.students || []);
    } catch (err) {
      setError(`Request failed. Check backend at ${API_BASE_URL}`);
    } finally {
      setLoading(false);
    }
  }

  function updateField(e) {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "parents_edu" || name === "scholarship_status" ? value : Number(value),
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
        setSlide(2);
      } else {
        const res = await signup({ name: auth.name, email: auth.email, password: auth.password });
        if (res.error) throw new Error(res.error);
        setUser(res);
        setSlide(2);
      }
    } catch (err) {
      setError(err.message || "Auth failed");
    }
  }

  async function handleGoogleAuth(token) {
    setError("");
    try {
      const res = await googleLogin(token);
      if (res.error) {
        const message = res.details ? `${res.error}: ${res.details}` : res.error;
        throw new Error(message);
      }
      setUser(res);
      setSlide(2);
    } catch (err) {
      setError(err.message || "Google login failed");
    }
  }

  function navigateTo(target) {
    setMenuOpen(false);
    if (!user && target > 1) {
      setError("Please login to continue.");
      setSlide(1);
      return;
    }
    setSlide(target);
  }

  function openChatSupport() {
    setMenuOpen(false);
    if (!user) {
      setError("Please login to continue.");
      setSlide(1);
      return;
    }
    setSlide(4);
    setChatOpen(true);
  }

  function handleSupportChange(e) {
    const { name, value } = e.target;
    setSupportForm((prev) => ({ ...prev, [name]: value }));
  }

  function submitSupport(e) {
    e.preventDefault();
    setSupportNote("Thanks! Our team will respond within 24 hours.");
    setSupportForm({ name: "", email: "", question: "" });
  }

  async function sendChat(e) {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const userMsg = { role: "user", text: chatInput.trim() };
    const lower = chatInput.trim().toLowerCase();

    // Optimistic UI: show the user message immediately.
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");

    try {
      const payload = [...chatMessages, userMsg];
      const res = await chatWithAi(payload);
      if (res?.reply) {
        setChatMessages((prev) => [...prev, { role: "ai", text: res.reply }]);
        return;
      }
      throw new Error(res?.error || "Chat failed");
    } catch (err) {
      // Fallback: keep the chat usable even if Gemini key isn't configured.
      let reply = "Thanks! I can help with risk, interventions, or scholarships.";
      if (lower.includes("scheme") || lower.includes("scholarship")) {
        reply =
          "Scholarship schemes: National Scholarship Portal, MP State Scholarship Portal, AICTE Pragati (Women), and UGC Scholarships. Check the links in Support.";
      }
      setChatMessages((prev) => [...prev, { role: "ai", text: reply }]);
    }
  }

  const canPrev = slide > 1;
  const canNext = slide < 4 && user;

  return (
    <div className="page light full">
      <nav className="top-nav">
        <div className="brand">
          <span className="brand-dot" />
          StudentAI
        </div>
        <div className="nav-actions">
          {user && <span className="user-pill">{user.name || "User"}</span>}
          <div className="menu-wrap">
            <button className="menu-button" onClick={() => setMenuOpen((prev) => !prev)}>
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </button>
            {menuOpen && (
              <div className="menu">
                <button onClick={() => navigateTo(1)}>Login / Signup</button>
                <button onClick={() => navigateTo(2)}>Features</button>
                <button onClick={() => navigateTo(3)}>Dashboard</button>
                <button onClick={() => navigateTo(4)}>Support</button>
                <button onClick={openChatSupport}>Chat Support</button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {slide === 1 && (
        <section className="slide login-slide">
          <div className="login-card">
            <div className="login-header">
              <h1>AI Student Retention System</h1>
              <p>Sign in to access predictive insights and early intervention tools.</p>
            </div>
            <div className="auth-toggle">
              <button className={authMode === "login" ? "tab active" : "tab"} onClick={() => setAuthMode("login")}>
                Login
              </button>
              <button className={authMode === "signup" ? "tab active" : "tab"} onClick={() => setAuthMode("signup")}>
                Sign up
              </button>
            </div>
            <div className="form-grid two">
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
              <div className="google-wrap">
                {googleOauthEnabled ? (
                  <GoogleLogin
                    onSuccess={(credentialResponse) => handleGoogleAuth(credentialResponse.credential)}
                    onError={() =>
                      setError(
                        "Google login failed. In Google Cloud Console add this origin: " +
                          window.location.origin
                      )
                    }
                  />
                ) : (
                  <div className="hint">
                    Google login disabled. Set VITE_GOOGLE_CLIENT_ID in frontend/.env.local and authorize origin:
                    {" "}
                    {window.location.origin}
                  </div>
                )}
              </div>
            </div>
            {error && <div className="error">{error}</div>}
          </div>
          <div className="login-hero">
            <h2>Predict Student Dropout Before It Happens</h2>
            <p>
              AI powered system that helps institutions identify at-risk students and take preventive actions
              to improve retention.
            </p>
            <div className="hero-metrics">
              <div>
                <span>Total Students</span>
                <strong>1,200</strong>
              </div>
              <div>
                <span>Students at Risk</span>
                <strong>84</strong>
              </div>
              <div>
                <span>Retention Rate</span>
                <strong>92%</strong>
              </div>
            </div>
          </div>
        </section>
      )}

      {slide === 2 && (
        <section className="slide feature-slide">
          <div className="feature-hero">
            <h1>AI Powered Tools</h1>
            <p>Smart features designed to improve student success with early, explainable interventions.</p>
          </div>
          <div className="flow-grid">
            {flowSteps.map((step) => (
              <div key={step.code} className="flow-card">
                <div className="flow-icon">{step.code}</div>
                <div>
                  <h3>{step.title}</h3>
                  <p>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="swap-cards">
            {featureCards.map((card, index) => (
              <div key={card.title} className={`swap-card ${index === featureIndex ? "active" : ""}`}>
                <div className="swap-card-inner">
                  <div className="swap-face swap-front">
                    <h3>{card.title}</h3>
                    <ul>
                      {card.bullets.map((b) => (
                        <li key={b}>{b}</li>
                      ))}
                    </ul>
                    <button className="btn small">Explore</button>
                  </div>
                  <div className="swap-face swap-back">
                    <h3>Impact</h3>
                    <p>{card.impact}</p>
                    <button className="ghost">View Example</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {slide === 3 && (
        <section className="slide dashboard-slide">
          <div className="dashboard-header">
            <h1>AI Student Retention Dashboard</h1>
            <p>Predict dropout risks early and help institutions take preventive actions.</p>
          </div>
          <section className="card form">
            <div className="card-header">
              <h3>Student Data Input</h3>
              <span className="hint">Fill in values and click Predict</span>
            </div>
            <div className="form-grid dashboard-form-grid">
              <label>
                Student ID
                <input
                  name="student_id"
                  type="number"
                  min="1"
                  step="1"
                  placeholder="e.g. 1"
                  value={form.student_id}
                  onChange={updateField}
                />
              </label>
              <label>
                Attendance %
                <input
                  name="attendance_pct"
                  type="number"
                  min="0"
                  max="100"
                  step="1"
                  placeholder="0 - 100"
                  value={form.attendance_pct}
                  onChange={updateField}
                />
              </label>
              <label>
                Backlogs
                <input
                  name="backlogs"
                  type="number"
                  min="0"
                  step="1"
                  placeholder="e.g. 0"
                  value={form.backlogs}
                  onChange={updateField}
                />
              </label>
              <label>
                Family Income
                <input
                  name="family_income"
                  type="number"
                  min="0"
                  step="1000"
                  placeholder="e.g. 120000"
                  value={form.family_income}
                  onChange={updateField}
                />
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
                <input
                  name="grade_math"
                  type="number"
                  min="0"
                  max="100"
                  step="1"
                  placeholder="0 - 100"
                  value={form.grade_math}
                  onChange={updateField}
                />
              </label>
              <label>
                Science Grade
                <input
                  name="grade_science"
                  type="number"
                  min="0"
                  max="100"
                  step="1"
                  placeholder="0 - 100"
                  value={form.grade_science}
                  onChange={updateField}
                />
              </label>
              <label>
                English Grade
                <input
                  name="grade_english"
                  type="number"
                  min="0"
                  max="100"
                  step="1"
                  placeholder="0 - 100"
                  value={form.grade_english}
                  onChange={updateField}
                />
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
          <section className="grid">
            <RiskCard score={result?.risk_score} />
            <ShapPlot data={result?.explanation} />
            <Recommendations items={result?.recommendations || []} />
            <HighRiskList students={highRisk} />
          </section>
          <section className="card scholarship-section">
            <div className="card-header">
              <h3>Scholarship Matches</h3>
              <span className="hint">Based on income + marks</span>
            </div>
            <div className="scroll-area">
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Amount</th>
                      <th>Deadline</th>
                      <th>Eligible</th>
                      <th>Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(!result?.scholarships || result.scholarships.length === 0) && (
                      <tr>
                        <td colSpan="5">Run Predict to see scholarship matches</td>
                      </tr>
                    )}
                    {(result?.scholarships || []).map((s) => (
                      <tr key={s.scholarship_id}>
                        <td className="cell-wrap">
                          <strong>{s.scholarship_name}</strong>
                          <div className="hint">{s.provider} • {s.state}</div>
                        </td>
                        <td>{s.scholarship_amount}</td>
                        <td>{s.deadline}</td>
                        <td>
                          <span className={s.eligible ? "badge ok" : "badge no"}>
                            {s.eligible ? "Yes" : "No"}
                          </span>
                        </td>
                        <td>
                          {typeof s.eligibility_probability === "number"
                            ? `${Math.round(s.eligibility_probability * 100)}%`
                            : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
          <section className="grid">
            <div className="card scholarship-section">
              <h3>Scholarship Schemes (India)</h3>
              <div className="scroll-area">
                <div className="scholarship-grid">
                  {scholarshipLinks.map((link) => (
                    <a key={link.name} href={link.url} target="_blank" rel="noreferrer">
                      <strong>{link.name}</strong>
                      <span>{link.desc}</span>
                      <span className="category">Category: {link.category}</span>
                      <span className="url">{link.url}</span>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </section>
        </section>
      )}

      {slide === 4 && (
        <section className="slide support-slide">
          <div className="support-header">
            <h1>Customer Support</h1>
            <p>Ask a question and our team will respond quickly.</p>
          </div>
          <div className="support-grid">
            <div className="card">
              <h3>Scholarship Links (India)</h3>
              <div className="link-list">
                {scholarshipLinks.map((link) => (
                  <a key={link.name} href={link.url} target="_blank" rel="noreferrer">
                    <strong>{link.name}</strong>
                    <span>{link.desc}</span>
                  </a>
                ))}
              </div>
            </div>
            <div className="card">
              <h3>Frequently Asked Questions</h3>
              <div className="faq">
                {faqItems.map((item) => (
                  <div key={item.q} className="faq-item">
                    <h4>{item.q}</h4>
                    <p>{item.a}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="card">
              <h3>Ask a Question</h3>
              <form className="form-grid" onSubmit={submitSupport}>
                <label>
                  Name
                  <input name="name" value={supportForm.name} onChange={handleSupportChange} required />
                </label>
                <label>
                  Email
                  <input name="email" type="email" value={supportForm.email} onChange={handleSupportChange} required />
                </label>
                <label>
                  Question
                  <textarea name="question" rows="4" value={supportForm.question} onChange={handleSupportChange} required />
                </label>
                <button className="btn" type="submit">Submit</button>
                {supportNote && <span className="hint">{supportNote}</span>}
              </form>
              <div className="chat-panel embedded">
                <div className="chat-header">
                  <h4>Student AI Chat</h4>
                  <button className="ghost" onClick={() => setChatOpen((prev) => !prev)}>
                    {chatOpen ? "Hide" : "Show"}
                  </button>
                </div>
                {chatOpen && (
                  <>
                    <div className="chat-body">
                      {chatMessages.map((msg, idx) => (
                        <div key={idx} className={`chat-bubble ${msg.role}`}>
                          {msg.text}
                        </div>
                      ))}
                    </div>
                    <form className="chat-input" onSubmit={sendChat}>
                      <input
                        type="text"
                        placeholder="Ask a question..."
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                      />
                      <button className="btn" type="submit">Send</button>
                    </form>
                  </>
                )}
              </div>
            </div>
          </div>
        </section>
      )}

      <div className="slide-nav">
        <button className="ghost" onClick={() => setSlide((prev) => Math.max(1, prev - 1))} disabled={!canPrev}>
          ← Previous
        </button>
        <button className="ghost" onClick={() => setSlide((prev) => Math.min(4, prev + 1))} disabled={!canNext}>
          Next →
        </button>
      </div>
    </div>
  );
}

