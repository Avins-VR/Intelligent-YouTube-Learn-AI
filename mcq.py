"""
mcq.py

RAG-Based MCQ Assessment Generation

Flow:
1. Retrieve educationally important chunks from ChromaDB.
2. Use semantic search with multiple assessment-focused queries.
3. Merge and deduplicate retrieved chunks.
4. Send retrieved context to Groq.
5. Generate dynamic MCQs based on video duration.
6. Parse and validate JSON response.
"""

import json
import re
from typing import List, Dict

from groq import Groq

import config
from embeddings import query_video_chunks
from utils.exceptions import LLMGenerationError


# --------------------------------------------------
# Configure Groq
# --------------------------------------------------

client = Groq(
    api_key=config.GROQ_API_KEY
)


# --------------------------------------------------
# Retrieval Queries
# --------------------------------------------------

ASSESSMENT_QUERIES = [
    "important concepts",
    "key definitions",
    "important formulas",
    "examples explained",
    "major topics discussed",
    "exam questions",
    "learning objectives",
    "important takeaways",
]


# --------------------------------------------------
# Prompt
# --------------------------------------------------

MCQ_PROMPT = """
You are an expert educational assessment designer.

Generate exactly {mcq_count} high-quality multiple-choice questions (MCQs)
using ONLY the retrieved transcript context below.

Difficulty Distribution:

- Easy Questions: {easy_count}
- Medium Questions: {medium_count}
- Hard Questions: {hard_count}

Rules:

1. Generate exactly {mcq_count} questions.
2. Easy questions should test basic understanding.
3. Medium questions should test conceptual understanding.
4. Hard questions should test deeper reasoning and application.
5. Use only information found in the context.
6. Do not invent information.
7. Each question must have exactly 4 options:
   A, B, C, D.
8. Exactly one option must be correct.
9. Avoid duplicate questions.
10. Include a short explanation.
11. Add a difficulty field.
12. Return ONLY valid JSON.

Output Format:

[
  {{
    "difficulty": "Easy",
    "question": "string",
    "options": {{
      "A": "string",
      "B": "string",
      "C": "string",
      "D": "string"
    }},
    "correct_answer": "A",
    "explanation": "string"
  }}
]

Retrieved Context:

{context}
"""


# --------------------------------------------------
# Retrieval Layer (RAG)
# --------------------------------------------------

def retrieve_mcq_context(video_id: str) -> str:
    """
    Retrieve educationally important chunks using
    multiple semantic search queries.
    """

    unique_chunks = []
    seen = set()

    for query in ASSESSMENT_QUERIES:

        try:

            chunks = query_video_chunks(
                video_id=video_id,
                question=query,
                top_k=2
            )

            for chunk in chunks:

                normalized = chunk.strip().lower()

                if normalized not in seen:

                    seen.add(normalized)
                    unique_chunks.append(chunk)

        except Exception:
            continue

    return "\n\n".join(unique_chunks)


# --------------------------------------------------
# JSON Utilities
# --------------------------------------------------

def extract_json_array(raw_text: str) -> str:

    cleaned = raw_text.strip()

    cleaned = re.sub(
        r"^```(?:json)?",
        "",
        cleaned,
        flags=re.IGNORECASE
    ).strip()

    cleaned = re.sub(
        r"```$",
        "",
        cleaned
    ).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1:

        return cleaned

    return cleaned[start:end + 1]


def validate_mcq(item: Dict) -> bool:

    if not isinstance(item, dict):
        return False

    required = {
        "difficulty",
        "question",
        "options",
        "correct_answer",
        "explanation"
    }

    if not required.issubset(item.keys()):
        return False

    options = item.get("options")

    if not isinstance(options, dict):
        return False

    if set(options.keys()) != {"A", "B", "C", "D"}:
        return False

    if item.get("correct_answer") not in {
        "A",
        "B",
        "C",
        "D"
    }:
        return False
    
    if item.get("difficulty") not in {
        "Easy",
        "Medium",
        "Hard"
    }:
        return False
    
    return True


def parse_mcq_response(raw_text: str) -> List[Dict]:

    json_text = extract_json_array(raw_text)

    try:

        parsed = json.loads(json_text)

    except Exception:

        return []

    if not isinstance(parsed, list):
        return []

    valid_mcqs = []

    for item in parsed:

        if validate_mcq(item):

            valid_mcqs.append(item)

    return valid_mcqs

def get_mcq_count(duration_seconds: int):

    minutes = duration_seconds // 60

    if minutes <= 5:
        return 8

    elif minutes <= 15:
        return 12

    elif minutes <= 30:
        return 15

    elif minutes <= 60:
        return 20

    elif minutes <= 120:
        return 30

    else:
        return 40
    
def get_difficulty_distribution(mcq_count):

    easy = int(mcq_count * 0.4)
    medium = int(mcq_count * 0.4)

    hard = mcq_count - easy - medium

    return easy, medium, hard

# --------------------------------------------------
# LLM Generation
# --------------------------------------------------

def generate_mcqs(video_id: str,duration: int) -> List[Dict]:
    """
    Main RAG-based MCQ generation pipeline.
    """

    mcq_count = get_mcq_count(
        duration
    )

    easy_count, medium_count, hard_count = (
        get_difficulty_distribution(mcq_count)
    )
    
    if not config.GROQ_API_KEY:

        raise LLMGenerationError(
            "GROQ_API_KEY is not set."
        )
    
    context = retrieve_mcq_context(
        video_id
    )

    if not context:

        return []

    prompt = MCQ_PROMPT.format(
        context=context,
        mcq_count=mcq_count,
        easy_count=easy_count,
        medium_count=medium_count,
        hard_count=hard_count
    )

    try:

        response = client.chat.completions.create(
            model=config.GROQ_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_completion_tokens=3000,
        )

        raw_text = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )
    except Exception as exc:

        raise LLMGenerationError(
            f"Groq API Error while generating MCQs: {str(exc)}"
        )

    mcqs = parse_mcq_response(
        raw_text
    )

    print(
        f"Generated {len(mcqs)} MCQs"
    )

    if not mcqs:

        raise LLMGenerationError(
            "Failed to generate valid MCQs."
        )

    return mcqs