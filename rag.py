"""
rag.py

Implements the Retrieval-Augmented Generation (RAG) question-answering
pipeline using Google Gemini.
"""

from typing import List

import google.generativeai as genai

import config
from utils.exceptions import LLMGenerationError, EmptyQuestionError


def build_rag_prompt(retrieved_chunks: List[str], user_question: str) -> str:
    """
    Build the final prompt sent to Gemini.
    """

    context = (
        "\n\n".join(retrieved_chunks)
        if retrieved_chunks
        else "No context available."
    )

    return config.RAG_PROMPT_TEMPLATE.format(
        retrieved_chunks=context,
        user_question=user_question,
    )


def call_gemini_llm(prompt: str) -> str:
    """
    Send prompt to Gemini and return response.
    """

    if not config.GEMINI_API_KEY:
        raise LLMGenerationError(
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )

    try:
        # Configure Gemini
        genai.configure(api_key=config.GEMINI_API_KEY)

        # Load model
        model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL_NAME
        )

        # Generate response
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": config.LLM_TEMPERATURE,
                "max_output_tokens": config.LLM_MAX_TOKENS,
            }
        )

        return response.text.strip()

    except Exception as exc:
        raise LLMGenerationError(
            f"Gemini API Error: {str(exc)}"
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

    return call_gemini_llm(prompt)