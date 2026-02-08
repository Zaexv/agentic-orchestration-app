"""State Management for Digital Twin Agent Orchestration

This module defines the state schema used across all agents in the system.
The state is shared between agents and maintains conversation history, routing
information, and retrieved context.
"""

from typing import TypedDict, Annotated, Optional
from operator import add
from datetime import datetime
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Message model for conversation history"""
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    agent: Optional[str] = Field(None, description="Agent that generated this message")


class RoutingDecision(BaseModel):
    """Routing decision metadata"""
    target_agent: str = Field(..., description="Agent to route to")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reasoning: Optional[str] = Field(None, description="Why this agent was selected")
    timestamp: datetime = Field(default_factory=datetime.now)


class RetrievedDocument(BaseModel):
    """Document retrieved from vector store"""
    content: str = Field(..., description="Document content")
    source: str = Field(..., description="Document source")
    score: float = Field(..., description="Relevance score")
    agent_domain: str = Field(..., description="Which agent's domain (professional, communication, etc)")


class IterationLog(BaseModel):
    """Log entry for each iteration"""
    iteration: int = Field(..., description="Iteration number")
    agent: str = Field(..., description="Agent that executed")
    action: str = Field(..., description="What happened in this iteration")
    confidence: float = Field(..., description="Routing confidence")
    reasoning: Optional[str] = Field(None, description="Why this happened")
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentState(TypedDict):
    """
    Central state object shared across all agents in the graph.
    
    Uses Annotated with reducers to control how state is updated:
    - add: Accumulates items into a list
    - replace (default): Overwrites the previous value
    """
    
    # Conversation History (accumulated)
    messages: Annotated[list[Message], add]
    
    # Routing Information (replaced)
    current_agent: str  # Current executing agent
    next_agent: Optional[str]  # Next agent to route to
    routing_history: Annotated[list[RoutingDecision], add]  # History of routing decisions
    routing_confidence: float  # Confidence of current routing decision
    
    # Iteration Tracking (accumulated)
    iteration_log: Annotated[list[IterationLog], add]  # What happened in each iteration
    
    # Retrieved Context (replaced per query)
    retrieved_docs: list[RetrievedDocument]  # Documents from RAG
    rag_query: Optional[str]  # Query used for retrieval
    
    # User Context (replaced)
    user_id: Optional[str]  # User identifier
    session_id: str  # Session identifier
    user_query: str  # Original user query
    
    # Control Flow (replaced)
    iterations: int  # Current iteration count
    max_iterations: int  # Maximum allowed iterations
    should_continue: bool  # Whether to continue or end
    
    # Final Output (replaced)
    final_response: Optional[str]  # Final response to user
    
    # Metadata (replaced)
    started_at: datetime
    updated_at: datetime
    error: Optional[str]  # Error message if something failed


def create_initial_state(
    user_query: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    max_iterations: int = 5
) -> AgentState:
    """
    Create initial state for a new conversation turn.
    
    Args:
        user_query: The user's input query
        user_id: Optional user identifier
        session_id: Optional session identifier (generated if not provided)
        max_iterations: Maximum iterations allowed
        
    Returns:
        AgentState: Initial state object
    """
    now = datetime.now()
    
    return AgentState(
        # Conversation
        messages=[Message(role="user", content=user_query, timestamp=now)],
        
        # Routing
        current_agent="router",  # Always start with router
        next_agent=None,
        routing_history=[],
        routing_confidence=0.0,
        
        # Iteration tracking
        iteration_log=[],
        
        # RAG
        retrieved_docs=[],
        rag_query=None,
        
        # User Context
        user_id=user_id,
        session_id=session_id or f"session_{now.timestamp()}",
        user_query=user_query,
        
        # Control Flow
        iterations=0,
        max_iterations=max_iterations,
        should_continue=True,
        
        # Output
        final_response=None,
        
        # Metadata
        started_at=now,
        updated_at=now,
        error=None
    )


def add_message(state: AgentState, role: str, content: str, agent: Optional[str] = None) -> AgentState:
    """
    Helper function to add a message to state.
    
    Args:
        state: Current state
        role: Message role (user/assistant/system)
        content: Message content
        agent: Agent that generated the message
        
    Returns:
        Updated state with new message
    """
    state["messages"].append(
        Message(role=role, content=content, agent=agent, timestamp=datetime.now())
    )
    state["updated_at"] = datetime.now()
    return state


def update_routing(
    state: AgentState,
    target_agent: str,
    confidence: float,
    reasoning: Optional[str] = None
) -> AgentState:
    """
    Helper function to update routing information.
    
    Args:
        state: Current state
        target_agent: Agent to route to
        confidence: Confidence score
        reasoning: Optional reasoning for the decision
        
    Returns:
        Updated state with routing info
    """
    decision = RoutingDecision(
        target_agent=target_agent,
        confidence=confidence,
        reasoning=reasoning
    )
    
    state["routing_history"].append(decision)
    state["next_agent"] = target_agent
    state["routing_confidence"] = confidence
    state["updated_at"] = datetime.now()
    
    return state


def increment_iteration(state: AgentState) -> AgentState:
    """
    Increment iteration counter and check if max is reached.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with incremented iteration
    """
    state["iterations"] += 1
    
    if state["iterations"] >= state["max_iterations"]:
        state["should_continue"] = False
        state["error"] = f"Max iterations ({state['max_iterations']}) reached"
    
    state["updated_at"] = datetime.now()
    return state
