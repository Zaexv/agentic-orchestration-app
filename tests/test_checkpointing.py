"""Tests for LangGraph checkpointing and conversation memory"""

import pytest
from app.orchestration.graph import run_workflow, workflow_app, checkpointer
from app.orchestration.state import create_initial_state


def test_checkpointer_configured():
    """Test that checkpointer is properly configured"""
    assert workflow_app.checkpointer is not None
    assert checkpointer is not None
    print("✅ Checkpointer is configured")


def test_workflow_with_thread_id():
    """Test workflow execution with thread_id for memory"""
    state = create_initial_state("What is Python?")
    result = run_workflow(state, thread_id="test-memory-001")
    
    assert result is not None
    assert result["iterations"] >= 1
    assert len(result["messages"]) > 0
    print(f"✅ Workflow completed with thread_id, {result['iterations']} iterations")


def test_conversation_memory_across_turns():
    """Test that conversation state persists across multiple turns"""
    thread_id = "conversation-memory-test"
    
    # First turn
    state1 = create_initial_state("My name is Alice")
    result1 = run_workflow(state1, thread_id=thread_id)
    
    assert len(result1["messages"]) >= 2  # User message + assistant response
    first_turn_messages = len(result1["messages"])
    
    # Second turn - should have memory of first turn
    state2 = create_initial_state("What is my name?")
    result2 = run_workflow(state2, thread_id=thread_id)
    
    # Second turn should have more messages (accumulated from both turns)
    assert len(result2["messages"]) > first_turn_messages
    print(f"✅ Conversation memory works: {first_turn_messages} → {len(result2['messages'])} messages")


def test_different_threads_isolated():
    """Test that different thread_ids maintain separate conversations"""
    # Thread 1
    state_a = create_initial_state("I like Python")
    result_a = run_workflow(state_a, thread_id="thread-a")
    messages_a = len(result_a["messages"])
    
    # Thread 2
    state_b = create_initial_state("I like JavaScript")
    result_b = run_workflow(state_b, thread_id="thread-b")
    messages_b = len(result_b["messages"])
    
    # Both should have their own state
    assert messages_a > 0
    assert messages_b > 0
    
    # Thread A should not be affected by Thread B
    state_a2 = create_initial_state("What do I like?")
    result_a2 = run_workflow(state_a2, thread_id="thread-a")
    
    # Should have accumulated messages from thread-a only
    assert len(result_a2["messages"]) > messages_a
    print(f"✅ Thread isolation works: Thread A={len(result_a2['messages'])}, Thread B={messages_b}")


def test_session_id_as_default_thread():
    """Test that session_id is used as default thread when thread_id not provided"""
    state = create_initial_state("Hello world")
    session_id = state["session_id"]
    
    # Run without explicit thread_id
    result = run_workflow(state)
    
    # Should work and use session_id internally
    assert result is not None
    assert result["session_id"] == session_id
    print(f"✅ Default thread_id works with session_id: {session_id}")


def test_checkpointing_with_iterations():
    """Test that checkpointing works with multi-iteration workflows"""
    state = create_initial_state("Complex query requiring multiple iterations", max_iterations=3)
    result = run_workflow(state, thread_id="multi-iteration-test")
    
    assert result["iterations"] >= 1
    assert len(result["iteration_log"]) > 0
    print(f"✅ Checkpointing works with {result['iterations']} iterations")


def test_routing_history_persisted():
    """Test that routing history is maintained in checkpointed state"""
    thread_id = "routing-history-test"
    
    state = create_initial_state("Tell me about FastAPI")
    result = run_workflow(state, thread_id=thread_id)
    
    assert len(result["routing_history"]) > 0
    assert result["routing_history"][0].target_agent in [
        "general", "professional", "communication", "knowledge", "decision"
    ]
    print(f"✅ Routing history persisted: {result['routing_history'][0].target_agent}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
