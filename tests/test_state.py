"""Tests for State Management"""

import pytest
from datetime import datetime
from app.orchestration.state import (
    AgentState,
    Message,
    RoutingDecision,
    RetrievedDocument,
    create_initial_state,
    add_message,
    update_routing,
    increment_iteration
)


def test_create_initial_state():
    """Test creating initial state"""
    query = "What are my technical skills?"
    state = create_initial_state(query, user_id="test_user")
    
    assert state["user_query"] == query
    assert state["user_id"] == "test_user"
    assert state["current_agent"] == "router"
    assert state["iterations"] == 0
    assert state["max_iterations"] == 10
    assert state["should_continue"] is True
    assert len(state["messages"]) == 1
    assert state["messages"][0].role == "user"
    assert state["messages"][0].content == query


def test_add_message():
    """Test adding messages to state"""
    state = create_initial_state("Test query")
    
    # Add assistant message
    state = add_message(state, role="assistant", content="Test response", agent="general")
    
    assert len(state["messages"]) == 2
    assert state["messages"][1].role == "assistant"
    assert state["messages"][1].content == "Test response"
    assert state["messages"][1].agent == "general"


def test_message_accumulation():
    """Test that messages accumulate correctly"""
    state = create_initial_state("Test")
    
    for i in range(3):
        state = add_message(state, role="system", content=f"Message {i}")
    
    # Initial user message + 3 system messages
    assert len(state["messages"]) == 4


def test_update_routing():
    """Test updating routing information"""
    state = create_initial_state("Test query")
    
    state = update_routing(
        state,
        target_agent="professional",
        confidence=0.85,
        reasoning="Query is about technical skills"
    )
    
    assert state["next_agent"] == "professional"
    assert state["routing_confidence"] == 0.85
    assert len(state["routing_history"]) == 1
    assert state["routing_history"][0].target_agent == "professional"


def test_routing_history_accumulation():
    """Test that routing history accumulates"""
    state = create_initial_state("Test query")
    
    agents = ["professional", "communication", "general"]
    for agent in agents:
        state = update_routing(state, target_agent=agent, confidence=0.8)
    
    assert len(state["routing_history"]) == 3
    assert [r.target_agent for r in state["routing_history"]] == agents


def test_increment_iteration():
    """Test iteration increment"""
    state = create_initial_state("Test", max_iterations=3)
    
    assert state["iterations"] == 0
    assert state["should_continue"] is True
    
    # Increment twice
    state = increment_iteration(state)
    assert state["iterations"] == 1
    assert state["should_continue"] is True
    
    state = increment_iteration(state)
    assert state["iterations"] == 2
    assert state["should_continue"] is True


def test_max_iterations_reached():
    """Test max iterations safety limit"""
    state = create_initial_state("Test", max_iterations=2)
    
    state = increment_iteration(state)
    assert state["should_continue"] is True
    
    state = increment_iteration(state)
    assert state["should_continue"] is False
    assert state["error"] is not None
    assert "Max iterations" in state["error"]


def test_message_model():
    """Test Message pydantic model"""
    msg = Message(role="user", content="Hello")
    
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert isinstance(msg.timestamp, datetime)
    assert msg.agent is None


def test_routing_decision_model():
    """Test RoutingDecision pydantic model"""
    decision = RoutingDecision(
        target_agent="professional",
        confidence=0.9,
        reasoning="Technical query"
    )
    
    assert decision.target_agent == "professional"
    assert decision.confidence == 0.9
    assert decision.reasoning == "Technical query"
    assert isinstance(decision.timestamp, datetime)


def test_routing_decision_validation():
    """Test that routing confidence is validated"""
    # Valid confidence
    decision = RoutingDecision(target_agent="test", confidence=0.5)
    assert decision.confidence == 0.5
    
    # Invalid confidence should raise validation error
    with pytest.raises(Exception):  # Pydantic ValidationError
        RoutingDecision(target_agent="test", confidence=1.5)


def test_retrieved_document_model():
    """Test RetrievedDocument pydantic model"""
    doc = RetrievedDocument(
        content="Sample content",
        source="resume.pdf",
        score=0.95,
        agent_domain="professional"
    )
    
    assert doc.content == "Sample content"
    assert doc.source == "resume.pdf"
    assert doc.score == 0.95
    assert doc.agent_domain == "professional"


def test_state_immutability_pattern():
    """Test that state updates return modified state (functional pattern)"""
    state = create_initial_state("Test")
    original_iteration = state["iterations"]
    
    # Update state
    state = increment_iteration(state)
    
    # State should be updated
    assert state["iterations"] == original_iteration + 1


def test_state_timestamp_updates():
    """Test that updated_at changes with state updates"""
    state = create_initial_state("Test")
    original_timestamp = state["updated_at"]
    
    import time
    time.sleep(0.01)  # Small delay
    
    state = add_message(state, role="system", content="Test")
    
    # Timestamp should be updated
    assert state["updated_at"] > original_timestamp
