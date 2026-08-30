"""
Thin wrapper around the Gemini API.

Design goals:
- Never crash the application if Gemini is unavailable.
- Never expose the Gemini API key to the frontend.
- Support normal text generation.
- Support structured JSON generation.
- Return None when Gemini cannot be reached or returns invalid data.
"""

import json
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    """Return True when a Gemini API key is configured."""

    key = getattr(
        settings,
        "GEMINI_API_KEY",
        "",
    )

    return bool(
        key and key.strip()
    )


def _get_model():
    """
    Create and return the configured Gemini model.

    The model is created on demand so configuration changes
    are picked up after restarting the backend.
    """

    import google.generativeai as genai

    api_key = settings.GEMINI_API_KEY.strip()

    genai.configure(
        api_key=api_key
    )

    return genai.GenerativeModel(
        settings.GEMINI_MODEL
    )


def generate(
    prompt: str,
    system_instruction: Optional[str] = None,
    json_mode: bool = False,
) -> Optional[str]:
    """
    Generate a response using Gemini.

    Returns:
        str: Gemini response
        None: Gemini unavailable or request failed
    """

    if not is_configured():
        logger.warning(
            "Gemini API key is not configured."
        )
        return None

    try:

        import google.generativeai as genai

        genai.configure(
            api_key=settings.GEMINI_API_KEY.strip()
        )

        generation_config = {}

        if json_mode:

            generation_config[
                "response_mime_type"
            ] = "application/json"

        model = genai.GenerativeModel(
            settings.GEMINI_MODEL,
            system_instruction=system_instruction,
            generation_config=(
                generation_config
                if generation_config
                else None
            ),
        )

        response = model.generate_content(
            prompt
        )

        if response is None:
            logger.warning(
                "Gemini returned an empty response."
            )
            return None

        text = getattr(
            response,
            "text",
            None,
        )

        if not text:
            logger.warning(
                "Gemini response contained no text."
            )
            return None

        return text.strip()

    except Exception as exc:
        logger.warning(
            "Gemini API call failed: %s",
            exc,
        )
        return None


def generate_json(
    prompt: str,
    system_instruction: Optional[str] = None,
) -> Optional[dict]:
    """
    Generate a JSON object using Gemini.

    Returns:
        dict: Parsed JSON object
        None: Gemini unavailable or invalid JSON
    """

    raw = generate(
        prompt=prompt,
        system_instruction=system_instruction,
        json_mode=True,
    )

    if raw is None:
        return None

    try:

        cleaned = raw.strip()

        # ----------------------------------------------------
        # Remove markdown code fences if Gemini returns them.
        # ----------------------------------------------------

        if cleaned.startswith("```"):

            lines = cleaned.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(
                lines
            ).strip()

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        parsed = json.loads(
            cleaned
        )

        if not isinstance(
            parsed,
            dict,
        ):
            logger.warning(
                "Gemini JSON response was not an object."
            )
            return None

        return parsed

    except (
        json.JSONDecodeError,
        ValueError,
        TypeError,
    ) as exc:

        logger.warning(
            "Failed to parse Gemini JSON response: %s",
            exc,
        )

        return None