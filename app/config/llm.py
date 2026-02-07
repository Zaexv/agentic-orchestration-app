"""LLM Factory - Creates configured LLM instances"""

from langchain_openai import ChatOpenAI
from app.config.settings import settings


def get_llm(
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None
) -> ChatOpenAI:
    """
    Create a configured ChatOpenAI instance
    
    Args:
        model: Model name (defaults to settings.default_llm_model)
        temperature: Temperature setting (defaults to settings.llm_temperature)
        max_tokens: Max tokens (defaults to settings.max_tokens)
    
    Returns:
        Configured ChatOpenAI instance
    """
    # Use base_url parameter for custom endpoints
    kwargs = {
        "api_key": settings.openai_api_key,
        "model": model or settings.default_llm_model,
        "temperature": temperature if temperature is not None else settings.llm_temperature,
        "max_tokens": max_tokens or settings.max_tokens
    }
    
    # Only set base_url if it's not the default OpenAI API
    if settings.openai_api_base != "https://api.openai.com/v1":
        kwargs["base_url"] = settings.openai_api_base
    
    return ChatOpenAI(**kwargs)


def get_embedding_model():
    """
    Create a configured embedding model instance
    
    Returns:
        Configured OpenAI embeddings instance
    """
    from langchain_openai import OpenAIEmbeddings
    
    kwargs = {
        "api_key": settings.openai_api_key,
        "model": settings.embedding_model
    }
    
    # Only set base_url if it's not the default OpenAI API
    if settings.openai_api_base != "https://api.openai.com/v1":
        kwargs["base_url"] = settings.openai_api_base
    
    return OpenAIEmbeddings(**kwargs)
