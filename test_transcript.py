# test_transcript.py

from transcript import get_processed_transcript

data = get_processed_transcript(
    "https://www.youtube.com/watch?v=aircAruvnKk"
)

print(data["video_id"])
print(data["cleaned_transcript"][:500])