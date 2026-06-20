"""
rag.py

Implements the Retrieval-Augmented Generation (RAG) question-answering
pipeline using Groq.
"""

from typing import List

from groq import Groq

import config
from utils.exceptions import (
    LLMGenerationError,
    EmptyQuestionError
)


_client = None


def _get_client():
    """
    Lazily create and cache the Groq client.
    """

    global _client

    if _client is None:

        if not config.GROQ_API_KEY:
            raise LLMGenerationError(
                "GROQ_API_KEY is not set. Please add it to your .env file."
            )

        _client = Groq(
            api_key=config.GROQ_API_KEY
        )

    return _client


def build_rag_prompt(
    retrieved_chunks: List[str],
    user_question: str
) -> str:
    """
    Build the final prompt sent to Groq.
    """

    if not retrieved_chunks:
        return (
            "I could not find any relevant information "
            "in the video transcript."
        )

    context = "\n\n".join(
        retrieved_chunks
    )

    return config.RAG_PROMPT_TEMPLATE.format(
        retrieved_chunks=context,
        user_question=user_question,
    )


def call_groq_llm(
    prompt: str
) -> str:
    """
    Send prompt to Groq and return response.
    """

    client = _get_client()

    try:

        response = client.chat.completions.create(
            model=config.GROQ_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=config.LLM_TEMPERATURE,
            max_completion_tokens=config.LLM_MAX_TOKENS,
        )

        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        print("\n============================")
        print("GROQ RESPONSE:")
        print(content)
        print("============================\n")

        return content

    except Exception as exc:

        raise LLMGenerationError(
            f"Groq API Error: {str(exc)}"
        )


def build_doubt_prompt(
    retrieved_chunks: List[str],
    user_question: str
) -> str:
    """
    Build the prompt for the conversational
    Doubt Clarification tutor chat.
    """

    context = (
        "\n\n".join(retrieved_chunks)
        if retrieved_chunks
        else "No context available."
    )

    return config.DOUBT_PROMPT_TEMPLATE.format(
        retrieved_chunks=context,
        user_question=user_question,
    )


def answer_doubt(
    retrieved_chunks: List[str],
    user_question: str
) -> str:
    """
    Entry point for the Doubt Clarification chat feature.
    Uses the same Groq call as answer_question,
    but with a conversational tutor prompt.
    """

    if not user_question or not user_question.strip():

        raise EmptyQuestionError(
            "Please enter a question before submitting."
        )

    prompt = build_doubt_prompt(
        retrieved_chunks,
        user_question.strip()
    )

    return call_groq_llm(
        prompt
    )


def answer_question(
    retrieved_chunks: List[str],
    user_question: str
) -> str:
    """
    Main RAG entry point.
    """

    if not user_question or not user_question.strip():

        raise EmptyQuestionError(
            "Please enter a question before submitting."
        )

    prompt = build_rag_prompt(
        retrieved_chunks,
        user_question.strip()
    )

    return call_groq_llm(
        prompt
    )