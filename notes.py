"""
notes.py

Hierarchical RAG Notes Generation

Flow:
1. Load transcript chunks from ChromaDB.
2. Generate notes for each chunk.
3. Merge all notes.
4. Remove duplicates.
5. Return final key notes.
"""

from typing import List

from groq import Groq

import config
from embeddings import get_all_video_chunks
from utils.exceptions import LLMGenerationError


# ==================================================
# Prompts
# ==================================================

CHUNK_NOTES_PROMPT = """
You are an expert educational note-taker.

Extract important concepts, definitions, formulas,
keywords, and learning takeaways from this transcript section.

Requirements:

1. Keep notes concise.
2. One concept per line.
3. Do not explain extensively.
4. Remove filler content.
5. Focus only on educational content.
6. Use simple language.
7. Return ONLY bullet points.
8. Start every line with "• ".

Transcript Section:

{chunk}

Notes:
"""


FINAL_NOTES_PROMPT = """
You are an expert educational note organizer.

You are given notes extracted from different sections
of the same lecture.

Tasks:

1. Remove duplicates.
2. Merge similar concepts.
3. Keep the most important educational concepts.
4. Keep definitions if available.
5. Keep formulas if available.
6. Keep important terminology.
7. Produce exam-ready revision notes.
8. Return approximately {note_limit} notes.
9. Return ONLY bullet points.
10. Start every line with "• ".

Collected Notes:

{notes}

Final Notes:
"""


# ==================================================
# Utilities
# ==================================================

def parse_notes_response(raw_response: str) -> List[str]:
    """
    Convert LLM response into clean notes.
    """

    if not raw_response:
        return []

    notes = []
    seen = set()

    for line in raw_response.splitlines():

        line = line.strip()

        if not line:
            continue

        line = (
            line.lstrip("•-*")
            .lstrip("0123456789")
            .lstrip(".)")
            .strip()
        )

        if not line:
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)
        notes.append(line)

    return notes


# ==================================================
# Groq Generation
# ==================================================

def generate_text(
    client: Groq,
    prompt: str,
    max_tokens: int = 1000
) -> str:
    """
    Generate text using Groq.
    """

    response = client.chat.completions.create(
        model=config.GROQ_MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_completion_tokens=max_tokens,
    )

    return response.choices[0].message.content.strip()


# ==================================================
# Chunk Notes
# ==================================================

def generate_chunk_notes(
    client: Groq,
    chunk: str
) -> List[str]:
    """
    Generate notes for one transcript chunk.
    """

    prompt = CHUNK_NOTES_PROMPT.format(
        chunk=chunk
    )

    response_text = generate_text(
        client=client,
        prompt=prompt,
        max_tokens=800
    )

    return parse_notes_response(
        response_text
    )

def calculate_note_limit(
    total_chunks: int
) -> int:

    if total_chunks <= 5:
        return 6

    elif total_chunks <= 10:
        return 12

    elif total_chunks <= 20:
        return 20

    elif total_chunks <= 40:
        return 40

    else:
        return 60
    
# ==================================================
# Final Notes Merge
# ==================================================

def combine_notes(
    client: Groq,
    all_notes: List[str],
    note_limit: int
) -> List[str]:
    """
    Merge and deduplicate notes.
    """

    notes_text = "\n".join(
        f"• {note}"
        for note in all_notes
    )

    prompt = FINAL_NOTES_PROMPT.format(
        notes=notes_text,
        note_limit=note_limit
    )

    response_text = generate_text(
        client=client,
        prompt=prompt,
        max_tokens=1500
    )

    return parse_notes_response(
        response_text
    )


# ==================================================
# Main Notes Pipeline
# ==================================================

def generate_key_notes(
    video_id: str
) -> List[str]:
    """
    Hierarchical RAG Notes Generation
    """

    if not config.GROQ_API_KEY:
        raise LLMGenerationError(
            "GROQ_API_KEY is not set."
        )

    chunks = get_all_video_chunks(
        video_id
    )

    if not chunks:
        return []
    note_limit = calculate_note_limit(
        len(chunks)
    )

    try:

        client = Groq(
            api_key=config.GROQ_API_KEY
        )

        all_notes = []

        BATCH_SIZE = 5

        for i in range(
            0,
            len(chunks),
            BATCH_SIZE
        ):

            batch = chunks[
                i:i + BATCH_SIZE
            ]

            print(
                f"Generating notes batch "
                f"{i // BATCH_SIZE + 1}"
            )

            combined_chunk = "\n\n".join(
                batch
            )

            chunk_notes = generate_chunk_notes(
                client,
                combined_chunk
            )

            all_notes.extend(
                chunk_notes
            )

        print(
            "Generating final notes..."
        )

        final_notes = combine_notes(
            client,
            all_notes,
            note_limit
        )

        return final_notes

    except Exception as exc:

        raise LLMGenerationError(
            f"Groq API Error while generating notes: {str(exc)}"
        )