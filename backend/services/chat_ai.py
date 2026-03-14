# pyright: ignore
import os
from typing import List, Dict, Optional


SYSTEM_INSTRUCTION = (
    "You are StudentAI, a helpful assistant for a student retention dashboard. "
    "Answer concisely. When asked about dropout risk, explain what factors matter and what actions can help. "
    "When asked about scholarships, suggest practical eligibility checks and next steps. "
    "Do not invent student-specific facts."
)


def _get_api_key() -> Optional[str]:
    # Support a couple of common env var names.
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def _pick_model(genai) -> tuple[str, str]:
    """Pick a model + method supported by the current API key.

    Returns: (model_name, method) where method is 'generateContent' or 'generateMessage'.
    """

    preferred: list[str] = []
    env_model = (os.getenv("GEMINI_MODEL") or "").strip()
    if env_model:
        preferred.append(env_model)

    # Common model ids across Gemini API versions.
    preferred.extend(
        [
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
            "gemini-1.0-pro",
            "gemini-pro",
        ]
    )

    try:
        by_name: dict[str, list[str]] = {}
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", []) or []
            name = (getattr(m, "name", "") or "").replace("models/", "")
            if name:
                by_name[name] = [str(x) for x in methods]

        # Prefer generateContent, then generateMessage.
        for desired_method in ("generateContent", "generateMessage"):
            for name in preferred:
                n = name.replace("models/", "")
                if n in by_name and desired_method in by_name[n]:
                    return n, desired_method

            # Any model supporting desired_method.
            for n, methods in by_name.items():
                if desired_method in methods:
                    return n, desired_method

    except Exception:
        pass

    # Safe fallback.
    return env_model or "gemini-pro", "generateMessage"


def generate_chat_reply(messages: List[Dict[str, str]]) -> str:
    """Generate a chat reply using Gemini.

    Expects messages like: [{role: 'user'|'ai', text: '...'}]
    """

    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY (or GOOGLE_API_KEY) in environment")

    try:
        import google.generativeai as genai
    except Exception as e:
        raise RuntimeError(f"Gemini SDK not installed: {e}")

    genai.configure(api_key=api_key)

    # Keep the prompt compact and deterministic.
    trimmed = (messages or [])[-12:]
    transcript_lines = []
    for m in trimmed:
        role = (m.get("role") or "").strip().lower()
        text = (m.get("text") or "").strip()
        if not text:
            continue
        if role == "ai" or role == "assistant" or role == "model":
            transcript_lines.append(f"Assistant: {text}")
        else:
            transcript_lines.append(f"User: {text}")

    prompt = SYSTEM_INSTRUCTION + "\n\nConversation so far:\n" + "\n".join(transcript_lines) + "\n\nAssistant:"

    model_name, method = _pick_model(genai)
    model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_INSTRUCTION)

    if method == "generateContent":
        response = model.generate_content(prompt)
        text = getattr(response, "text", None) or ""
        return text.strip() or "I can help—what would you like to know about risk, interventions, or scholarships?"

    # Interactions API path (generateMessage): use chat history + last user message.
    history = []
    last_user_text = ""
    for m in trimmed:
        role = (m.get("role") or "").strip().lower()
        text = (m.get("text") or "").strip()
        if not text:
            continue
        if role in {"user", "human"}:
            last_user_text = text
            history.append({"role": "user", "parts": [text]})
        else:
            history.append({"role": "model", "parts": [text]})

    if not last_user_text:
        last_user_text = transcript_lines[-1].replace("User:", "").strip() if transcript_lines else "Hello"

    chat = model.start_chat(history=history[:-1] if history else [])
    response = chat.send_message(last_user_text)
    text = getattr(response, "text", None) or ""
    return text.strip() or "I can help—what would you like to know about risk, interventions, or scholarships?"
