import { useEffect, useState } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext";

const ROLES = ["student"];

export default function LoginPage() {
  const { isAuthenticated, login, signup, loginWithGoogle, loading } = useAuth();
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "student" });
  const isGoogleEnabled = typeof window !== "undefined" && Boolean(window.__SR_GOOGLE_ENABLED__);
  const isBackendUp = typeof window === "undefined" ? true : window.__SR_BACKEND_UP__ !== false;

  useEffect(() => {
    const requestedMode = searchParams.get("mode");
    if (requestedMode === "login" || requestedMode === "signup") {
      setMode(requestedMode);
    }
  }, [searchParams]);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const submit = async (e) => {
    e.preventDefault();
    // Login and signup share the same form; behavior switches by mode.
    if (mode === "login") {
      await login({ email: form.email, password: form.password, role: form.role });
      return;
    }
    await signup(form);
  };

  const handleGoogle = async (credentialResponse) => {
    const token = credentialResponse?.credential;
    if (!token) return;
    await loginWithGoogle({ token, role: form.role });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-200 p-4 text-slate-900 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 dark:text-slate-100 md:p-8">
      <div className="mx-auto flex min-h-[calc(100vh-2rem)] max-w-6xl items-center md:min-h-[calc(100vh-4rem)]">
        <section className="glass w-full p-6 md:p-10">
          <h1 className="text-center text-3xl font-bold md:text-4xl">Student Retento</h1>
          <p className="mt-2 text-center text-slate-600 dark:text-slate-300">Student login only. Teacher login is disabled.</p>

          <div className="mt-8 grid gap-8 lg:grid-cols-2">
            <div>
              <div className="flex gap-2">
                <button className={`ghost-btn ${mode === "login" ? "ring-2 ring-blue-400" : ""}`} onClick={() => setMode("login")}>Login</button>
                <button className={`ghost-btn ${mode === "signup" ? "ring-2 ring-blue-400" : ""}`} onClick={() => setMode("signup")}>Signup</button>
              </div>

              <form className="mt-4 space-y-3" onSubmit={submit}>
                {!isBackendUp && (
                  <p className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                    Backend is not running. Start it with <span className="font-semibold">npm run backend</span>, then refresh this page.
                  </p>
                )}

                {mode === "signup" && (
                  <input
                    className="input"
                    placeholder="Full name"
                    value={form.name}
                    onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                    required
                  />
                )}
                <input
                  className="input"
                  type="email"
                  placeholder="Email"
                  value={form.email}
                  onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
                  required
                />
                <input
                  className="input"
                  type="password"
                  placeholder="Password"
                  value={form.password}
                  onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
                  required
                />
                {/* Role selection removed: only student login allowed */}
                <button className="primary-btn w-full" disabled={loading} type="submit">
                  {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
                </button>

                <div className="pt-2">
                  {/* Google button appears only when backend exposes a client id. */}
                  {isGoogleEnabled ? (
                    <GoogleLogin onSuccess={handleGoogle} onError={() => toast.error("Google sign-in failed. Please try again.")} />
                  ) : (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {isBackendUp
                        ? "Set GOOGLE_CLIENT_ID in backend/.env to enable Google sign-in."
                        : "Google sign-in is unavailable while backend is offline."}
                    </p>
                  )}
                </div>
              </form>
            </div>

            <div className="rounded-2xl border border-slate-200/80 bg-white/70 p-6 dark:border-slate-700/70 dark:bg-slate-900/50">
              <h2 className="text-xl font-semibold">Why this platform</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                <li>• Predicts dropout risk using ML probability scores.</li>
                <li>• Tracks attendance, behavior, and academic patterns.</li>
                <li>• Recommends interventions in real time.</li>
                <li>• Empowers students to take charge of their progress.</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
