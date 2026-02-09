# 🔄 Multi-Iteration Test Prompts

## ✅ System Now Uses LangGraph Workflow!

The `/api/chat` endpoint now runs through the LangGraph workflow, enabling multi-iteration!

---

## 📝 Test Prompts That Should Trigger Iteration

### 1. **Vague/Ambiguous Query (Low Confidence)**
This should get low confidence and trigger a retry:

```
"Help me with this"
"I need assistance"
"Can you help?"
"What should I do?"
```

**Expected behavior:**
- Iteration 1: Router picks "general" with ~50-60% confidence
- should_continue detects low confidence (<70%)
- Iteration 2: Router re-evaluates, may pick different agent
- Response includes `iterations: 2` in routing_history

---

### 2. **Multi-Part Question**
These complex queries may trigger multiple iterations:

```
"Write a Python function to sort a list, explain how it works, and show me some test cases"

"Help me decide between Python and JavaScript for web development, explain the pros and cons, and give me a recommendation"

"Tell me about my coding preferences, write a sample function in my style, and explain why that's my preferred approach"
```

**Expected behavior:**
- Multiple routing decisions in routing_history
- Iterations > 1
- Different agents may be involved

---

### 3. **Trigger Continuation Signal**
Create a scenario where the agent might say "let me also":

```
"Explain decorators in Python"
```

**Expected behavior:**
- Professional agent might respond with: "Here's how decorators work. Let me also show you some examples..."
- should_continue detects "let me also" and continues
- Iteration 2: Agent provides examples
- Response shows `iterations: 2`

---

### 4. **Cross-Agent Collaboration**
Start a conversation that naturally shifts between agents:

```
Turn 1: "Write a Python class for user management"
→ Professional agent

Turn 2: "Make the docstrings more casual and friendly"  
→ Should route to Communication agent (sees Professional's code)

Turn 3: "What's my preferred naming convention?"
→ Should route to Knowledge agent
```

---

## 🧪 Testing via cURL

### Check Iterations in Response

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me with this",
    "user_id": "test",
    "max_iterations": 5
  }' | jq '.iterations, .routing_history'
```

### Vague Query Test

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need assistance",
    "user_id": "test"
  }' | jq '{iterations, agent_used, confidence, routing_history: .routing_history | map({agent: .agent_name, confidence})}'
```

### Multi-Part Query Test

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write Python code, explain it, and show examples",
    "user_id": "test",
    "max_iterations": 5
  }' | jq '.iterations'
```

---

## 📊 Expected Response Structure

```json
{
  "response": "...",
  "agent_used": "professional",
  "confidence": 0.85,
  "iterations": 2,
  "routing_history": [
    {
      "agent_name": "general",
      "confidence": 0.55,
      "reasoning": "Vague query, general handler",
      "timestamp": "2026-02-08T20:15:00"
    },
    {
      "agent_name": "professional", 
      "confidence": 0.85,
      "reasoning": "Re-routed for better accuracy",
      "timestamp": "2026-02-08T20:15:01"
    }
  ],
  "processing_time_ms": 2341.23
}
```

---

## 🎯 How to Verify Iteration is Working

### In Frontend (http://localhost:5173):

1. Send a vague message: **"Help me"**
2. Check the response trace panel (click "View Trace")
3. Look for:
   - **Iterations**: Should show > 1
   - **Routing History**: Multiple agent selections

### In Backend Logs:

```bash
# Watch for workflow execution
tail -f /path/to/logs

# You should see:
# - "Executing router_node"
# - "Executing [agent]_agent"  
# - "should_continue: continue" (if iterating)
# - "Executing router_node" (again)
# - "Executing [different_agent]"
# - "should_continue: end"
```

---

## 🔍 Debugging

If iterations are still 1:

1. **Check should_continue logic** in `app/orchestration/graph.py`
2. **Verify confidence scores** - Need <70% for retry
3. **Check agent responses** - Need continuation keywords
4. **Increase max_iterations** in request (default is 5)

```python
# In graph.py, add debug logging:
def should_continue(state):
    print(f"🔍 Iterations: {state['iterations']}/{state['max_iterations']}")
    print(f"🔍 Confidence: {state['routing_history'][-1].confidence if state['routing_history'] else 'N/A'}")
    print(f"🔍 Last message: {state['messages'][-1].content[:100]}")
    # ... rest of logic
```

---

## 🎉 Success Indicators

✅ Response shows `iterations: 2` or higher
✅ `routing_history` has multiple entries
✅ Different agents appear in routing_history
✅ Processing time is higher (multiple LLM calls)
✅ Response is more complete/refined

---

**Version**: 1.1.0
**Updated**: 2026-02-08
**Status**: ✅ Multi-iteration enabled via LangGraph workflow
