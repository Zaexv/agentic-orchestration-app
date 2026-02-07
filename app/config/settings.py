"""Application Configuration Settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # OpenAI Configuration
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"  # OpenAI API endpoint
    
    # LangSmith Configuration (Optional)
    langsmith_api_key: str | None = None
    langsmith_tracing_v2: bool = False
    langsmith_project: str = "digital-twin"
    
    # Vector Store Configuration
    vector_store_type: Literal["chromadb", "pinecone"] = "chromadb"
    chroma_persist_dir: str = "./data/vector_stores"
    pinecone_api_key: str | None = None
    pinecone_environment: str | None = None
    
    # Model Configuration
    default_llm_model: str = "gpt-4o-mini"  # Updated to gpt-4o-mini for MW
    embedding_model: str = "text-embedding-3-small"
    llm_temperature: float = 0.1  # Updated to 0.1 for MW
    max_tokens: int = 4096
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Router Configuration
    routing_confidence_threshold: float = 0.7
    max_routing_iterations: int = 3
    
    # Safety Configuration
    max_agent_iterations: int = 10
    tool_timeout_seconds: int = 30


# Global settings instance
settings = Settings()
