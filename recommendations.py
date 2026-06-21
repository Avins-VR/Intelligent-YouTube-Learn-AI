"""
recommendations.py

Learning Path Recommendations

Recommends 5-10 next topics for a student to learn after finishing the
current video, based on the generated summary and key notes (key
concepts). Mirrors the existing Groq-based pattern used elsewhere in
the app — does not touch any existing backend module.
"""

import json
import re
from typing import List, Dict

from groq import Groq

import config
from utils.exceptions import LLMGenerationError


client = Groq(api_key=config.GROQ_API_KEY)


RECOMMENDATIONS_PROMPT = """
You are an expert curriculum advisor for an educational platform.

Based on the video content below (its summary and key concepts),
recommend the next topics a student should learn.

Requirements:

1. Recommend exactly {recommendation_count} topics.
2. Order topics to follow a logical learning path (foundational topics
   first, more advanced topics later).
3. Each recommendation must be clearly related to the current video's
   content — do not recommend unrelated subjects.
4. For each topic, briefly explain WHY it is recommended (1-2 sentences),
   referencing how it builds on or extends the current video's content.

Respond with ONLY valid JSON — no preamble, no markdown code fences,
no commentary. The JSON must contain exactly {recommendation_count} objects in this exact
shape:

[
  {{
    "topic": "string",
    "reason": "string"
  }}
]

Video Summary:

{summary}

Key Concepts:

{key_concepts}
"""


def _extract_json_array(raw_text: str) -> str:
    """Best-effort extraction of a JSON array from a model response."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end < start:
        return cleaned

    return cleaned[start:end + 1]


def _validate_recommendation(item: Dict) -> bool:
    if not isinstance(item, dict):
        return False
    return {"topic", "reason"}.issubset(item.keys())


def parse_recommendations_response(raw_text: str,recommendation_count: int) -> List[Dict]:
    """Parse the model's JSON response into a list of validated recommendation dicts."""
    json_str = _extract_json_array(raw_text)

    try:
        parsed = json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(parsed, list):
        return []

    valid_items = [item for item in parsed if _validate_recommendation(item)]

    return valid_items[:recommendation_count]

def get_recommendation_count(duration_seconds: int):

    minutes = duration_seconds // 60

    if minutes <= 5:
        return 3

    elif minutes <= 15:
        return 6

    elif minutes <= 30:
        return 10

    elif minutes <= 60:
        return 15

    elif minutes <= 120:
        return 25

    else:
        return 40

def generate_recommendations(summary: str, notes: List[str],duration: int) -> List[Dict]:
    """
    Generate dynamic learning path recommendations based on video duration from the video's summary and
    key notes (used as a stand-in for "key concepts"). Returns a list of
    dicts: {"topic", "reason"}.
    """
    if not config.GROQ_API_KEY:
        raise LLMGenerationError("GROQ_API_KEY is not set.")

    if not summary:
        return []

    key_concepts = "\n".join(f"- {note}" for note in notes) if notes else "Not available."

    recommendation_count = get_recommendation_count(
        duration
    )

    prompt = RECOMMENDATIONS_PROMPT.format(summary=summary, key_concepts=key_concepts, recommendation_count=recommendation_count)

    try:
        response = client.chat.completions.create(
            model=config.GROQ_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_completion_tokens=1500,
        )

        raw_text = response.choices[0].message.content.strip()

    except Exception as exc:
        raise LLMGenerationError(f"Groq API Error while generating recommendations: {str(exc)}")

    recommendations = parse_recommendations_response(raw_text,recommendation_count)

    if not recommendations:
        raise LLMGenerationError(
            "The AI response could not be parsed into valid recommendations. Please try again."
        )

    return recommendations