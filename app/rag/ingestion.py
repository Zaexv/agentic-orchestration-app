"""Document Ingestion Pipeline for RAG System

Handles loading, chunking, and ingesting documents into vector stores.
Currently supports .txt files (PDF/DOCX require additional dependencies).

Note: Simplified to avoid Python 3.14 compatibility issues.
"""

from pathlib import Path
from typing import Optional, List
from datetime import datetime
import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.stores import get_vector_store_manager, AGENT_DOMAINS


class DocumentIngestionPipeline:
    """Pipeline for ingesting documents into agent-specific vector stores."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """Initialize ingestion pipeline."""
        self.vector_store = get_vector_store_manager()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_document(self, file_path: str) -> List[str]:
        """Load document from file and split into chunks."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == ".txt":
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.text_splitter.split_text(text)
        else:
            raise ValueError(f"Unsupported format: {suffix}. Only .txt supported currently.")
    
    def ingest_document(
        self,
        file_path: str,
        domain: str,
        source: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> int:
        """Ingest a document into a specific agent domain."""
        if domain not in AGENT_DOMAINS:
            raise ValueError(f"Invalid domain: {domain}")
        
        chunks = self.load_document(file_path)
        file_name = Path(file_path).name
        base_metadata = {
            "source": source or file_name,
            "file_name": file_name,
            "domain": domain,
            "ingestion_date": datetime.now().isoformat(),
            "chunk_count": len(chunks),
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        ids = []
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{file_path}_{i}_{chunk[:100]}".encode()).hexdigest()
            ids.append(chunk_id)
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = i
            metadatas.append(chunk_metadata)
        
        self.vector_store.add_documents(
            domain=domain,
            texts=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(chunks)
    
    def ingest_directory(
        self,
        directory_path: str,
        domain: str,
        recursive: bool = False,
        file_extensions: Optional[List[str]] = None
    ) -> dict:
        """Ingest all documents from a directory."""
        if file_extensions is None:
            file_extensions = [".txt"]
        
        path = Path(directory_path)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")
        
        pattern = "**/*" if recursive else "*"
        files = [
            f for f in path.glob(pattern)
            if f.is_file() and f.suffix.lower() in file_extensions
        ]
        
        results = {
            "files_processed": 0,
            "total_chunks": 0,
            "files": []
        }
        
        for file_path in files:
            try:
                chunks = self.ingest_document(str(file_path), domain=domain, source=file_path.stem)
                results["files_processed"] += 1
                results["total_chunks"] += chunks
                results["files"].append({
                    "path": str(file_path),
                    "chunks": chunks,
                    "status": "success"
                })
            except Exception as e:
                results["files"].append({
                    "path": str(file_path),
                    "status": "error",
                    "error": str(e)
                })
        
        return results


def get_ingestion_pipeline() -> DocumentIngestionPipeline:
    """Get document ingestion pipeline instance."""
    return DocumentIngestionPipeline()
