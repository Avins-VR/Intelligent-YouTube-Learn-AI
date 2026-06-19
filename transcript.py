"""
transcript.py

Handles all operations related to extracting and preparing YouTube video
transcripts:
    - Parsing/validating YouTube URLs to extract the video ID.
    - Fetching transcripts via yt-dlp.
    - Combining transcript segments into a single clean text document.
"""

import re

import yt_dlp
import requests

from utils.exceptions import (
    InvalidYouTubeURLError,
    TranscriptNotFoundError,
    TranscriptFetchError,
)

from utils.text_cleaning import clean_transcript_text


# Regex patterns covering the common YouTube URL formats:
#   https://www.youtube.com/watch?v=VIDEO_ID
#   https://youtu.be/VIDEO_ID
#   https://www.youtube.com/embed/VIDEO_ID
#   https://www.youtube.com/shorts/VIDEO_ID
#   Plain 11-character video IDs
_YOUTUBE_URL_PATTERNS = [
    r"(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})",
    r"(?:youtu\.be\/)([a-zA-Z0-9_-]{11})",
    r"(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
    r"(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})",
    r"^([a-zA-Z0-9_-]{11})$",
]


def extract_video_id(youtube_url: str) -> str:
    """
    Extract the 11-character YouTube video ID from a given URL.

    Args:
        youtube_url: A YouTube URL (or raw video ID) provided by the user.

    Returns:
        The extracted video ID.

    Raises:
        InvalidYouTubeURLError: If no valid video ID could be extracted.
    """
    if not youtube_url or not youtube_url.strip():
        raise InvalidYouTubeURLError("Please provide a YouTube URL.")

    cleaned_url = youtube_url.strip()

    for pattern in _YOUTUBE_URL_PATTERNS:
        match = re.search(pattern, cleaned_url)
        if match:
            return match.group(1)

    raise InvalidYouTubeURLError(
        "The provided URL does not appear to be a valid YouTube video link."
    )


def fetch_transcript(video_id: str):

    try:
        url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            "skip_download": True,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration", 0)
        subtitles = info.get("subtitles", {})

        if "en" not in subtitles:

            subtitles = info.get("automatic_captions", {})

        if "en" not in subtitles:
            raise TranscriptNotFoundError(
                "English subtitles not available."
            )
        json_url = None

        for subtitle in subtitles["en"]:
            if subtitle["ext"] == "json3":
                json_url = subtitle["url"]
                break

        if not json_url:
            raise TranscriptNotFoundError(
                "JSON subtitles not available."
            )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        }

        import time

        time.sleep(2)

        response = requests.get(
            json_url,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        transcript_parts = []

        for event in data.get("events", []):

            if "segs" not in event:
                continue

            start_seconds = int(event.get("tStartMs", 0) / 1000)

            minutes = start_seconds // 60
            seconds = start_seconds % 60

            timestamp = f"[{minutes:02d}:{seconds:02d}]"

            text = "".join(
                seg.get("utf8", "")
                for seg in event["segs"]
            ).strip()

            if text:
                transcript_parts.append(
                    f"{timestamp} {text}"
                )

        transcript_text = "\n".join(transcript_parts)

        if not transcript_text.strip():
            raise TranscriptNotFoundError(
                "Transcript is empty."
            )

        return transcript_text, duration

    except TranscriptNotFoundError:
        raise

    except Exception as exc:
        raise TranscriptFetchError(
            f"Failed to fetch transcript: {str(exc)}"
        )

def get_processed_transcript(youtube_url: str) -> dict:
    """
    High-level helper that extracts the video ID, fetches the transcript,
    and returns both the raw and cleaned versions along with metadata.

    Args:
        youtube_url: The YouTube URL provided by the user.

    Returns:
        A dictionary with keys: video_id, raw_transcript, cleaned_transcript.

    Raises:
        InvalidYouTubeURLError, TranscriptNotFoundError, TranscriptFetchError
    """
    video_id = extract_video_id(youtube_url)
    raw_transcript, duration = fetch_transcript(video_id)
    cleaned_transcript = clean_transcript_text(raw_transcript)

    return {
        "video_id": video_id,
        "raw_transcript": raw_transcript,
        "cleaned_transcript": cleaned_transcript,
        "duration": duration,
    }