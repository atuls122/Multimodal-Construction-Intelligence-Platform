"""Thin wrapper around the Google Gemini API (google-genai SDK)."""
import json
import os

DEFAULT_MODEL = "gemini-2.5-flash"


def get_client(api_key: str | None = None):
    """Create a Gemini client. Falls back to the GEMINI_API_KEY environment variable."""
    from google import genai  # imported here so the rest of the app/tests work without the package

    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("No Gemini API key found. Paste it in the sidebar or set GEMINI_API_KEY in .env")
    return genai.Client(api_key=key)


def ask_text(client, prompt: str, image=None, model: str = DEFAULT_MODEL) -> str:
    """Send a prompt (optionally with a PIL image) and return plain text."""
    contents = [image, prompt] if image is not None else [prompt]
    response = client.models.generate_content(model=model, contents=contents)
    return response.text or ""


def ask_json(client, prompt: str, image=None, model: str = DEFAULT_MODEL) -> dict:
    """Send a prompt and parse the reply as JSON. Returns {"_raw": text} if parsing fails."""
    from google.genai import types

    contents = [image, prompt] if image is not None else [prompt]
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    text = (response.text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text}
