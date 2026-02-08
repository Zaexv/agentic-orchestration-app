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
        "default_user",
        description="User identifier for personalization"
    )
    
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID to continue existing conversation"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID to continue conversation"
    )
    
    max_iterations: int = Field(
        5,
        description="Maximum iterations for agent execution (enables multi-turn reasoning)",
        ge=1,
        le=10
    )


class IterationDetail(BaseModel):
    """Detail about what happened in an iteration"""
    
    iteration: int = Field(..., description="Iteration number")
    agent: str = Field(..., description="Agent that executed")
    action: str = Field(..., description="What happened")
    confidence: float = Field(..., description="Confidence score")
    reasoning: Optional[str] = Field(None, description="Why this happened")
    timestamp: datetime


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
    
    conversation_id: Optional[str] = Field(None, description="Conversation identifier for persistence")
    
    routing_history: list[AgentExecution] = Field(
        default_factory=list,
        description="History of agent executions (DEPRECATED - use iteration_details)"
    )
    
    iteration_details: list[IterationDetail] = Field(
        default_factory=list,
        description="Detailed log of what happened in each iteration"
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


class ConversationResponse(BaseModel):
    """Response model for conversation data"""
    
    id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages in conversation")


class MessageResponse(BaseModel):
    """Response model for message data"""
    
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    agent: Optional[str] = Field(None, description="Agent that generated response")
    confidence: Optional[float] = Field(None, description="Routing confidence")
    processing_time_ms: Optional[float] = Field(None, description="Processing time")
    timestamp: datetime = Field(..., description="Message timestamp")


class ConversationListResponse(BaseModel):
    """Response model for list of conversations"""
    
    conversations: list[ConversationResponse] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")


class ConversationMessagesResponse(BaseModel):
    """Response model for conversation messages"""
    
    conversation_id: str = Field(..., description="Conversation ID")
    messages: list[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")
