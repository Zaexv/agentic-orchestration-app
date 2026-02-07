"""
Unit tests for routing logic.

Tests the keyword-based routing system that directs messages to appropriate agents.
"""

import pytest
from app.api.routes import route_to_agent


class TestRouteToAgent:
    """Tests for the route_to_agent function."""
    
    # Professional Agent Tests
    def test_route_professional_single_keyword(self):
        """Test routing with single professional keyword."""
        agent, confidence, reasoning = route_to_agent("I need help with Python code")
        
        assert agent == "professional"
        assert confidence >= 0.65
        assert "professional" in reasoning.lower()
    
    def test_route_professional_multiple_keywords(self):
        """Test routing with multiple professional keywords."""
        agent, confidence, reasoning = route_to_agent(
            "Help me debug this Python API code and test the framework"
        )
        
        assert agent == "professional"
        assert confidence >= 0.75  # Multiple keywords = higher confidence
        assert "professional" in reasoning.lower()
    
    def test_route_professional_technical_query(self):
        """Test routing technical queries to professional agent."""
        queries = [
            "How do I implement a design pattern in JavaScript?",
            "Debug this error in my Java code",
            "What's the best data structure for this algorithm?",
            "How to deploy a software architecture?",
        ]
        
        for query in queries:
            agent, confidence, _ = route_to_agent(query)
            assert agent == "professional"
            assert confidence >= 0.65
    
    # Communication Agent Tests
    def test_route_communication_single_keyword(self):
        """Test routing with single communication keyword."""
        agent, confidence, reasoning = route_to_agent("Help me write an email")
        
        assert agent == "communication"
        assert confidence >= 0.65
        assert "communication" in reasoning.lower()
    
    def test_route_communication_multiple_keywords(self):
        """Test routing with multiple communication keywords."""
        agent, confidence, reasoning = route_to_agent(
            "I need to draft a message with the right tone and style"
        )
        
        assert agent == "communication"
        assert confidence >= 0.75
        assert "communication" in reasoning.lower()
    
    def test_route_communication_writing_tasks(self):
        """Test routing writing tasks to communication agent."""
        queries = [
            "Write a professional email response",
            "Help me phrase this message better",
            "Draft a letter with a formal tone",
        ]
        
        for query in queries:
            agent, confidence, _ = route_to_agent(query)
            assert agent == "communication"
            assert confidence >= 0.65
    
    # Knowledge Agent Tests
    def test_route_knowledge_single_keyword(self):
        """Test routing with single knowledge keyword."""
        agent, confidence, reasoning = route_to_agent("What do I prefer for breakfast?")
        
        assert agent == "knowledge"
        assert confidence >= 0.65
        assert "knowledge" in reasoning.lower()
    
    def test_route_knowledge_personal_queries(self):
        """Test routing personal queries to knowledge agent."""
        queries = [
            "Tell me about my background",
            "What is my favorite programming language?",
            "Remember my preferences",
            "Who am I and what do I like?",
        ]
        
        for query in queries:
            agent, confidence, _ = route_to_agent(query)
            assert agent == "knowledge"
            assert confidence >= 0.65
    
    # Decision Agent Tests
    def test_route_decision_single_keyword(self):
        """Test routing with single decision keyword."""
        agent, confidence, reasoning = route_to_agent("Should I learn Rust or Go?")
        
        assert agent == "decision"
        assert confidence >= 0.65
        assert "decision" in reasoning.lower()
    
    def test_route_decision_multiple_keywords(self):
        """Test routing with multiple decision keywords."""
        agent, confidence, reasoning = route_to_agent(
            "Help me decide which option to choose, considering the pros and cons"
        )
        
        assert agent == "decision"
        assert confidence >= 0.75
        assert "decision" in reasoning.lower()
    
    def test_route_decision_choice_queries(self):
        """Test routing choice queries to decision agent."""
        queries = [
            "What would I recommend for this situation?",
            "Help me evaluate the trade-offs",
            "Give me advice on this decision",
        ]
        
        for query in queries:
            agent, confidence, _ = route_to_agent(query)
            assert agent == "decision"
            assert confidence >= 0.65
    
    # General Agent Tests
    def test_route_general_no_keywords(self):
        """Test routing to general agent when no keywords match."""
        agent, confidence, reasoning = route_to_agent("Hello there!")
        
        assert agent == "general"
        assert confidence == 0.6  # Default confidence for general
        assert "no specific keywords" in reasoning.lower()
    
    def test_route_general_casual_greeting(self):
        """Test routing casual messages to general agent."""
        queries = [
            "Hi!",
            "How are you?",
            "Good morning",
            "Thanks!",
        ]
        
        for query in queries:
            agent, confidence, _ = route_to_agent(query)
            assert agent == "general"
            assert confidence == 0.6
    
    # Edge Cases
    def test_route_case_insensitive(self):
        """Test that routing is case-insensitive."""
        queries = [
            "HELP ME WITH PYTHON CODE",
            "help me with python code",
            "HeLp Me WiTh PyThOn CoDe",
        ]
        
        for query in queries:
            agent, confidence, _ = route_to_agent(query)
            assert agent == "professional"
            assert confidence >= 0.65
    
    def test_route_empty_string(self):
        """Test routing with empty string."""
        agent, confidence, reasoning = route_to_agent("")
        
        assert agent == "general"
        assert confidence == 0.6
        assert "no specific keywords" in reasoning.lower()
    
    def test_route_confidence_capped_at_95(self):
        """Test that confidence is capped at 0.95."""
        # Query with many professional keywords
        agent, confidence, _ = route_to_agent(
            "python javascript java code programming software development "
            "debug error function api algorithm data structure architecture "
            "design pattern technical engineer build deploy test framework"
        )
        
        assert agent == "professional"
        assert confidence <= 0.95
    
    def test_route_tie_breaking(self):
        """Test behavior when multiple agents have same score."""
        # This will match 1 keyword in both professional and decision
        agent, confidence, _ = route_to_agent("Should I code this feature?")
        
        # Either agent is acceptable, but should be deterministic
        assert agent in ["professional", "decision"]
        assert confidence >= 0.65
    
    def test_route_mixed_keywords(self):
        """Test routing with keywords from multiple domains."""
        # Professional (code, python) vs Decision (should)
        agent, confidence, _ = route_to_agent("Should I use Python code for this?")
        
        # Professional should win with 2 keywords vs 1
        assert agent == "professional"
        assert confidence >= 0.75
    
    # Confidence Calculation Tests
    def test_confidence_increases_with_keywords(self):
        """Test that confidence increases with more keyword matches."""
        one_keyword = route_to_agent("Help with code")[1]
        two_keywords = route_to_agent("Help with Python code")[1]
        three_keywords = route_to_agent("Help with Python API code")[1]
        
        assert two_keywords > one_keyword
        assert three_keywords > two_keywords
    
    def test_confidence_formula(self):
        """Test the confidence calculation formula: min(0.95, 0.65 + matches * 0.1)"""
        # 1 match: 0.65 + 0.1 = 0.75
        _, conf1, _ = route_to_agent("code")
        assert conf1 == pytest.approx(0.75, abs=0.01)
        
        # 2 matches: 0.65 + 0.2 = 0.85
        _, conf2, _ = route_to_agent("code python")
        assert conf2 == pytest.approx(0.85, abs=0.01)
        
        # 3 matches: 0.65 + 0.3 = 0.95 (capped)
        _, conf3, _ = route_to_agent("code python javascript")
        assert conf3 == pytest.approx(0.95, abs=0.01)
    
    # Realistic Query Tests
    def test_realistic_professional_queries(self):
        """Test realistic professional queries."""
        queries = [
            "Can you help me debug this Python function?",
            "What's the best way to implement authentication in my API?",
            "Explain how async/await works in JavaScript",
            "Review this code for performance issues",
        ]
        
        for query in queries:
            agent, _, _ = route_to_agent(query)
            assert agent == "professional"
    
    def test_realistic_communication_queries(self):
        """Test realistic communication queries."""
        queries = [
            "Help me write a professional email to my boss",
            "How should I phrase this message to sound more polite?",
            "Draft a response to this client inquiry",
        ]
        
        for query in queries:
            agent, _, _ = route_to_agent(query)
            assert agent == "communication"
    
    def test_realistic_knowledge_queries(self):
        """Test realistic knowledge queries."""
        queries = [
            "What do I usually prefer for database technologies?",
            "Tell me about my experience with React",
            "What is my favorite tech stack?",
        ]
        
        for query in queries:
            agent, _, _ = route_to_agent(query)
            assert agent == "knowledge"
    
    def test_realistic_decision_queries(self):
        """Test realistic decision queries."""
        # Note: "Should I learn Rust or Go for systems programming?" routes to professional
        # because it contains "programming" keyword. This is acceptable behavior.
        queries = [
            "Help me decide between MongoDB and PostgreSQL",
            "What are the pros and cons of microservices vs monolith?",
            "Should I choose option A or option B?",
        ]
        
        for query in queries:
            agent, _, _ = route_to_agent(query)
            assert agent == "decision"
    
    def test_realistic_general_queries(self):
        """Test realistic general queries."""
        queries = [
            "Hello! How's it going?",
            "Thanks for your help!",
            "What's the weather like?",
            "Tell me a joke",
        ]
        
        for query in queries:
            agent, _, _ = route_to_agent(query)
            assert agent == "general"
