import React from "react";
import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import App from "./App.jsx";

<<<<<<< HEAD
const GOOGLE_CLIENT_ID =
  import.meta.env.VITE_GOOGLE_CLIENT_ID ||
  "886376637376-0v87tkcqkukg983r5kokqfcf2rit7e81.apps.googleusercontent.com";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>
);
=======
const rawGoogleClientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID || "").trim();
const googleClientIdPattern = /^\d{12}-[a-z0-9-]+\.apps\.googleusercontent\.com$/i;
const GOOGLE_CLIENT_ID = googleClientIdPattern.test(rawGoogleClientId) ? rawGoogleClientId : "";

if (rawGoogleClientId && !GOOGLE_CLIENT_ID) {
  console.error("Invalid VITE_GOOGLE_CLIENT_ID format in frontend/.env.local");
}

const app = (
  <React.StrictMode>
    <App googleOauthEnabled={Boolean(GOOGLE_CLIENT_ID)} />
  </React.StrictMode>
);

createRoot(document.getElementById("root")).render(
  GOOGLE_CLIENT_ID ? <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>{app}</GoogleOAuthProvider> : app
);

>>>>>>> upstream/main
