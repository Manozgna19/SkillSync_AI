"""
Turns the recommendation engine's structured reasons into a human-readable
explanation. Gemini is only allowed to *rephrase* the reasons we give it -
it must not invent new ones. If Gemini is unavailable, we fall back to a
deterministic template.
"""
from typing import List

from app.ai import gemini_client

SYSTEM_INSTRUCTION = """You are writing a short, friendly explanation for why a
learning resource was recommended to a learner. You will be given a list of
factual reasons (already computed by a recommendation engine). Rephrase them
into 2-3 natural, encouraging sentences. Do NOT invent any reason that is not
in the provided list. Do NOT mention scores or percentages verbatim unless
given. Keep it concise."""


def _fallback_explanation(reasons: List[str]) -> str:
    if not reasons:
        return "This resource matches your current learning path."
    return "This was recommended because: " + "; ".join(reasons) + "."


def explain_recommendation(
    goal: str,
    resource_title: str,
    reasons: List[str],
) -> str:
    if not reasons:
        return _fallback_explanation(reasons)

    prompt = (
        f"Learner's goal: {goal}\n"
        f"Recommended resource: {resource_title}\n"
        f"Reasons (facts, do not add to this list): {reasons}\n\n"
        "Write the explanation now."
    )
    text = gemini_client.generate(prompt, system_instruction=SYSTEM_INSTRUCTION)
    if text:
        return text.strip()
    return _fallback_explanation(reasons)
