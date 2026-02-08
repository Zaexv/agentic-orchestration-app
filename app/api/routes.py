"""
API routes for the Digital Twin AI system.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import time

from app.api.models import (
    ChatRequest,
    ChatResponse,
    AgentExecution,
    StateExampleResponse,
    ConversationResponse,
    ConversationListResponse,
    ConversationMessagesResponse,
    MessageResponse,
)
from app.database import get_db
from app.services.conversation import ConversationService
from app.orchestration.state import (
    AgentState,
    Message,
    RoutingDecision,
    create_initial_state,
)
from app.orchestration.graph import run_workflow
from app.agents import (
    general_agent,
    professional_agent,
    communication_agent,
    knowledge_agent,
    decision_agent,
)
from app.agents.router import router_agent_with_fallback

router = APIRouter(tags=["chat"])

# Agent registry for easy lookup
AGENT_REGISTRY = {
    "general": general_agent,
    "professional": professional_agent,
    "communication": communication_agent,
    "knowledge": knowledge_agent,
    "decision": decision_agent,
}


@router.post("/chat/graph", response_model=ChatResponse)
async def chat_with_graph(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint using LangGraph workflow (Phase 5).
    
    Uses the StateGraph workflow for routing and execution, enabling:
    - Visual workflow representation
    - Multi-turn conversations (future)
    - Agent-to-agent handoffs (future)
    - Better debugging with LangGraph Studio
    
    Flow:
    1. Create initial state
    2. Run through compiled StateGraph workflow
    3. Return final response
    """
    start_time = time.time()
    
    # Create initial state
    state = create_initial_state(
        user_query=request.message,
        user_id=request.user_id,
        max_iterations=request.max_iterations
    )
    
    # Run through the graph workflow
    try:
        final_state = run_workflow(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")
    
    # Get the agent's response (last message)
    agent_response = final_state["messages"][-1].content
    
    # Get routing info
    latest_routing = final_state["routing_history"][-1] if final_state["routing_history"] else None
    agent_used = latest_routing.target_agent if latest_routing else "general"
    confidence = latest_routing.confidence if latest_routing else 0.0
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Build response
    return ChatResponse(
        response=agent_response,
        agent_used=agent_used,
        confidence=confidence,
        session_id=final_state["session_id"],
        routing_history=[
            AgentExecution(
                agent_name=rd.target_agent,
                confidence=rd.confidence,
                reasoning=rd.reasoning,
                timestamp=rd.timestamp,
            )
            for rd in final_state["routing_history"]
        ],
        iterations=final_state["iterations"],
        processing_time_ms=processing_time,
    )



@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """
    Main chat endpoint with agent routing, execution, and persistence.
    
    Flow:
    1. Get or create user and conversation
    2. Load conversation history if existing conversation
    3. Create initial state
    4. Add user message
    5. Route to appropriate agent
    6. Execute agent
    7. Save messages to database
    8. Return response
    """
    start_time = time.time()
    
    # Get or create user
    user = ConversationService.get_or_create_user(db, username=request.user_id)
    
    # Get or create conversation
    if request.conversation_id:
        conversation = ConversationService.get_conversation(db, request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if conversation.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
    else:
        # Create new conversation
        conversation = ConversationService.create_conversation(
            db, 
            user_id=user.id,
            title=request.message[:50] + ("..." if len(request.message) > 50 else "")
        )
    
    # Load conversation history if continuing conversation
    history_messages = []
    if request.conversation_id:
        db_messages = ConversationService.get_conversation_messages(db, conversation.id)
        history_messages = ConversationService.messages_to_state_format(db_messages)
    
    # Create initial state directly
    now = datetime.now()
    state: AgentState = {
        "messages": history_messages + [Message(role="user", content=request.message, timestamp=now.isoformat())],
        "current_agent": "router",
        "next_agent": None,
        "routing_history": [],
        "routing_confidence": 0.0,
        "retrieved_docs": [],
        "rag_query": None,
        "user_id": request.user_id,
        "session_id": request.session_id or f"session_{time.time()}",
        "user_query": request.message,
        "iterations": 0,
        "max_iterations": request.max_iterations,
        "should_continue": True,
        "metadata": {},
        "created_at": now,
        "updated_at": now,
    }
    
    # Save user message to database
    ConversationService.add_message(
        db,
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    
    # Use LLM-based router (Phase 4)
    target_agent, confidence, reasoning = router_agent_with_fallback(request.message)
    
    # Add routing decision
    routing_decision = RoutingDecision(
        target_agent=target_agent,
        confidence=confidence,
        reasoning=reasoning,
        timestamp=datetime.now().isoformat()
    )
    state["routing_history"].append(routing_decision)
    state["next_agent"] = target_agent
    state["routing_confidence"] = confidence
    state["iterations"] += 1
    
    # Execute the selected agent
    try:
        agent_func = AGENT_REGISTRY.get(target_agent, general_agent)
        state = agent_func(state)
    except Exception as e:
        # Fallback to general agent on error
        print(f"Error with {target_agent} agent: {e}")
        import traceback
        traceback.print_exc()
        state = general_agent(state)
        target_agent = "general"
    
    # Get the agent's response (last message)
    agent_response = state["messages"][-1].content
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Save assistant message to database
    ConversationService.add_message(
        db,
        conversation_id=conversation.id,
        role="assistant",
        content=agent_response,
        agent=target_agent,
        confidence=confidence,
        processing_time_ms=processing_time
    )
    
    # Build response
    return ChatResponse(
        response=agent_response,
        agent_used=target_agent,
        confidence=confidence,
        session_id=state["session_id"],
        conversation_id=conversation.id,
        routing_history=[
            AgentExecution(
                agent_name=rd.target_agent,
                confidence=rd.confidence,
                reasoning=rd.reasoning,
                timestamp=rd.timestamp,
            )
            for rd in state["routing_history"]
        ],
        iterations=state["iterations"],
        processing_time_ms=processing_time,
    )


def route_to_agent(message: str) -> tuple[str, float, str]:
    """
    Simple keyword-based routing logic.
    
    Phase 4 will replace this with an LLM-based router agent.
    
    Args:
        message: User message to route
        
    Returns:
        Tuple of (agent_name, confidence, reasoning)
    """
    message_lower = message.lower()
    
    # Professional keywords
    professional_keywords = [
        "code", "programming", "python", "javascript", "typescript", "java",
        "software", "development", "debug", "error", "function", "api",
        "algorithm", "data structure", "architecture", "design pattern",
        "technical", "engineer", "build", "deploy", "test", "framework",
    ]
    
    # Communication keywords
    communication_keywords = [
        "write", "email", "message", "draft", "tone", "style",
        "communicate", "letter", "response", "reply", "phrase",
    ]
    
    # Knowledge keywords
    knowledge_keywords = [
        "tell me about", "what do i", "my preference", "my favorite",
        "remember", "recall", "personal", "background", "experience",
        "who am i", "what is my", "do i like", "prefer",
    ]
    
    # Decision keywords
    decision_keywords = [
        "should i", "decide", "choice", "option", "pros and cons",
        "recommend", "advice", "what would i", "help me choose",
        "trade-off", "consider", "evaluate",
    ]
    
    # Check for keyword matches
    professional_score = sum(1 for kw in professional_keywords if kw in message_lower)
    communication_score = sum(1 for kw in communication_keywords if kw in message_lower)
    knowledge_score = sum(1 for kw in knowledge_keywords if kw in message_lower)
    decision_score = sum(1 for kw in decision_keywords if kw in message_lower)
    
    scores = {
        "professional": professional_score,
        "communication": communication_score,
        "knowledge": knowledge_score,
        "decision": decision_score,
    }
    
    max_score = max(scores.values())
    
    # If no clear match, use general agent
    if max_score == 0:
        return "general", 0.6, "No specific keywords matched; using general agent"
    
    # Get agent with highest score
    best_agent = max(scores, key=scores.get)
    confidence = min(0.95, 0.65 + (max_score * 0.1))  # Scale confidence
    
    reasoning = f"Matched {max_score} keyword(s) for {best_agent} domain"
    
    return best_agent, confidence, reasoning


@router.get("/state/example", response_model=StateExampleResponse)
async def get_state_example():
    """
    Get an example of the internal state structure.
    """
    # Create example state
    now = datetime.now()
    state: AgentState = {
        "messages": [
            Message(role="user", content="Example query", timestamp=now.isoformat()),
            Message(role="assistant", content="Example response", agent="professional", timestamp=now.isoformat())
        ],
        "current_agent": "router",
        "next_agent": None,
        "routing_history": [
            RoutingDecision(target_agent="professional", confidence=0.9, reasoning="Example routing", timestamp=now.isoformat())
        ],
        "routing_confidence": 0.9,
        "retrieved_docs": [],
        "rag_query": None,
        "user_id": "example_user",
        "session_id": "example_session",
        "user_query": "Example query",
        "iterations": 1,
        "max_iterations": 10,
        "should_continue": True,
        "metadata": {},
        "created_at": now,
        "updated_at": now,
    }
    
    return StateExampleResponse(
        state_structure=state,
        note="This shows the internal state structure with Phase 3 agents active!",
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    user_id: str = "default_user",
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> ConversationListResponse:
    """
    List all conversations for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of conversations to return
        offset: Offset for pagination
        db: Database session
        
    Returns:
        List of conversations
    """
    # Get or create user
    user = ConversationService.get_or_create_user(db, username=user_id)
    
    # Get conversations
    conversations = ConversationService.list_conversations(db, user.id, limit, offset)
    
    # Convert to response format
    conversation_responses = [
        ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages)
        )
        for conv in conversations
    ]
    
    return ConversationListResponse(
        conversations=conversation_responses,
        total=len(conversation_responses)
    )


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    conversation_id: str,
    user_id: str = "default_user",
    limit: int = None,
    db: Session = Depends(get_db)
) -> ConversationMessagesResponse:
    """
    Get all messages for a conversation.
    
    Args:
        conversation_id: Conversation ID
        user_id: User identifier (for authorization)
        limit: Optional limit on number of messages
        db: Database session
        
    Returns:
        List of messages
    """
    # Get user
    user = ConversationService.get_or_create_user(db, username=user_id)
    
    # Get conversation
    conversation = ConversationService.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied to this conversation")
    
    # Get messages
    messages = ConversationService.get_conversation_messages(db, conversation_id, limit)
    
    # Convert to response format
    message_responses = [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            agent=msg.agent,
            confidence=msg.confidence,
            processing_time_ms=msg.processing_time_ms,
            timestamp=msg.timestamp
        )
        for msg in messages
    ]
    
    return ConversationMessagesResponse(
        conversation_id=conversation_id,
        messages=message_responses,
        total=len(message_responses)
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: Conversation ID
        user_id: User identifier (for authorization)
        db: Database session
        
    Returns:
        Success message
    """
    # Get user
    user = ConversationService.get_or_create_user(db, username=user_id)
    
    # Get conversation
    conversation = ConversationService.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied to this conversation")
    
    # Delete conversation
    success = ConversationService.delete_conversation(db, conversation_id)
    
    if success:
        return {"message": "Conversation deleted successfully", "conversation_id": conversation_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete conversation")
