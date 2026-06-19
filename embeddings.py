"""
embeddings.py

Handles:
    - Splitting cleaned transcript text into semantic chunks.
    - Generating embeddings for those chunks using Sentence Transformers.
    - Storing/retrieving chunks and embeddings in ChromaDB.
    - Preventing duplicate insertion of the same video's data.
"""

from typing import List, Optional

import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

import config
from utils.exceptions import EmbeddingGenerationError, VectorStoreError


# ---------------------------------------------------------------------------
# Embedding model (loaded once and cached at module level)
# ---------------------------------------------------------------------------
_embedding_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """
    Lazily load and cache the Sentence Transformer embedding model.

    Returns:
        The loaded SentenceTransformer instance.

    Raises:
        EmbeddingGenerationError: If the model fails to load.
    """
    global _embedding_model
    if _embedding_model is None:
        try:
            _embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        except Exception as exc:
            raise EmbeddingGenerationError(
                f"Failed to load embedding model '{config.EMBEDDING_MODEL_NAME}': {str(exc)}"
            )
    return _embedding_model


# ---------------------------------------------------------------------------
# ChromaDB client (loaded once and cached at module level)
# ---------------------------------------------------------------------------
_chroma_client: Optional[chromadb.api.ClientAPI] = None


def get_chroma_client() -> chromadb.api.ClientAPI:
    """
    Lazily create and cache a persistent ChromaDB client.

    Returns:
        The ChromaDB PersistentClient instance.

    Raises:
        VectorStoreError: If the client fails to initialize.
    """
    global _chroma_client
    if _chroma_client is None:
        try:
            _chroma_client = chromadb.PersistentClient(
                path=config.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(anonymized_telemetry=False),
            )
        except Exception as exc:
            raise VectorStoreError(f"Failed to initialize ChromaDB client: {str(exc)}")
    return _chroma_client


def get_collection_name(video_id: str) -> str:
    """Build a deterministic, valid ChromaDB collection name for a video ID."""
    # ChromaDB collection names must be alphanumeric (+ underscores/hyphens),
    # 3-63 characters. Video IDs can contain '-' and '_' which are safe.
    return f"{config.CHROMA_COLLECTION_PREFIX}{video_id}"


def chunk_transcript(cleaned_text: str) -> List[str]:
    """
    Split cleaned transcript text into semantic chunks using
    RecursiveCharacterTextSplitter.

    Args:
        cleaned_text: The cleaned transcript text.

    Returns:
        A list of text chunks.

    Raises:
        EmbeddingGenerationError: If chunking produces no usable chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(cleaned_text)
    chunks = [chunk.strip() for chunk in chunks if chunk and chunk.strip()]

    if not chunks:
        raise EmbeddingGenerationError("Transcript chunking produced no usable text chunks.")

    return chunks


def video_already_processed(video_id: str) -> bool:
    """
    Check whether a video's chunks have already been stored in ChromaDB,
    to prevent duplicate insertion.

    Args:
        video_id: The YouTube video ID.

    Returns:
        True if a non-empty collection already exists for this video.
    """
    client = get_chroma_client()
    collection_name = get_collection_name(video_id)

    try:
        existing_collections = [c.name for c in client.list_collections()]
        if collection_name not in existing_collections:
            return False

        collection = client.get_collection(collection_name)
        return collection.count() > 0
    except Exception:
        # If anything goes wrong checking existence, default to "not processed"
        # so the pipeline can attempt (re)creation safely.
        return False


def create_and_store_embeddings(video_id: str, chunks: List[str]) -> int:
    """
    Generate embeddings for each chunk and store them in a ChromaDB
    collection dedicated to this video. Skips insertion if the video
    has already been processed.

    Args:
        video_id: The YouTube video ID (used to scope the collection).
        chunks: List of transcript text chunks.

    Returns:
        The number of chunks stored (0 if skipped due to duplicate).

    Raises:
        EmbeddingGenerationError: If embedding generation fails.
        VectorStoreError: If storing in ChromaDB fails.
    """
    if video_already_processed(video_id):
        return 0

    model = get_embedding_model()

    try:
        embeddings = model.encode(chunks, show_progress_bar=False).tolist()
    except Exception as exc:
        raise EmbeddingGenerationError(f"Failed to generate embeddings: {str(exc)}")

    client = get_chroma_client()
    collection_name = get_collection_name(video_id)

    try:
        # Ensure a clean slate in case a partial collection exists
        existing_collections = [c.name for c in client.list_collections()]
        if collection_name in existing_collections:
            client.delete_collection(collection_name)

        collection = client.create_collection(
            name=collection_name,
            metadata={"video_id": video_id},
        )

        ids = [f"{video_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"video_id": video_id, "chunk_index": i} for i in range(len(chunks))]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
    except Exception as exc:
        raise VectorStoreError(f"Failed to store embeddings in ChromaDB: {str(exc)}")

    return len(chunks)


def query_video_chunks(video_id: str, question: str, top_k: Optional[int] = None) -> List[str]:
    """
    Convert a user question into an embedding and retrieve the top
    most relevant transcript chunks for a given video.

    Args:
        video_id: The YouTube video ID whose collection should be queried.
        question: The user's natural-language question.
        top_k: Number of top results to retrieve (defaults to config.TOP_K_RESULTS).

    Returns:
        A list of the most relevant chunk texts, ordered by relevance.

    Raises:
        EmbeddingGenerationError: If embedding the question fails.
        VectorStoreError: If querying ChromaDB fails.
    """
    if top_k is None:
        top_k = config.TOP_K_RESULTS

    model = get_embedding_model()

    try:
        question_embedding = model.encode([question], show_progress_bar=False).tolist()
    except Exception as exc:
        raise EmbeddingGenerationError(f"Failed to generate embedding for question: {str(exc)}")

    client = get_chroma_client()
    collection_name = get_collection_name(video_id)

    try:
        collection = client.get_collection(collection_name)
        results = collection.query(
            query_embeddings=question_embedding,
            n_results=top_k,
        )
    except Exception as exc:
        raise VectorStoreError(f"Failed to query ChromaDB collection: {str(exc)}")

    documents = results.get("documents", [[]])
    return documents[0] if documents else []

def get_all_video_chunks(video_id):

    client = get_chroma_client()

    collection_name = get_collection_name(video_id)

    collection = client.get_collection(
        collection_name
    )

    data = collection.get()

    return data.get("documents", [])