"""
utils/exceptions.py

Custom exception classes used throughout the application to provide
clear, specific error handling and user-friendly messages.
"""


class VideoAssistantError(Exception):
    """Base exception for all application-specific errors."""
    pass


class InvalidYouTubeURLError(VideoAssistantError):
    """Raised when the provided YouTube URL is invalid or video ID cannot be extracted."""
    pass


class TranscriptNotFoundError(VideoAssistantError):
    """Raised when a transcript is unavailable, disabled, or missing for a video."""
    pass


class TranscriptFetchError(VideoAssistantError):
    """Raised when the transcript fetch operation fails for any other reason."""
    pass


class EmbeddingGenerationError(VideoAssistantError):
    """Raised when embedding generation fails."""
    pass


class VectorStoreError(VideoAssistantError):
    """Raised when a ChromaDB operation fails (insertion, query, persistence)."""
    pass


class LLMGenerationError(VideoAssistantError):
    """Raised when the Gemini LLM API call fails or returns an invalid response."""
    pass


class EmptyQuestionError(VideoAssistantError):
    """Raised when the user submits an empty or whitespace-only question."""
    pass