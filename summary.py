"""
summary.py

Generates a complete lecture summary using Gemini 2.5 Flash.

Flow:
1. Load all transcript chunks from ChromaDB.
2. Merge chunks into one transcript.
3. Send transcript to Gemini.
4. Generate a structured study summary.
"""

import google.generativeai as genai

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

    # --------------------------------------------------
    # Configure Gemini
    # --------------------------------------------------
    genai.configure(api_key=config.GEMINI_API_KEY)

    # --------------------------------------------------
    # Load transcript chunks
    # --------------------------------------------------
    chunks = get_all_video_chunks(video_id)

    if not chunks:
        return "No transcript data available."

    # --------------------------------------------------
    # Merge transcript
    # --------------------------------------------------
    full_transcript = "\n\n".join(chunks)

    # --------------------------------------------------
    # Convert duration
    # --------------------------------------------------
    total_minutes = duration // 60
    total_seconds = duration % 60

    video_duration = f"{total_minutes:02d}:{total_seconds:02d}"

    # --------------------------------------------------
    # Build Prompt
    # --------------------------------------------------
    prompt = f"""
You are an expert educational lecture analyst.

Analyze the lecture transcript and create comprehensive study notes.

Requirements:

1. Divide the lecture into major topics.
2. Give a clear title for each topic.
3. For each topic write a detailed explanation of 25-35 sentences.
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

    # --------------------------------------------------
    # Load Gemini Model
    # --------------------------------------------------
    model = genai.GenerativeModel(
        model_name=config.GEMINI_MODEL_NAME
    )

    # --------------------------------------------------
    # Generate Summary
    # --------------------------------------------------
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1,
            "max_output_tokens": 3500,
        }
    )

    # --------------------------------------------------
    # Return Summary
    # --------------------------------------------------
    return response.text