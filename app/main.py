"""FastAPI Main Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.routes import router as api_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Digital Twin AI",
    description="Multi-agent AI digital twin with router orchestration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api", tags=["chat"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Digital Twin AI application...")
    logger.info(f"Using LLM model: {settings.default_llm_model}")
    logger.info(f"OpenAI API base: {settings.openai_api_base}")
    logger.info(f"Vector store type: {settings.vector_store_type}")
    
    # Enable LangSmith tracing if configured
    if settings.langsmith_tracing_v2:
        logger.info(f"LangSmith tracing enabled for project: {settings.langsmith_project}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down Digital Twin AI application...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Digital Twin AI API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/chat",
            "state_example": "/api/state/example",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": settings.default_llm_model,
        "vector_store": settings.vector_store_type,
        "api_base": settings.openai_api_base
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
