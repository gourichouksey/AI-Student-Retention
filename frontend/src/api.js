function getDefaultApiBaseUrl() {
  // If you open the frontend from another device on LAN (e.g. http://192.168.1.20:5173),
  // the backend is typically on the same host at port 5000.
  if (typeof window !== "undefined" && window?.location?.hostname) {
    const protocol = window.location.protocol || "http:";
    return `${protocol}//${window.location.hostname}:5000`;
  }
  return "http://127.0.0.1:5000";
}

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || getDefaultApiBaseUrl()).replace(/\/$/, "");

export async function predictStudent(payload) {
  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function fetchHighRisk() {
  const res = await fetch(`${API_BASE_URL}/students/high-risk`);
  return res.json();
}

export async function fetchMonitoring() {
  const res = await fetch(`${API_BASE_URL}/monitoring`);
  return res.json();
}

export async function createAction(payload) {
  const res = await fetch(`${API_BASE_URL}/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function signup(payload) {
  const res = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function login(payload) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function googleLogin(token) {
  const res = await fetch(`${API_BASE_URL}/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  return res.json();
}

export async function chatWithAi(messages) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  return res.json();
}

