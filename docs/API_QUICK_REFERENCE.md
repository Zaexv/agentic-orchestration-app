# 📋 API Quick Reference Card

## Base URL
```
http://localhost:8000
```

## Main Endpoint
```bash
POST /api/chat
```

## Request Format
```json
{
  "message": "Your question here",
  "user_id": "eduardo"
}
```

## Response Format
```json
{
  "response": "AI response text",
  "agent_used": "professional|communication|knowledge|decision|general",
  "confidence": 0.95,
  "session_id": "session_xxx",
  "routing_history": [...],
  "iterations": 1,
  "processing_time_ms": 2000
}
```

## Quick Test
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!","user_id":"eduardo"}'
```

## JavaScript Example
```javascript
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "How do I code OAuth?",
    user_id: "eduardo"
  })
})
.then(res => res.json())
.then(data => console.log(data.response));
```

## 5 Agent Types

| Agent | Icon | Trigger | Example |
|-------|------|---------|---------|
| **General** | 🌐 | Default | "Hello!" |
| **Professional** | 💼 | Technical | "How do I code OAuth?" |
| **Communication** | ✉️ | Writing | "Write an email" |
| **Knowledge** | 🧠 | Personal | "What are my hobbies?" |
| **Decision** | ⚖️ | Choices | "Should I learn Rust?" |

## Color Scheme
- 🌐 General: `#6B7280` (gray)
- 💼 Professional: `#3B82F6` (blue)
- ✉️ Communication: `#10B981` (green)
- 🧠 Knowledge: `#8B5CF6` (purple)
- ⚖️ Decision: `#F59E0B` (orange)

## Status Codes
- `200` - Success
- `422` - Invalid request (missing fields)
- `500` - Server error

## Full Docs
📖 See `docs/FRONTEND_INTEGRATION.md` for complete guide
