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
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    pass

# ---------------------------------------------------------------------------
# Embedding Model Configuration
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Text Chunking Configuration
# ---------------------------------------------------------------------------
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 300

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
TOP_K_RESULTS: int = 5

# ---------------------------------------------------------------------------
# Groq Configuration
# ---------------------------------------------------------------------------
GROQ_MODEL_NAME: str = "llama-3.3-70b-versatile"

GROQ_API_URL: str = (
    "https://api.groq.com/openai/v1/chat/completions"
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
# Doubt Clarification (Chat) Prompt Template
# ---------------------------------------------------------------------------
DOUBT_PROMPT_TEMPLATE: str = """You are an educational AI tutor.

Answer only from the provided transcript context.

If information is unavailable in the transcript, reply:
"I could not find this information in the video."

Be conversational and explain concepts clearly, the way a helpful tutor would.
Do not invent information that isn't grounded in the transcript context below.

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