# 🧪 Phase 3 Testing Guide - Specialized Agents

Complete guide to testing the 5 specialized agents in the Digital Twin AI system.

---

## 📋 Overview

**Phase 3 Complete!** All 5 specialized agents are now implemented:

1. **General Agent** - Fallback for miscellaneous queries
2. **Professional Agent** - Technical expertise and work queries
3. **Communication Agent** - Writing style and communication
4. **Knowledge Agent** - Personal facts and memories
5. **Decision Agent** - Decision-making and values

---

## 🚀 Quick Start

```bash
# 1. Make sure server is running
make run-local

# 2. In another terminal, test all agents
./scripts/test_all_agents.sh

# Or test manually with curl (see examples below)
```

---

## 🎯 Testing Each Agent

### 1️⃣ General Agent

**Purpose:** Handles miscellaneous queries that don't fit other categories.

**Test Queries:**
```bash
# Basic greeting
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! How are you?",
    "user_id": "eduardo"
  }' | jq

# Random question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the weather like today?",
    "user_id": "eduardo"
  }' | jq

# Mixed intent
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me something interesting",
    "user_id": "eduardo"
  }' | jq
```

**Expected Response:**
- `agent_used: "general"`
- Confidence: ~0.6
- Friendly, balanced response

---

### 2️⃣ Professional Agent

**Purpose:** Technical expertise, programming, and work-related queries.

**Test Queries:**
```bash
# Programming question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I implement a binary search algorithm in Python?",
    "user_id": "eduardo"
  }' | jq

# Debugging help
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a TypeError in my JavaScript code, how do I debug it?",
    "user_id": "eduardo"
  }' | jq

# Architecture question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the best practices for API design?",
    "user_id": "eduardo"
  }' | jq

# Framework question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Should I use FastAPI or Flask for my Python API project?",
    "user_id": "eduardo"
  }' | jq
```

**Expected Response:**
- `agent_used: "professional"`
- Confidence: 0.75-0.95
- Technical, detailed response with examples

**Trigger Keywords:** code, programming, python, javascript, software, debug, api, architecture, technical, framework

---

### 3️⃣ Communication Agent

**Purpose:** Writing assistance, tone, and communication style.

**Test Queries:**
```bash
# Email drafting
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me write a professional email to decline a meeting invitation",
    "user_id": "eduardo"
  }' | jq

# Tone advice
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How should I phrase this message to sound more friendly?",
    "user_id": "eduardo"
  }' | jq

# Writing improvement
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you help me draft a response to this feedback?",
    "user_id": "eduardo"
  }' | jq
```

**Expected Response:**
- `agent_used: "communication"`
- Confidence: 0.75-0.95
- Specific suggestions with alternatives

**Trigger Keywords:** write, email, message, draft, tone, style, communicate, phrase, reply

---

### 4️⃣ Knowledge Agent

**Purpose:** Personal knowledge base, facts, and memories.

**Test Queries:**
```bash
# Personal preference
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do I usually prefer for breakfast?",
    "user_id": "eduardo"
  }' | jq

# Background information
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about my educational background",
    "user_id": "eduardo"
  }' | jq

# Personal facts
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my favorite programming languages?",
    "user_id": "eduardo"
  }' | jq
```

**Expected Response:**
- `agent_used: "knowledge"`
- Confidence: 0.75-0.95
- Will acknowledge limited knowledge (Phase 8 adds RAG)

**Trigger Keywords:** tell me about, what do i, my preference, my favorite, remember, personal, who am i

---

### 5️⃣ Decision Agent

**Purpose:** Decision-making assistance and value-based reasoning.

**Test Queries:**
```bash
# Decision help
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Should I take this job offer or stay at my current company?",
    "user_id": "eduardo"
  }' | jq

# Options evaluation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me evaluate the pros and cons of learning Rust vs Go",
    "user_id": "eduardo"
  }' | jq

# Recommendation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What would I recommend for a career change decision?",
    "user_id": "eduardo"
  }' | jq
```

**Expected Response:**
- `agent_used: "decision"`
- Confidence: 0.75-0.95
- Structured analysis with trade-offs

**Trigger Keywords:** should i, decide, choice, pros and cons, recommend, advice, what would i, trade-off

---

## 🔍 Verifying Routing Logic

Each response includes routing metadata:

```json
{
  "response": "...",
  "agent_used": "professional",
  "confidence": 0.85,
  "routing_history": [
    {
      "agent_name": "professional",
      "confidence": 0.85,
      "reasoning": "Matched 3 keyword(s) for professional domain",
      "timestamp": "2026-02-07T..."
    }
  ]
}
```

**Check:**
- ✅ Correct agent selected for query type
- ✅ Confidence score reasonable (0.6-0.95)
- ✅ Reasoning explains routing decision

---

## 🧪 Testing Agent Characteristics

### Temperature Settings

Each agent uses different temperature for different creativity levels:

- **Professional:** 0.3 (precise, technical)
- **Knowledge:** 0.4 (factual, specific)
- **Decision:** 0.4 (analytical, structured)
- **Communication:** 0.5 (balanced creativity)
- **General:** 0.7 (more creative)

### Response Style Verification

**Professional Agent:**
- Technical terminology
- Code examples or technical details
- Solution-oriented
- Practical explanations

**Communication Agent:**
- Specific phrasing suggestions
- Multiple options/alternatives
- Explanation of tone choices
- Context-aware recommendations

**Knowledge Agent:**
- Personal context (when available)
- Honest about knowledge gaps (currently)
- Specific details when known
- Helpful guidance

**Decision Agent:**
- Structured analysis
- Trade-off discussion
- Multiple perspectives
- Value-based considerations

**General Agent:**
- Conversational tone
- Balanced responses
- Acknowledges limitations
- Adaptable to context

---

## 🔄 Testing Multi-Turn Conversations

Currently each request is independent. Multi-turn will be enhanced in Phase 5 (LangGraph).

```bash
# First message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help with Python",
    "user_id": "eduardo"
  }' | jq '.session_id'
# Save the session_id for future phases
```

---

## 📊 Success Criteria

**Phase 3 is successful if:**

- ✅ All 5 agents respond correctly
- ✅ Routing selects appropriate agent (>80% accuracy)
- ✅ Response style matches agent personality
- ✅ Temperature settings produce expected creativity
- ✅ API response time <3 seconds
- ✅ Error handling works (fallback to general)

---

## 🐛 Troubleshooting

### Agent Not Responding
```bash
# Check server is running
curl http://localhost:8000/health

# Check logs for errors
# Server will print errors to console
```

### Wrong Agent Selected
```bash
# Check routing history in response
# Verify keywords in your message
# Adjust message to include more specific keywords
```

### Slow Response
```bash
# Check OpenAI API status
# Verify OpenAI API connectivity
# Check processing_time_ms in response
```

---

## 📝 Test Script (Complete)

Save this as `scripts/test_all_agents.sh`:

```bash
#!/bin/bash
echo "🧪 Testing All Agents"
echo ""

BASE_URL="http://localhost:8000/api/chat"

# Test General Agent
echo "1️⃣  General Agent:"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! How are you?", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, response: .response[:100]}'
echo ""

# Test Professional Agent
echo "2️⃣  Professional Agent:"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I implement error handling in Python?", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, response: .response[:100]}'
echo ""

# Test Communication Agent
echo "3️⃣  Communication Agent:"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me write a professional email", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, response: .response[:100]}'
echo ""

# Test Knowledge Agent
echo "4️⃣  Knowledge Agent:"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "What do I prefer for programming languages?", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, response: .response[:100]}'
echo ""

# Test Decision Agent
echo "5️⃣  Decision Agent:"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "Should I learn Rust or Go? Help me decide.", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, response: .response[:100]}'
echo ""

echo "✅ All agents tested!"
```

Then run:
```bash
chmod +x scripts/test_all_agents.sh
./scripts/test_all_agents.sh
```

---

## 🎯 Next Phase Preview

**Phase 4: Router Implementation**
- Replace keyword routing with LLM-based router
- Improve routing accuracy with semantic understanding
- Add confidence calibration
- Multi-agent consultation for complex queries

---

## 📚 Related Documentation

- [State Management Guide](STATE_MANAGEMENT_GUIDE.md)
- [API Testing Guide](API_TESTING.md)
- [Project Plan](../project_plan.md)
- [Project Status](../STATUS.md)

---

**Happy Testing!** 🎉
