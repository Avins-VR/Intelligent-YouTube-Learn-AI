# summary.py

"""
Generates a complete timeline-based summary for the entire lecture.

Flow:
1. Load all transcript chunks from ChromaDB.
2. Merge chunks into one transcript.
3. Send transcript to Groq.
4. Generate a structured timeline summary.
"""

import requests

import config
from embeddings import get_all_video_chunks


def generate_summary(video_id, duration):
    """
    Generate lecture summary.

    Args:
        video_id (str): YouTube video ID
        duration (int): Video duration in seconds

    Returns:
        str: Generated summary
    """

    # --------------------------------------------
    # Load transcript chunks from ChromaDB
    # --------------------------------------------
    chunks = get_all_video_chunks(video_id)

    if not chunks:
        return "No transcript data available."

    # --------------------------------------------
    # Combine all chunks
    # --------------------------------------------
    full_transcript = "\n\n".join(chunks)

    # --------------------------------------------
    # Convert duration
    # --------------------------------------------
    total_minutes = duration // 60
    total_seconds = duration % 60

    video_duration = (
        f"{total_minutes:02d}:{total_seconds:02d}"
    )

    # --------------------------------------------
    # Prompt
    # --------------------------------------------
    prompt = f"""
You are an expert educational lecture analyst.

Analyze the lecture transcript and create comprehensive study notes.

Requirements:

1. Divide the lecture into major topics.
2. Give a clear title for each topic.
3. For each topic write a detailed explanation of 15-25 sentences.
4. Explain concepts in simple student-friendly language.
5. Include examples mentioned in the lecture.
6. Explain why the concept is important.
7. Explain relationships between concepts.
8. Cover all important information from the transcript.
9. Use only transcript content.
10. Do not invent information.
11. Do not generate timestamps.
12. Do not generate bullet points.
13. Do not generate Key Ideas sections.
14. Make the summary detailed enough that a student can study from it without watching the video.

Output Format:

Topic Title

Detailed Explanation

Topic Title

Detailed Explanation

Topic Title

Detailed Explanation

Transcript:

{full_transcript[:20000]}
"""
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": config.GROQ_MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.1,
        "max_tokens": 3500,
    }

    # --------------------------------------------
    # Call Groq
    # --------------------------------------------
    response = requests.post(
        config.GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )

    data = response.json()

    # --------------------------------------------
    # Debugging
    # --------------------------------------------
    print(data)

    if "choices" not in data:
        raise Exception(
            f"Groq Error: {data}"
        )

    summary = data["choices"][0]["message"]["content"]

    return summary