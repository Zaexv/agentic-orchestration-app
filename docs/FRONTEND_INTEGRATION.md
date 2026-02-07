# 🚀 Frontend Integration Guide - Digital Twin API

## 📋 Overview

This guide provides all the information needed to build a frontend for the AI Digital Twin system.

**Base URL:** `http://localhost:8000`  
**API Version:** `0.1.0`  
**Content-Type:** `application/json`

---

## 🔌 Available Endpoints

### 1. **Health Check**
```http
GET /health
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

### 2. **Root Endpoint**
```http
GET /
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

### 3. **Chat Endpoint (Primary)**
```http
POST /api/chat
```

**Request Body:**
```json
{
  "message": "Your question or message here",
  "user_id": "eduardo",          // Optional
  "max_iterations": 10            // Optional, default: 10
}
```

**Response:**
```json
{
  "response": "The AI's response text",
  "agent_used": "professional",
  "confidence": 0.95,
  "session_id": "session_1770495595.83646",
  "routing_history": [
    {
      "agent_name": "professional",
      "confidence": 0.95,
      "reasoning": "LLM: Technical question about programming",
      "timestamp": "2026-02-07T21:19:57.158220"
    }
  ],
  "iterations": 1,
  "processing_time_ms": 2107.69,
  "sources_used": null
}
```

---

### 4. **Chat with Graph Endpoint (Phase 5)**
```http
POST /api/chat/graph
```

Same request/response format as `/api/chat`, but uses LangGraph workflow internally.

**Request Body:** (Same as `/api/chat`)
```json
{
  "message": "Your question",
  "user_id": "eduardo",
  "max_iterations": 10
}
```

---

### 5. **State Example**
```http
GET /api/state/example
```

Returns an example of the internal state structure (useful for debugging).

---

## 🤖 Available Agents

The system automatically routes to the best agent based on your query. Here are the 5 specialized agents:

### 1. **General Agent** 🌐
- **Purpose:** Fallback for general conversation
- **Temperature:** 0.7 (more creative)
- **Trigger Keywords:** None specific (default)
- **Example Queries:**
  - "Hello, how are you?"
  - "Tell me a joke"
  - "What can you help me with?"

### 2. **Professional Agent** 💼
- **Purpose:** Technical expertise, work-related queries
- **Temperature:** 0.3 (more precise)
- **Trigger Keywords:** `code`, `python`, `javascript`, `api`, `debug`, `implement`, `technical`, `programming`, `software`
- **Example Queries:**
  - "How do I implement OAuth in Python?"
  - "Debug this JavaScript error"
  - "What's the best way to structure a REST API?"
  - "Explain async/await in JavaScript"

### 3. **Communication Agent** ✉️
- **Purpose:** Writing assistance, tone, style
- **Temperature:** 0.5 (balanced)
- **Trigger Keywords:** `write`, `email`, `draft`, `tone`, `letter`, `message`, `communicate`, `respond`, `reply`
- **Example Queries:**
  - "Help me write a professional email"
  - "Draft a response to a client complaint"
  - "How should I phrase this message?"
  - "Write a meeting invitation"

### 4. **Knowledge Agent** 🧠
- **Purpose:** Personal facts, memories, preferences
- **Temperature:** 0.4 (factual)
- **Trigger Keywords:** `my`, `what do i`, `my preference`, `remember`, `personal`, `about me`, `favorite`, `hobby`
- **Example Queries:**
  - "What are my hobbies?"
  - "What's my preferred tech stack?"
  - "What do I like to do on weekends?"
  - "Tell me about my past projects"

### 5. **Decision Agent** ⚖️
- **Purpose:** Decision-making, trade-offs, analysis
- **Temperature:** 0.4 (analytical)
- **Trigger Keywords:** `should i`, `decide`, `choose`, `pros and cons`, `compare`, `which`, `decision`, `recommend`
- **Example Queries:**
  - "Should I learn Rust or Go?"
  - "Which framework is better: React or Vue?"
  - "Help me decide between these two options"
  - "What are the pros and cons of microservices?"

---

## 📤 Request Examples (cURL)

### Basic Chat Request
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I implement OAuth in Python?",
    "user_id": "eduardo"
  }'
```

### With Max Iterations
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me write an email",
    "user_id": "eduardo",
    "max_iterations": 5
  }'
```

### Using Graph Endpoint
```bash
curl -X POST http://localhost:8000/api/chat/graph \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my hobbies?",
    "user_id": "eduardo"
  }'
```

---

## 📥 Request Examples (JavaScript)

### Using Fetch API
```javascript
async function chatWithAgent(message, userId = "eduardo") {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      user_id: userId,
      max_iterations: 10
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  return data;
}

// Usage
chatWithAgent("How do I implement OAuth in Python?")
  .then(data => {
    console.log("Response:", data.response);
    console.log("Agent used:", data.agent_used);
    console.log("Confidence:", data.confidence);
  })
  .catch(error => console.error("Error:", error));
```

### Using Axios
```javascript
import axios from 'axios';

async function chatWithAgent(message, userId = "eduardo") {
  try {
    const response = await axios.post('http://localhost:8000/api/chat', {
      message: message,
      user_id: userId,
      max_iterations: 10
    });
    
    return response.data;
  } catch (error) {
    console.error("Error:", error.response?.data || error.message);
    throw error;
  }
}

// Usage
const result = await chatWithAgent("Should I learn Rust or Go?");
console.log(result);
```

---

## 📥 Request Examples (Python)

### Using requests
```python
import requests
import json

def chat_with_agent(message, user_id="eduardo", max_iterations=10):
    url = "http://localhost:8000/api/chat"
    
    payload = {
        "message": message,
        "user_id": user_id,
        "max_iterations": max_iterations
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Usage
result = chat_with_agent("How do I implement OAuth in Python?")
print(f"Response: {result['response']}")
print(f"Agent: {result['agent_used']}")
print(f"Confidence: {result['confidence']}")
```

---

## 📊 Response Structure Explained

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | The AI's text response |
| `agent_used` | string | Which agent handled the query (`general`, `professional`, `communication`, `knowledge`, `decision`) |
| `confidence` | float | Router confidence score (0.0-1.0) |
| `session_id` | string | Unique session identifier |
| `routing_history` | array | History of routing decisions |
| `iterations` | integer | Number of iterations used |
| `processing_time_ms` | float | Processing time in milliseconds |
| `sources_used` | array/null | Retrieved documents (Phase 6+, currently null) |

### Routing History Object

```json
{
  "agent_name": "professional",
  "confidence": 0.95,
  "reasoning": "LLM: Technical question about programming",
  "timestamp": "2026-02-07T21:19:57.158220"
}
```

---

## 🎨 Frontend UI Suggestions

### Chat Interface Components

**1. Message Input**
```jsx
<textarea 
  placeholder="Ask me anything..."
  value={message}
  onChange={(e) => setMessage(e.target.value)}
/>
<button onClick={sendMessage}>Send</button>
```

**2. Message Display**
```jsx
<div className="message user">
  <span className="content">{userMessage}</span>
</div>

<div className="message assistant">
  <span className="agent-badge">{agentUsed}</span>
  <span className="content">{response}</span>
  <span className="confidence">Confidence: {confidence}%</span>
</div>
```

**3. Agent Indicator**
Show which agent is responding with color coding:
- 🌐 General: Gray
- 💼 Professional: Blue
- ✉️ Communication: Green
- 🧠 Knowledge: Purple
- ⚖️ Decision: Orange

**4. Typing Indicator**
Show while `processing_time_ms` is pending:
```jsx
{loading && (
  <div className="typing-indicator">
    <span></span><span></span><span></span>
  </div>
)}
```

---

## 🔍 Suggested Query Examples (Pre-filled Prompts)

Show these to users as quick start examples:

**Professional Queries:**
- "How do I implement OAuth in Python?"
- "Explain the difference between REST and GraphQL"
- "Debug this code: [paste code]"

**Communication Queries:**
- "Help me write a professional email"
- "Draft a polite decline for a meeting"
- "How should I respond to this message?"

**Knowledge Queries:**
- "What are my hobbies?"
- "What's my preferred tech stack?"
- "Tell me about my past projects"

**Decision Queries:**
- "Should I learn Rust or Go?"
- "Compare React vs Vue for my project"
- "What are pros and cons of microservices?"

**General Queries:**
- "Hello! What can you help me with?"
- "Tell me something interesting"
- "How does this system work?"

---

## ⚠️ Error Handling

### Common Errors

**1. Server Unreachable**
```json
{
  "error": "Failed to connect to server"
}
```
**Solution:** Check if server is running on port 8000

**2. Invalid Request**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Solution:** Ensure `message` field is included in request

**3. Server Error**
```json
{
  "detail": "Internal server error"
}
```
**Solution:** Check server logs, retry request

### JavaScript Error Handling Example
```javascript
async function chatWithErrorHandling(message) {
  try {
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: "eduardo" })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
  } catch (error) {
    if (error.message.includes('Failed to fetch')) {
      return { error: 'Server is not running' };
    }
    return { error: error.message };
  }
}
```

---

## 🚀 Quick Start Checklist for Frontend Dev

- [ ] Server is running on `http://localhost:8000`
- [ ] Test `/health` endpoint returns 200
- [ ] Implement basic POST to `/api/chat`
- [ ] Display `response` in chat UI
- [ ] Show `agent_used` badge with color coding
- [ ] Display `confidence` score (optional)
- [ ] Add loading state during API call
- [ ] Implement error handling for network failures
- [ ] Add pre-filled example queries
- [ ] Style based on agent type
- [ ] Show `processing_time_ms` (optional)

---

## 🎯 Recommended Frontend Stack

**Suggested Technologies:**
- **Framework:** React, Vue, or Svelte
- **HTTP Client:** Axios or native Fetch API
- **State Management:** React Context/Redux (optional)
- **Styling:** Tailwind CSS, Material-UI, or styled-components
- **Markdown Rendering:** react-markdown (for formatted responses)

---

## 📱 Mobile Considerations

- Use responsive design (mobile-first)
- Touch-friendly input areas
- Optimize for slower connections (show loading states)
- Consider implementing message persistence (localStorage)
- Add pull-to-refresh for chat history

---

## 🔐 CORS Configuration

The API has CORS enabled with:
```python
allow_origins=["*"]  # Configure for production
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

For production, update to specific origins in `app/main.py`.

---

## 📖 Interactive API Docs

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- Test all endpoints directly in browser
- See request/response schemas
- Try different query examples

---

## 💡 Pro Tips

1. **Cache Responses:** Store chat history in state to avoid re-fetching
2. **Session Management:** Use `session_id` from responses to track conversations
3. **Typing Indicators:** Show while waiting for response
4. **Agent Badges:** Use different colors/icons per agent type
5. **Confidence Display:** Show confidence score as percentage or stars
6. **Error Recovery:** Implement retry logic for failed requests
7. **Offline Mode:** Show message when server is unreachable
8. **Response Streaming:** Consider implementing streaming for long responses (future)

---

## 📞 Need Help?

- **API Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

---

## 🔄 Coming Soon (Future Phases)

**Phase 6 - RAG System:**
- `sources_used` will contain retrieved documents
- Show "Based on your documents..." context

**Phase 7 - Persistence:**
- Conversation history retrieval
- Multi-session support
- User profiles

**Phase 8 - Production:**
- Authentication
- Rate limiting
- WebSocket streaming (real-time responses)

---

**Happy Building! 🚀**
