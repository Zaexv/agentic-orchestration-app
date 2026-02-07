# API Testing Guide

## Available Endpoints

### 1. Root Endpoint
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Digital Twin AI API",
  "version": "0.1.0",
  "docs": "/docs",
  "endpoints": {
    "chat": "/api/chat",
    "state_example": "/api/state/example",
    "health": "/health"
  }
}
```

---

### 2. Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model": "gpt-4o-mini",
  "vector_store": "chromadb",
  "api_base": "https://aikeys.maibornwolff.de/"
}
```

---

### 3. Chat Endpoint (State Management Demo)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my technical skills?",
    "user_id": "eduardo",
    "max_iterations": 10
  }'
```

**Response:**
```json
{
  "response": "Hello! I received your message: 'What are my technical skills?'. Full agent responses will be available in Phase 3. Currently demonstrating state management.",
  "agent_used": "general",
  "confidence": 0.75,
  "session_id": "session_1770485301.049928",
  "routing_history": [
    {
      "agent_name": "general",
      "confidence": 0.75,
      "reasoning": "Demo: Using general agent for now (specialized agents coming in Phase 3)",
      "timestamp": "2026-02-07T18:28:21.050000"
    }
  ],
  "iterations": 1,
  "processing_time_ms": 0.097,
  "sources_used": null
}
```

**What This Shows:**
- ✅ State creation (`session_id` generated)
- ✅ Message tracking (user message stored)
- ✅ Routing decision (recorded in `routing_history`)
- ✅ Iteration counting (`iterations: 1`)
- ✅ Agent execution (`agent_used: "general"`)
- ✅ Response generation with metadata

---

### 4. State Structure Example
```bash
curl http://localhost:8000/api/state/example
```

**Response:**
```json
{
  "state_structure": {
    "messages": [
      {
        "role": "user",
        "content": "Example query",
        "agent": null,
        "timestamp": "2026-02-07T18:28:27.403217"
      },
      {
        "role": "assistant",
        "content": "Example response",
        "agent": "professional",
        "timestamp": "2026-02-07T18:28:27.403288"
      }
    ],
    "current_agent": "router",
    "routing_history": [
      {
        "target_agent": "professional",
        "confidence": 0.9,
        "reasoning": "Example routing",
        "timestamp": "2026-02-07T18:28:27.403283"
      }
    ],
    "iterations": 1,
    "max_iterations": 10,
    "should_continue": true,
    "session_id": "example_session",
    "user_id": "example_user"
  },
  "note": "This shows the internal state structure. Full agents coming in Phase 3!"
}
```

**What This Shows:**
- Complete state structure
- Message accumulation (ADD pattern)
- Routing history (ADD pattern)
- Current values (REPLACE pattern)
- Safety mechanisms (iterations, max_iterations)

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

---

## Testing with Python

```python
import requests

# Test chat endpoint
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "What programming languages do I know?",
        "user_id": "eduardo"
    }
)

print(response.json())

# Check routing history
data = response.json()
print(f"Agent used: {data['agent_used']}")
print(f"Confidence: {data['confidence']}")
print(f"Iterations: {data['iterations']}")
print(f"Processing time: {data['processing_time_ms']}ms")
```

---

## State Management in Action

The `/api/chat` endpoint demonstrates:

1. **State Creation**
   ```python
   state = create_initial_state(user_query, user_id)
   ```

2. **Routing Decision**
   ```python
   state = update_routing(state, "general", 0.75, "reasoning")
   ```

3. **Message Addition**
   ```python
   state = add_message(state, "assistant", response, "general")
   ```

4. **Iteration Tracking**
   ```python
   state = increment_iteration(state)
   ```

All these operations follow the patterns from `docs/STATE_MANAGEMENT_GUIDE.md`.

---

## What's Next?

In **Phase 3**, these endpoints will be enhanced with:
- Real specialized agents (Professional, Communication, Knowledge, Decision)
- Actual routing logic based on query classification
- RAG retrieval for personalized responses
- Full conversation history management

Current implementation is a **working demo** of state management patterns that will be used by all agents.
