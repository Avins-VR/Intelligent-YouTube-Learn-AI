"""
summary.py

Hierarchical RAG Summary Generation

Flow:
1. Load transcript chunks from ChromaDB.
2. Generate a summary for each chunk.
3. Combine all chunk summaries.
4. Generate one final comprehensive summary.
"""

from groq import Groq

import config
from embeddings import get_all_video_chunks


# --------------------------------------------------
# Configure Groq
# --------------------------------------------------

client = Groq(
    api_key=config.GROQ_API_KEY
)


def summarize_chunk(chunk: str) -> str:
    """
    Generate summary for a single chunk.
    """
    prompt = f"""
You are an expert educational content analyst.

Summarize the following transcript section.

Instructions:

1. Preserve ALL important concepts.
2. Preserve ALL definitions.
3. Preserve ALL examples.
4. Preserve ALL explanations.
5. Preserve important discussions and arguments.
6. Do not skip details.
7. Expand concepts in simple student-friendly language.
8. Keep educational depth.
9. Use multiple paragraphs.
10. Generate between 150 and 700 words depending on the amount of content available.
11. Do not invent information.
12. Use paragraph format only.

Transcript Section:

{chunk}
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
        max_completion_tokens=1500,
    )

    return (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

def get_summary_size(duration_seconds: int):

    minutes = duration_seconds // 60

    if minutes <= 5:
        return {
            "paragraphs": "3-4",
            "words": "300-600"
        }

    elif minutes <= 15:
        return {
            "paragraphs": "5-8",
            "words": "800-1200"
        }

    elif minutes <= 30:
        return {
            "paragraphs": "8-12",
            "words": "1200-2000"
        }

    elif minutes <= 60:
        return {
            "paragraphs": "12-20",
            "words": "2000-3500"
        }

    elif minutes <= 120:
        return {
            "paragraphs": "20-35",
            "words": "3500-6000"
        }

    else:
        return {
            "paragraphs": "35-50",
            "words": "6000-10000"
        }
    
def combine_chunk_summaries(
    summaries: list[str],
    video_duration: str,
    summary_size: dict
) -> str:
    """
    Merge all chunk summaries into one final summary.
    """

    combined_text = "\n\n".join(
        summaries
    )

    prompt = f"""
You are an expert educational lecture analyst.

Video Duration:
{video_duration}

You are given summaries generated from different sections of a lecture.

Create a final comprehensive study summary.

Instructions:

1. Cover the entire lecture.
2. Divide the summary into major topics.
3. Create clear topic headings.
4. Explain concepts thoroughly.
5. Explain relationships between concepts.
6. Include examples whenever available.
7. Use student-friendly language.
8. Do not invent information.
9. Do not generate timestamps.
10. Do not generate bullet points.
11. Write in paragraph format.
12. Make the summary suitable for exam preparation.
13. Ensure all important topics are included.
14. Generate an extremely detailed study summary.
15. Expand every topic thoroughly.
16. Explain concepts as if teaching a student.
17. Include all major points from the lecture.
18. Include supporting explanations.
19. Include examples whenever mentioned.
20. Preserve important insights from the speaker.
21. Do not compress information.
22. Generate approximately {summary_size["paragraphs"]} detailed paragraphs.
23. Target approximately {summary_size["words"]} words.
24. Longer videos should have more detail.
25. Short videos should have concise summaries.
26. Every paragraph should contain 6-8 meaningful lines.
27. Do not add unnecessary content just to increase length.
28. Generate summary proportionally to the lecture length.
29. The summary should feel like detailed lecture notes.
30. Make the output suitable for exam preparation and revision.

Output Format:

# Topic Title

Detailed Explanation

# Topic Title

Detailed Explanation

IMPORTANT FORMATTING RULES:

1. Every topic title must be on its own line.
2. Add ONE empty line after every heading.
3. Start the explanation on the next line.
4. Never put explanation text on the same line as the heading.
5. Use proper Markdown headings.

Correct Example:

# Introduction to Success and Perseverance

The speaker explains the importance of perseverance...

# The Value of Resilience

The speaker highlights...

Chunk Summaries:

{combined_text}
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
        max_completion_tokens=6000,
    )

    return (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


def generate_summary(
    video_id,
    duration
):
    """
    Generate hierarchical RAG summary.
    """

    chunks = get_all_video_chunks(
        video_id
    )

    if not chunks:
        return (
            "No transcript data available."
        )

    total_minutes = duration // 60
    total_seconds = duration % 60

    video_duration = (
        f"{total_minutes:02d}:"
        f"{total_seconds:02d}"
    )
    
    summary_size = get_summary_size(
        duration
    )

    chunk_summaries = []

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
            f"Generating summary batch "
            f"{i//BATCH_SIZE + 1}"
        )

        combined_chunk = (
            "\n\n".join(batch)
        )

        summary = summarize_chunk(
            combined_chunk
        )

        chunk_summaries.append(
            summary
        )

    print(
        "Generating final summary..."
    )

    final_summary = (
        combine_chunk_summaries(
            chunk_summaries,
            video_duration,
            summary_size
        )
    )

    return final_summary