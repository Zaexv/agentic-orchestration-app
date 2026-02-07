"""Pydantic Models for API Request/Response"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for /chat endpoint"""
    
    message: str = Field(
        ...,
        description="User's message/query",
        min_length=1,
        max_length=4000,
        examples=["What are my technical skills?"]
    )
    
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier for personalization"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID to continue conversation"
    )
    
    max_iterations: int = Field(
        10,
        description="Maximum iterations for agent execution",
        ge=1,
        le=20
    )


class AgentExecution(BaseModel):
    """Information about an agent execution"""
    
    agent_name: str = Field(..., description="Name of the agent")
    confidence: float = Field(..., description="Routing confidence")
    reasoning: Optional[str] = Field(None, description="Why this agent was chosen")
    timestamp: datetime


class ChatResponse(BaseModel):
    """Response model for /chat endpoint"""
    
    response: str = Field(..., description="Final response from the digital twin")
    
    agent_used: str = Field(..., description="Primary agent that handled the query")
    
    confidence: float = Field(
        ...,
        description="Confidence in routing decision",
        ge=0.0,
        le=1.0
    )
    
    session_id: str = Field(..., description="Session identifier")
    
    routing_history: list[AgentExecution] = Field(
        default_factory=list,
        description="History of agent executions"
    )
    
    iterations: int = Field(..., description="Number of iterations taken")
    
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    
    sources_used: Optional[list[str]] = Field(
        None,
        description="Sources/documents used for response (RAG)"
    )


class ErrorResponse(BaseModel):
    """Error response model"""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Service status")
    model: str = Field(..., description="LLM model being used")
    vector_store: str = Field(..., description="Vector store type")
    api_base: str = Field(..., description="OpenAI API base URL")
    timestamp: datetime = Field(default_factory=datetime.now)


class StateExampleResponse(BaseModel):
    """Response model for state structure example"""
    
    state_structure: dict = Field(..., description="Example agent state structure")
    note: str = Field(..., description="Explanatory note about the state")
