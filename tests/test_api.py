"""
Unit tests for API endpoints.

Tests the FastAPI routes and request/response models.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.orchestration.state import Message


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""
    
    def test_health_endpoint_returns_200(self):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")
        
        assert response.status_code == 200
    
    def test_health_endpoint_response_format(self):
        """Test health endpoint response format."""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "model" in data
        assert "vector_store" in data
        assert "api_base" in data


class TestRootEndpoint:
    """Tests for the / endpoint."""
    
    def test_root_endpoint_returns_200(self):
        """Test that root endpoint returns 200 OK."""
        response = client.get("/")
        
        assert response.status_code == 200
    
    def test_root_endpoint_response_format(self):
        """Test root endpoint response format."""
        response = client.get("/")
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "endpoints" in data


class TestStateExampleEndpoint:
    """Tests for the /api/state/example endpoint."""
    
    def test_state_example_returns_200(self):
        """Test that state example endpoint returns 200 OK."""
        response = client.get("/api/state/example")
        
        assert response.status_code == 200
    
    def test_state_example_response_structure(self):
        """Test state example response has correct structure."""
        response = client.get("/api/state/example")
        data = response.json()
        
        assert "state_structure" in data
        assert "note" in data
        # Check nested state structure
        state = data["state_structure"]
        assert "messages" in state
        assert "current_agent" in state
        assert "routing_history" in state
    
    def test_state_example_has_messages(self):
        """Test state example includes message objects."""
        response = client.get("/api/state/example")
        data = response.json()
        
        state = data["state_structure"]
        assert len(state["messages"]) > 0
        message = state["messages"][0]
        assert "role" in message
        assert "content" in message
        assert "timestamp" in message


class TestChatEndpoint:
    """Tests for the /api/chat endpoint."""
    
    def test_chat_endpoint_requires_post(self):
        """Test that chat endpoint only accepts POST."""
        response = client.get("/api/chat")
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_chat_endpoint_requires_message(self):
        """Test that chat endpoint requires message field."""
        response = client.post("/api/chat", json={})
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_chat_endpoint_user_id_optional(self):
        """Test that chat endpoint works without user_id (it's optional)."""
        response = client.post("/api/chat", json={"message": "Hello"})
        
        # Should succeed since user_id is optional
        assert response.status_code == 200
    
    def test_chat_endpoint_validates_empty_message(self):
        """Test that chat endpoint rejects empty messages."""
        response = client.post("/api/chat", json={
            "message": "",
            "user_id": "test_user"
        })
        
        assert response.status_code == 422
    
    @patch('app.api.routes.general_agent')
    def test_chat_endpoint_success_response(self, mock_agent):
        """Test successful chat endpoint response."""
        # Mock the agent to return a state with a response
        now = datetime.now()
        mock_state = {
            "messages": [
                Message(role="user", content="Hello", timestamp=now.isoformat()),
                Message(role="assistant", content="Hi there!", agent="general", timestamp=now.isoformat())
            ],
            "current_agent": "general",
            "next_agent": None,
            "routing_history": [],
            "routing_confidence": 0.6,
            "retrieved_docs": [],
            "rag_query": None,
            "user_id": "test_user",
            "session_id": "test_session",
            "user_query": "Hello",
            "iterations": 1,
            "max_iterations": 10,
            "should_continue": True,
            "metadata": {},
            "created_at": now,
            "updated_at": now,
        }
        mock_agent.return_value = mock_state
        
        response = client.post("/api/chat", json={
            "message": "Hello",
            "user_id": "test_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert "agent_used" in data
        assert "confidence" in data
        assert "session_id" in data
        assert "routing_history" in data
        assert "iterations" in data
        assert "processing_time_ms" in data
    
    def test_chat_endpoint_response_content(self):
        """Test chat endpoint returns required response fields."""
        response = client.post("/api/chat", json={
            "message": "Hello",
            "user_id": "test_user"
        })
        
        data = response.json()
        assert "response" in data
        assert "agent_used" in data
        assert data["agent_used"] == "general"  # Hello routes to general
        assert len(data["response"]) > 0
    
    def test_chat_endpoint_routes_to_professional(self):
        """Test chat endpoint routes technical queries to professional agent."""
        response = client.post("/api/chat", json={
            "message": "Help with Python code",
            "user_id": "test_user"
        })
        
        data = response.json()
        assert response.status_code == 200
        assert data["agent_used"] == "professional"
        assert data["confidence"] >= 0.65


class TestChatEndpointRouting:
    """Tests for routing behavior in chat endpoint."""
    
    @patch('app.api.routes.router_agent_with_fallback')
    @patch('app.api.routes.general_agent')
    def test_routing_function_called(self, mock_agent, mock_route):
        """Test that router_agent_with_fallback is called."""
        mock_route.return_value = ("general", 0.6, "No keywords")
        
        now = datetime.now()
        mock_state = {
            "messages": [
                Message(role="user", content="Hello", timestamp=now.isoformat()),
                Message(role="assistant", content="Hi", agent="general", timestamp=now.isoformat())
            ],
            "current_agent": "general",
            "next_agent": None,
            "routing_history": [],
            "routing_confidence": 0.6,
            "retrieved_docs": [],
            "rag_query": None,
            "user_id": "test_user",
            "session_id": "test_session",
            "user_query": "Hello",
            "iterations": 1,
            "max_iterations": 10,
            "should_continue": True,
            "metadata": {},
            "created_at": now,
            "updated_at": now,
        }
        mock_agent.return_value = mock_state
        
        client.post("/api/chat", json={
            "message": "Hello",
            "user_id": "test_user"
        })
        
        mock_route.assert_called_once_with("Hello")
    
    def test_routing_to_different_agents(self):
        """Test that different queries route to appropriate agents."""
        test_cases = [
            ("Help with Python code", "professional"),
            ("Write an email", "communication"),
            ("Hello!", "general"),
        ]
        
        for query, expected_agent in test_cases:
            response = client.post("/api/chat", json={
                "message": query,
                "user_id": "test_user"
            })
            
            data = response.json()
            assert data["agent_used"] == expected_agent, f"Query '{query}' should route to {expected_agent}"


class TestChatEndpointErrors:
    """Tests for error handling in chat endpoint."""
    
    def test_chat_invalid_json(self):
        """Test chat endpoint handles invalid JSON."""
        response = client.post("/api/chat", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_chat_missing_content_type(self):
        """Test chat endpoint requires JSON content type."""
        response = client.post("/api/chat", data="message=hello")
        
        assert response.status_code == 422
