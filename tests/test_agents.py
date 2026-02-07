"""
Unit tests for all specialized agents.

Tests each agent's ability to process messages and update state correctly.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.orchestration.state import AgentState, Message
from app.agents.general import general_agent
from app.agents.professional import professional_agent
from app.agents.communication import communication_agent
from app.agents.knowledge import knowledge_agent
from app.agents.decision import decision_agent


@pytest.fixture
def base_state() -> AgentState:
    """Create a base state for testing."""
    now = datetime.now()
    return {
        "messages": [
            Message(role="user", content="Test query", timestamp=now.isoformat())
        ],
        "current_agent": "router",
        "next_agent": None,
        "routing_history": [],
        "routing_confidence": 0.0,
        "retrieved_docs": [],
        "rag_query": None,
        "user_id": "test_user",
        "session_id": "test_session",
        "user_query": "Test query",
        "iterations": 1,
        "max_iterations": 10,
        "should_continue": True,
        "metadata": {},
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    mock_response = Mock()
    mock_response.content = "This is a test response from the agent."
    return mock_response


class TestGeneralAgent:
    """Tests for the General Agent."""
    
    def test_general_agent_adds_message(self, base_state, mock_llm_response):
        """Test that general agent adds a message to state."""
        with patch('app.agents.general.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            result = general_agent(base_state)
            
            assert len(result["messages"]) == 2
            assert result["messages"][-1].role == "assistant"
            assert result["messages"][-1].agent == "general"
            assert result["current_agent"] == "general"
    
    def test_general_agent_with_empty_messages(self):
        """Test general agent handles empty message list."""
        empty_state = {
            "messages": [],
            "current_agent": "router",
            "next_agent": None,
            "routing_history": [],
            "routing_confidence": 0.0,
            "retrieved_docs": [],
            "rag_query": None,
            "user_id": "test_user",
            "session_id": "test_session",
            "user_query": "",
            "iterations": 0,
            "max_iterations": 10,
            "should_continue": True,
            "metadata": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        result = general_agent(empty_state)
        assert result == empty_state  # Should return unchanged
    
    def test_general_agent_uses_correct_temperature(self, base_state, mock_llm_response):
        """Test that general agent uses temperature 0.7."""
        with patch('app.agents.general.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            general_agent(base_state)
            
            mock_get_llm.assert_called_once_with(temperature=0.7)
    
    def test_general_agent_uses_system_prompt(self, base_state, mock_llm_response):
        """Test that general agent includes system prompt."""
        with patch('app.agents.general.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            general_agent(base_state)
            
            call_args = mock_llm.invoke.call_args[0][0]
            assert call_args[0]["role"] == "system"
            assert len(call_args[0]["content"]) > 0


class TestProfessionalAgent:
    """Tests for the Professional Agent."""
    
    def test_professional_agent_adds_message(self, base_state, mock_llm_response):
        """Test that professional agent adds a message to state."""
        with patch('app.agents.professional.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            result = professional_agent(base_state)
            
            assert len(result["messages"]) == 2
            assert result["messages"][-1].role == "assistant"
            assert result["messages"][-1].agent == "professional"
            assert result["current_agent"] == "professional"
    
    def test_professional_agent_uses_correct_temperature(self, base_state, mock_llm_response):
        """Test that professional agent uses temperature 0.3."""
        with patch('app.agents.professional.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            professional_agent(base_state)
            
            mock_get_llm.assert_called_once_with(temperature=0.3)


class TestCommunicationAgent:
    """Tests for the Communication Agent."""
    
    def test_communication_agent_adds_message(self, base_state, mock_llm_response):
        """Test that communication agent adds a message to state."""
        with patch('app.agents.communication.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            result = communication_agent(base_state)
            
            assert len(result["messages"]) == 2
            assert result["messages"][-1].role == "assistant"
            assert result["messages"][-1].agent == "communication"
            assert result["current_agent"] == "communication"
    
    def test_communication_agent_uses_correct_temperature(self, base_state, mock_llm_response):
        """Test that communication agent uses temperature 0.5."""
        with patch('app.agents.communication.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            communication_agent(base_state)
            
            mock_get_llm.assert_called_once_with(temperature=0.5)


class TestKnowledgeAgent:
    """Tests for the Knowledge Agent."""
    
    def test_knowledge_agent_adds_message(self, base_state, mock_llm_response):
        """Test that knowledge agent adds a message to state."""
        with patch('app.agents.knowledge.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            result = knowledge_agent(base_state)
            
            assert len(result["messages"]) == 2
            assert result["messages"][-1].role == "assistant"
            assert result["messages"][-1].agent == "knowledge"
            assert result["current_agent"] == "knowledge"
    
    def test_knowledge_agent_uses_correct_temperature(self, base_state, mock_llm_response):
        """Test that knowledge agent uses temperature 0.4."""
        with patch('app.agents.knowledge.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            knowledge_agent(base_state)
            
            mock_get_llm.assert_called_once_with(temperature=0.4)


class TestDecisionAgent:
    """Tests for the Decision Agent."""
    
    def test_decision_agent_adds_message(self, base_state, mock_llm_response):
        """Test that decision agent adds a message to state."""
        with patch('app.agents.decision.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            result = decision_agent(base_state)
            
            assert len(result["messages"]) == 2
            assert result["messages"][-1].role == "assistant"
            assert result["messages"][-1].agent == "decision"
            assert result["current_agent"] == "decision"
    
    def test_decision_agent_uses_correct_temperature(self, base_state, mock_llm_response):
        """Test that decision agent uses temperature 0.4."""
        with patch('app.agents.decision.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_get_llm.return_value = mock_llm
            
            decision_agent(base_state)
            
            mock_get_llm.assert_called_once_with(temperature=0.4)


class TestAllAgentsErrorHandling:
    """Test error handling across all agents."""
    
    @pytest.mark.parametrize("agent_func,agent_name", [
        (general_agent, "general"),
        (professional_agent, "professional"),
        (communication_agent, "communication"),
        (knowledge_agent, "knowledge"),
        (decision_agent, "decision"),
    ])
    def test_agent_handles_string_response(self, base_state, agent_func, agent_name):
        """Test agents can handle string responses from LLM."""
        with patch(f'app.agents.{agent_name}.get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_llm.invoke.return_value = "Plain string response"
            mock_get_llm.return_value = mock_llm
            
            result = agent_func(base_state)
            
            assert len(result["messages"]) == 2
            assert result["messages"][-1].content == "Plain string response"
