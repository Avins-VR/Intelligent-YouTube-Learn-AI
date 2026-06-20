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
    return f"{config.CHROMA_COLLECTION_PREFIX}{video_id}"


def chunk_transcript(cleaned_text: str) -> List[str]:
    """
    Split cleaned transcript text into semantic chunks using
    RecursiveCharacterTextSplitter.
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
        return False


def create_and_store_embeddings(video_id: str, chunks: List[str]) -> int:
    """
    Generate embeddings for each chunk and store them in a ChromaDB
    collection dedicated to this video. Skips insertion if the video
    has already been processed.
    """
    if video_already_processed(video_id):
        return 0

    model = get_embedding_model()

    try:
        embeddings = model.encode(
            chunks,
            normalize_embeddings=True,
            show_progress_bar=False
        ).tolist()
    except Exception as exc:
        raise EmbeddingGenerationError(f"Failed to generate embeddings: {str(exc)}")

    client = get_chroma_client()
    collection_name = get_collection_name(video_id)

    try:
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
    """
    if top_k is None:
        top_k = config.TOP_K_RESULTS

    model = get_embedding_model()

    try:
        question_embedding = model.encode(
            [question],
            normalize_embeddings=True,
            show_progress_bar=False
        ).tolist()
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


def get_all_video_chunks(video_id: str) -> List[str]:

    client = get_chroma_client()

    collection = client.get_collection(
        get_collection_name(video_id)
    )

    data = collection.get(
        include=["documents", "metadatas"]
    )

    documents = data["documents"]
    metadatas = data["metadatas"]

    sorted_docs = [
        doc
        for _, doc in sorted(
            zip(
                [m["chunk_index"] for m in metadatas],
                documents
            )
        )
    ]

    return sorted_docs