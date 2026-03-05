export async function predictStudent(payload) {
  const res = await fetch("http://127.0.0.1:5000/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function fetchHighRisk() {
  const res = await fetch("http://127.0.0.1:5000/students/high-risk");
  return res.json();
}

export async function fetchMonitoring() {
  const res = await fetch("http://127.0.0.1:5000/monitoring");
  return res.json();
}

export async function createAction(payload) {
  const res = await fetch("http://127.0.0.1:5000/actions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function signup(payload) {
  const res = await fetch("http://127.0.0.1:5000/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function login(payload) {
  const res = await fetch("http://127.0.0.1:5000/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}
