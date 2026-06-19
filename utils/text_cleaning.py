"""
utils/text_cleaning.py

Text preprocessing utilities for cleaning raw YouTube transcript text
before chunking and embedding.
"""

import re


def clean_transcript_text(raw_text: str) -> str:
    """
    Clean raw transcript text for downstream NLP processing.

    Steps performed:
        1. Collapse multiple whitespace characters into a single space.
        2. Remove unnecessary symbols/artifacts common in auto-generated
           transcripts (e.g., '[Music]', '[Applause]', stray brackets).
        3. Normalize punctuation spacing.
        4. Strip leading/trailing whitespace.

    Educational content (numbers, technical terms, punctuation that carries
    meaning) is preserved.

    Args:
        raw_text: The raw, unprocessed transcript text.

    Returns:
        A cleaned, normalized string ready for chunking.
    """
    if not raw_text:
        return ""

    text = raw_text

    # Remove common auto-caption artifacts like [Music], [Applause], (laughs)
    text = re.sub(
        r"\[(?!\d{2}:\d{2}\])[^]]*\]",
        " ",
        text
    )
    text = re.sub(r"\([^)]*\)", " ", text)

    # Remove unusual symbols but keep standard punctuation used in education
    # (letters, numbers, basic punctuation, and common math symbols)
    text = re.sub(
        r"[^\w\s\[\].,;:!?'\"%/\-+=]",
        " ",
        text
    )

    # Collapse multiple whitespace/newlines/tabs into a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Fix spacing before punctuation (e.g., "word ." -> "word.")
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)

    return text.strip()


def get_text_stats(text: str) -> dict:
    """
    Compute basic statistics about a piece of text.

    Args:
        text: The text to analyze.

    Returns:
        Dictionary containing character count and approximate word count.
    """
    return {
        "character_count": len(text),
        "word_count": len(text.split()) if text else 0,
    }