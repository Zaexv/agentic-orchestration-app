"""Embedding utilities for RAG system

Provides OpenAI embedding model configuration and utility functions
for generating embeddings for documents and queries.
"""

from langchain_openai import OpenAIEmbeddings
from app.config.settings import settings


def get_embedding_model() -> OpenAIEmbeddings:
    """
    Get configured OpenAI embedding model.
    
    Uses text-embedding-3-small for cost-effectiveness and quality.
    
    Returns:
        OpenAIEmbeddings: Configured embedding model
    """
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key,
        openai_api_base=settings.openai_api_base,
    )


def embed_text(text: str) -> list[float]:
    """
    Generate embedding for a single text string.
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    embeddings = get_embedding_model()
    return embeddings.embed_query(text)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple documents.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    embeddings = get_embedding_model()
    return embeddings.embed_documents(texts)
