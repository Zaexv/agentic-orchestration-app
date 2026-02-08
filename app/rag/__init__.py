"""RAG (Retrieval-Augmented Generation) System

Provides vector store management, document ingestion, and retrieval
for personalized agent responses.
"""

from app.rag.embeddings import get_embedding_model, embed_text, embed_documents
from app.rag.stores import get_vector_store_manager, VectorStoreManager, AGENT_DOMAINS
from app.rag.ingestion import get_ingestion_pipeline, DocumentIngestionPipeline
from app.rag.retriever import get_retriever, Retriever, RetrievedDocument

__all__ = [
    # Embeddings
    "get_embedding_model",
    "embed_text",
    "embed_documents",
    
    # Vector Stores
    "get_vector_store_manager",
    "VectorStoreManager",
    "AGENT_DOMAINS",
    
    # Ingestion
    "get_ingestion_pipeline",
    "DocumentIngestionPipeline",
    
    # Retrieval
    "get_retriever",
    "Retriever",
    "RetrievedDocument",
]
