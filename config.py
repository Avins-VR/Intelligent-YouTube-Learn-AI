"""
config.py

Centralized configuration for the Video Learning Assistant.
Loads environment variables and defines global constants used
across the application.
"""

import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    pass

# ---------------------------------------------------------------------------
# Embedding Model Configuration
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Text Chunking Configuration
# ---------------------------------------------------------------------------
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 100

# ---------------------------------------------------------------------------
# ChromaDB Configuration
# ---------------------------------------------------------------------------
CHROMA_PERSIST_DIRECTORY: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chroma_db"
)

CHROMA_COLLECTION_PREFIX: str = "video_"

# ---------------------------------------------------------------------------
# Retrieval Configuration
# ---------------------------------------------------------------------------
TOP_K_RESULTS: int = 3

# ---------------------------------------------------------------------------
# Gemini Configuration
# ---------------------------------------------------------------------------
GEMINI_MODEL_NAME: str = "gemini-2.5-flash"

GEMINI_API_URL: str = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL_NAME}:generateContent"
)

LLM_TEMPERATURE: float = 0.2
LLM_MAX_TOKENS: int = 1024

# ---------------------------------------------------------------------------
# RAG Prompt Template
# ---------------------------------------------------------------------------
RAG_PROMPT_TEMPLATE: str = """You are an educational AI assistant.

Answer only from the provided transcript context.

If the answer is not available in the transcript, respond:
"I could not find this information in the video transcript."

Context:
{retrieved_chunks}

Question:
{user_question}

Answer:"""

# ---------------------------------------------------------------------------
# Application Metadata
# ---------------------------------------------------------------------------
APP_TITLE: str = "🎓 AI-Powered Educational Video Learning Assistant"

APP_DESCRIPTION: str = (
    "Paste a YouTube video URL, let the AI process its transcript, "
    "and ask questions strictly answered from the video's content."
)