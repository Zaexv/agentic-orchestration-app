"""Vector Store Management for RAG System

Manages ChromaDB collections for each agent domain, providing
persistent vector storage with easy retrieval.

Note: Python 3.14 has Pydantic V1 compatibility warnings with ChromaDB.
This is a known issue but doesn't affect functionality.
"""

import warnings
# Suppress Pydantic V1 warnings for Python 3.14
warnings.filterwarnings('ignore', category=UserWarning, message='.*Pydantic V1.*')

import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
from typing import Optional

from app.rag.embeddings import get_embedding_model


# Agent domains
AGENT_DOMAINS = [
    "professional",
    "communication", 
    "knowledge",
    "decision",
    "general",
    "shared"  # Shared memory across all agents
]


class VectorStoreManager:
    """
    Manages vector stores for all agent domains.
    
    Now includes a shared memory collection accessible by all agents.
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize vector store manager.
        
        Args:
            persist_directory: Directory for ChromaDB persistence
                              Defaults to data/vector_stores/
        """
        if persist_directory is None:
            persist_directory = str(Path(__file__).parent.parent.parent / "data" / "vector_stores")
        
        # Create directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.embedding_model = get_embedding_model()
        self.collections = {}
        
        # Initialize collections for each domain
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Create or get existing collections for each agent domain."""
        for domain in AGENT_DOMAINS:
            collection_name = f"{domain}_kb"
            
            # Get or create collection
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"domain": domain}
            )
            
            self.collections[domain] = collection
    
    def get_collection(self, domain: str):
        """
        Get ChromaDB collection for a specific agent domain.
        
        Args:
            domain: Agent domain (professional, communication, etc.)
            
        Returns:
            ChromaDB collection
            
        Raises:
            ValueError: If domain is not valid
        """
        if domain not in AGENT_DOMAINS:
            raise ValueError(f"Invalid domain: {domain}. Must be one of {AGENT_DOMAINS}")
        
        return self.collections[domain]
    
    def add_documents(
        self,
        domain: str,
        texts: list[str],
        metadatas: list[dict],
        ids: list[str]
    ):
        """
        Add documents to a domain's vector store.
        
        Args:
            domain: Agent domain
            texts: Document texts
            metadatas: Metadata for each document
            ids: Unique IDs for each document
        """
        collection = self.get_collection(domain)
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_documents(texts)
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def query(
        self,
        domain: str,
        query_text: str,
        n_results: int = 3,
        metadata_filter: Optional[dict] = None
    ) -> dict:
        """
        Query a domain's vector store.
        
        Args:
            domain: Agent domain
            query_text: Query string
            n_results: Number of results to return
            metadata_filter: Optional metadata filters
            
        Returns:
            Query results with documents, distances, and metadata
        """
        collection = self.get_collection(domain)
        
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query_text)
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=metadata_filter
        )
        
        return results
    
    def count_documents(self, domain: str) -> int:
        """
        Get document count for a domain.
        
        Args:
            domain: Agent domain
            
        Returns:
            Number of documents in the collection
        """
        collection = self.get_collection(domain)
        return collection.count()
    
    def reset_collection(self, domain: str):
        """
        Delete all documents from a domain's collection.
        
        Args:
            domain: Agent domain
        """
        collection_name = f"{domain}_kb"
        self.client.delete_collection(collection_name)
        
        # Recreate empty collection
        collection = self.client.create_collection(
            name=collection_name,
            metadata={"domain": domain}
        )
        self.collections[domain] = collection
    
    def reset_all(self):
        """Delete all collections and reinitialize."""
        for domain in AGENT_DOMAINS:
            self.reset_collection(domain)


# Singleton instance
_vector_store_manager: Optional[VectorStoreManager] = None


def get_vector_store_manager() -> VectorStoreManager:
    """
    Get singleton vector store manager instance.
    
    Returns:
        VectorStoreManager instance
    """
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager
