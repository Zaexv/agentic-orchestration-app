"""
Unit tests for the LLM-based router agent.

Tests the new Phase 4 router implementation.
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.router import (
    router_agent,
    router_agent_with_fallback,
    _keyword_fallback,
)


class TestRouterAgent:
    """Tests for LLM-based router_agent function."""
    
    @patch('app.agents.router.get_llm')
    def test_router_agent_professional_query(self, mock_get_llm):
        """Test router correctly identifies professional query."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"agent": "professional", "confidence": 0.95, "reasoning": "Technical question"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        agent, confidence, reasoning = router_agent("How do I implement OAuth in Python?")
        
        assert agent == "professional"
        assert confidence == 0.95
        assert "Technical" in reasoning or "technical" in reasoning
    
    @patch('app.agents.router.get_llm')
    def test_router_agent_communication_query(self, mock_get_llm):
        """Test router correctly identifies communication query."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"agent": "communication", "confidence": 0.90, "reasoning": "Writing assistance"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        agent, confidence, reasoning = router_agent("Help me draft an email")
        
        assert agent == "communication"
        assert confidence == 0.90
    
    @patch('app.agents.router.get_llm')
    def test_router_agent_knowledge_query(self, mock_get_llm):
        """Test router correctly identifies knowledge query."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"agent": "knowledge", "confidence": 0.88, "reasoning": "Personal preferences"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        agent, confidence, reasoning = router_agent("What are my favorite hobbies?")
        
        assert agent == "knowledge"
        assert confidence == 0.88
    
    @patch('app.agents.router.get_llm')
    def test_router_agent_decision_query(self, mock_get_llm):
        """Test router correctly identifies decision query."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"agent": "decision", "confidence": 0.92, "reasoning": "Decision making"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        agent, confidence, reasoning = router_agent("Should I learn Rust or Go?")
        
        assert agent == "decision"
        assert confidence == 0.92
    
    @patch('app.agents.router.get_llm')
    def test_router_agent_general_query(self, mock_get_llm):
        """Test router correctly identifies general query."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"agent": "general", "confidence": 0.85, "reasoning": "Casual greeting"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        agent, confidence, reasoning = router_agent("Hello! How are you?")
        
        assert agent == "general"
        assert confidence == 0.85
    
    @patch('app.agents.router.get_llm')
    def test_router_agent_invalid_agent_name(self, mock_get_llm):
        """Test router handles invalid agent names."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"agent": "invalid_agent", "confidence": 0.95, "reasoning": "Test"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        agent, confidence, reasoning = router_agent("Test query")
        
        assert agent == "general"  # Should fallback to general
        assert confidence == 0.6
    
    @patch('app.agents.router.get_llm')
    def test_router_agent_json_parse_error(self, mock_get_llm):
        """Test router handles JSON parsing errors."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = 'Not valid JSON'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        agent, confidence, reasoning = router_agent("Test query")
        
        assert agent == "general"
        assert confidence == 0.6
        assert "Could not parse" in reasoning or "general" in reasoning
    
    @patch('app.agents.router.get_llm')
    def test_router_agent_confidence_bounds(self, mock_get_llm):
        """Test router clips confidence to valid range [0, 1]."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"agent": "professional", "confidence": 1.5, "reasoning": "Test"}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        agent, confidence, reasoning = router_agent("Test query")
        
        assert 0.0 <= confidence <= 1.0
        assert confidence == 1.0  # Should be clipped to max


class TestKeywordFallback:
    """Tests for keyword fallback routing."""
    
    def test_keyword_fallback_professional(self):
        """Test keyword fallback identifies professional query."""
        agent, confidence, reasoning = _keyword_fallback("Help me debug my Python code")
        
        assert agent == "professional"
        assert confidence > 0.6
        assert "Fallback" in reasoning
    
    def test_keyword_fallback_communication(self):
        """Test keyword fallback identifies communication query."""
        agent, confidence, reasoning = _keyword_fallback("Write an email for me")
        
        assert agent == "communication"
        assert confidence > 0.6
    
    def test_keyword_fallback_knowledge(self):
        """Test keyword fallback identifies knowledge query."""
        agent, confidence, reasoning = _keyword_fallback("What do I prefer for breakfast?")
        
        assert agent == "knowledge"
        assert confidence > 0.6
    
    def test_keyword_fallback_decision(self):
        """Test keyword fallback identifies decision query."""
        agent, confidence, reasoning = _keyword_fallback("Should I choose option A or B?")
        
        assert agent == "decision"
        assert confidence > 0.6
    
    def test_keyword_fallback_general(self):
        """Test keyword fallback uses general for no matches."""
        agent, confidence, reasoning = _keyword_fallback("Hello there!")
        
        assert agent == "general"
        assert confidence == 0.6
        assert "No keywords" in reasoning


class TestRouterWithFallback:
    """Tests for router_agent_with_fallback function."""
    
    @patch('app.agents.router.router_agent')
    def test_uses_llm_router_on_success(self, mock_router):
        """Test that LLM router is tried first."""
        mock_router.return_value = ("professional", 0.95, "LLM decision")
        
        agent, confidence, reasoning = router_agent_with_fallback("Test query")
        
        assert agent == "professional"
        assert confidence == 0.95
        assert "LLM" in reasoning
    
    @patch('app.agents.router.router_agent')
    def test_uses_keyword_fallback_on_low_confidence(self, mock_router):
        """Test that keyword fallback is used when confidence is too low."""
        mock_router.return_value = ("general", 0.3, "Low confidence")
        
        agent, confidence, reasoning = router_agent_with_fallback("Help me code")
        
        # Should use keyword fallback and likely route to professional
        assert "Fallback" in reasoning
    
    @patch('app.agents.router.router_agent')
    def test_handles_router_exception(self, mock_router):
        """Test that exceptions in LLM router trigger keyword fallback."""
        mock_router.side_effect = Exception("LLM error")
        
        agent, confidence, reasoning = router_agent_with_fallback("Test query")
        
        assert agent in ["professional", "communication", "knowledge", "decision", "general"]
        assert "Fallback" in reasoning


class TestRouterIntegration:
    """Integration tests for router with real LLM (if available)."""
    
    @pytest.mark.skip(reason="Integration test - requires OpenAI API key")
    def test_router_real_llm_professional(self):
        """Test router with real LLM on professional query."""
        agent, confidence, reasoning = router_agent("How do I implement a REST API in FastAPI?")
        
        assert agent == "professional"
        assert confidence > 0.7
    
    @pytest.mark.skip(reason="Integration test - requires OpenAI API key")
    def test_router_real_llm_communication(self):
        """Test router with real LLM on communication query."""
        agent, confidence, reasoning = router_agent("Help me write a thank you note")
        
        assert agent == "communication"
        assert confidence > 0.7
    
    @pytest.mark.skip(reason="Integration test - requires OpenAI API key")
    def test_router_real_llm_general(self):
        """Test router with real LLM on general query."""
        agent, confidence, reasoning = router_agent("Hi! How's your day going?")
        
        assert agent == "general"
        assert confidence > 0.6
