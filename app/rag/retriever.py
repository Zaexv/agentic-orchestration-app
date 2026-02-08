"""Retrieval Logic for RAG System

Provides retrieval functions for querying vector stores and
augmenting agent prompts with relevant context.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass

from app.rag.stores import get_vector_store_manager


@dataclass
class RetrievedDocument:
    """Represents a retrieved document with metadata."""
    content: str
    score: float  # Distance/similarity score (lower is better for distance)
    metadata: dict
    domain: str


class Retriever:
    """
    Handles retrieval from vector stores for RAG.
    """
    
    def __init__(self):
        """Initialize retriever with vector store manager."""
        self.vector_store = get_vector_store_manager()
    
    def retrieve(
        self,
        query: str,
        domain: str,
        top_k: int = 3,
        metadata_filter: Optional[dict] = None
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            domain: Agent domain to search in
            top_k: Number of documents to retrieve
            metadata_filter: Optional metadata filters
            
        Returns:
            List of retrieved documents
        """
        # Check if collection has documents
        count = self.vector_store.count_documents(domain)
        if count == 0:
            return []
        
        # Query vector store
        results = self.vector_store.query(
            domain=domain,
            query_text=query,
            n_results=top_k,
            metadata_filter=metadata_filter
        )
        
        # Parse results
        documents = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                doc = RetrievedDocument(
                    content=results['documents'][0][i],
                    score=results['distances'][0][i] if 'distances' in results else 0.0,
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                    domain=domain
                )
                documents.append(doc)
        
        return documents
    
    def format_context(self, documents: List[RetrievedDocument]) -> str:
        """
        Format retrieved documents into a context string for LLM.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return ""
        
        context_parts = ["Retrieved Context:"]
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source', 'Unknown')
            context_parts.append(f"\n[Document {i} - Source: {source}]")
            context_parts.append(doc.content)
        
        return "\n".join(context_parts)
    
    def retrieve_and_format(
        self,
        query: str,
        domain: str,
        top_k: int = 3,
        metadata_filter: Optional[dict] = None
    ) -> str:
        """
        Retrieve documents and format them as context string.
        
        Convenience method combining retrieve() and format_context().
        
        Args:
            query: Search query
            domain: Agent domain
            top_k: Number of documents to retrieve
            metadata_filter: Optional metadata filters
            
        Returns:
            Formatted context string
        """
        documents = self.retrieve(
            query=query,
            domain=domain,
            top_k=top_k,
            metadata_filter=metadata_filter
        )
        
        return self.format_context(documents)


# Singleton instance
_retriever: Optional[Retriever] = None


def get_retriever() -> Retriever:
    """
    Get singleton retriever instance.
    
    Returns:
        Retriever instance
    """
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
