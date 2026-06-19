"""
rag.py

Implements the Retrieval-Augmented Generation (RAG) question-answering
pipeline: takes retrieved transcript chunks and a user question, builds
a strict prompt, and queries the Groq Llama 3 API for a grounded answer.
"""

from typing import List

import requests

import config
from utils.exceptions import LLMGenerationError, EmptyQuestionError


def build_rag_prompt(retrieved_chunks: List[str], user_question: str) -> str:
    """
    Build the final prompt sent to the LLM, combining retrieved transcript
    context with the user's question using the configured template.

    Args:
        retrieved_chunks: List of relevant transcript chunks.
        user_question: The user's question.

    Returns:
        The fully formatted prompt string.
    """
    context = "\n\n".join(retrieved_chunks) if retrieved_chunks else "No context available."
    return config.RAG_PROMPT_TEMPLATE.format(
        retrieved_chunks=context,
        user_question=user_question,
    )


def call_groq_llm(prompt: str) -> str:
    """
    Send a prompt to the Groq API (Llama 3 model) and return the generated answer.

    Args:
        prompt: The fully constructed RAG prompt.

    Returns:
        The LLM-generated answer text.

    Raises:
        LLMGenerationError: If the API key is missing, the request fails,
            or the response is malformed.
    """
    if not config.GROQ_API_KEY:
        raise LLMGenerationError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )

    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": config.GROQ_MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": config.LLM_TEMPERATURE,
        "max_tokens": config.LLM_MAX_TOKENS,
    }

    try:
        response = requests.post(
            config.GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise LLMGenerationError("The request to Groq timed out. Please try again.")
    except requests.exceptions.HTTPError as exc:
        raise LLMGenerationError(f"Groq API returned an error: {str(exc)}")
    except requests.exceptions.RequestException as exc:
        raise LLMGenerationError(f"Failed to connect to Groq API: {str(exc)}")

    try:
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as exc:
        raise LLMGenerationError(f"Received an unexpected response format from Groq: {str(exc)}")

    return answer.strip()


def answer_question(retrieved_chunks: List[str], user_question: str) -> str:
    """
    High-level RAG entry point: validates the question, builds the prompt,
    and queries the LLM for a final grounded answer.

    Args:
        retrieved_chunks: List of relevant transcript chunks retrieved from ChromaDB.
        user_question: The user's question.

    Returns:
        The final answer string.

    Raises:
        EmptyQuestionError: If the question is empty or whitespace-only.
        LLMGenerationError: If the LLM call fails.
    """
    if not user_question or not user_question.strip():
        raise EmptyQuestionError("Please enter a question before submitting.")

    prompt = build_rag_prompt(retrieved_chunks, user_question.strip())
    return call_groq_llm(prompt)