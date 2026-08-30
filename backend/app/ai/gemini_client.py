"""
Thin wrapper around the Gemini API.

Design goals:
- Never crash the app if Gemini is unavailable (no key, network error,
  quota exceeded, malformed response). Callers get `None` back and are
  expected to fall back to deterministic behavior.
- The API key is only ever read from the environment/settings and is
  never returned to the frontend.
"""
import json
import logging
from functools import lru_cache
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(settings.GEMINI_API_KEY.strip())


@lru_cache(maxsize=1)
def _get_client():
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel(settings.GEMINI_MODEL)


def generate(prompt: str, system_instruction: Optional[str] = None, json_mode: bool = False) -> Optional[str]:
    """
    Call Gemini with a prompt. Returns the raw text response, or None if
    Gemini is not configured or the call fails for any reason.
    """
    if not is_configured():
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        generation_config = {}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            system_instruction=system_instruction,
            generation_config=generation_config or None,
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:  # noqa: BLE001 - we want to swallow all errors here
        logger.warning("Gemini call failed, falling back to deterministic logic: %s", exc)
        return None


def generate_json(prompt: str, system_instruction: Optional[str] = None) -> Optional[dict]:
    """Call Gemini expecting a JSON object back; returns a parsed dict or None."""
    raw = generate(prompt, system_instruction=system_instruction, json_mode=True)
    if raw is None:
        return None
    try:
        # Strip markdown fences defensively, in case the model adds them.
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.split("\n", 1)[-1] if "\n" in cleaned else cleaned
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Failed to parse Gemini JSON response: %s", exc)
        return None
