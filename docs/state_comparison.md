# State Management Patterns - Visual Comparison

## Pattern Comparison

### Pattern 1: REPLACE (Default - Overwrites)

**Use For:** Current snapshot values

```python
class AgentState(TypedDict):
    current_agent: str              # "router" → "professional"
    iterations: int                 # 0 → 1 → 2
    routing_confidence: float       # 0.0 → 0.85 → 0.92
```

✅ **Good for:** Counters, flags, current values  
❌ **Bad for:** History, logs, accumulated data

---

### Pattern 2: ADD (Accumulative - Appends)

**Use For:** History and audit trails

```python
from operator import add
from typing import Annotated

class AgentState(TypedDict):
    messages: Annotated[list[Message], add]
    # [msg1] → [msg1, msg2] → [msg1, msg2, msg3]
    
    routing_history: Annotated[list[RoutingDecision], add]
    # [] → [router→prof] → [router→prof, prof→general]
```

✅ **Good for:** Conversation history, audit logs, accumulated results  
❌ **Bad for:** Single current values

---

### Pattern 3: CUSTOM REDUCER (Your own merge logic)

**Use For:** Complex merging (e.g., deduplicate, weighted average)

```python
def merge_docs(a: list, b: list) -> list:
    # Deduplicate by source
    seen = {doc.source for doc in a}
    return a + [doc for doc in b if doc.source not in seen]

class AgentState(TypedDict):
    retrieved_docs: Annotated[list[Doc], merge_docs]
```

✅ **Good for:** Deduplication, weighted merging, special logic  
❌ **Bad for:** Simple accumulation (use add) or replacement (use default)

---

## Real-World Example

### Initial State (Router):
```python
{
    "messages": ["User: What skills do I have?"],
    "current_agent": "router",
    "iterations": 0,
    "routing_history": []
}
```

### After Router Decision:
```python
{
    "messages": ["User: What skills do I have?"],  # unchanged
    "current_agent": "professional",  # REPLACED
    "iterations": 1,  # REPLACED
    "routing_history": [  # ADDED
        {"agent": "professional", "confidence": 0.9}
    ]
}
```

### After Professional Agent Response:
```python
{
    "messages": [  # ADDED
        "User: What skills do I have?",
        "Assistant: Python, TypeScript, Go..."
    ],
    "current_agent": "professional",  # unchanged
    "iterations": 2,  # REPLACED
    "routing_history": [  # unchanged
        {"agent": "professional", "confidence": 0.9}
    ]
}
```

---

## When to Use Each Pattern

| Data Type | Pattern | Why |
|-----------|---------|-----|
| Conversation msgs | ✅ ADD | Need full history |
| Current agent | ✅ REPLACE | Only care about current |
| Iteration counter | ✅ REPLACE | Single incrementing value |
| Routing history | ✅ ADD | Audit trail needed |
| Retrieved docs | ⚠️ REPLACE or CUSTOM | Depends on use case |
| Final response | ✅ REPLACE | Only one final answer |
| Error message | ✅ REPLACE | Latest error matters |
| User preferences | ✅ REPLACE | Current prefs only |
| Confidence score | ✅ REPLACE | Current confidence |
| Timestamps | ✅ REPLACE | Latest timestamp |

---

## Memory Considerations

### ⚠️ Warning: Accumulative Lists Grow Indefinitely

**Problem:**
```python
messages: Annotated[list[Message], add]
# After 1000 turns → 1000 messages in memory
```

**Solutions:**

1. **Compress old messages** (summarize)
2. **Keep sliding window** (last N messages)
3. **Use external storage** (DB) for old messages
4. **Checkpoint and prune** periodically

**Example:**
```python
def compress_messages(state: AgentState) -> AgentState:
    if len(state["messages"]) > 50:
        old = state["messages"][:-20]
        summary = summarize(old)
        state["messages"] = [
            Message(role="system", content=f"Previous: {summary}"),
            *state["messages"][-20:]
        ]
    return state
```

---

## Flow Diagram

```
┌─────────────────┐
│  Initial State  │
│  messages: [U]  │
│  agent: router  │
│  iter: 0        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Router Update  │
│  agent: prof ←──┼─── REPLACE
│  iter: 1     ←──┼─── REPLACE
│  history: [R] ←─┼─── ADD
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent Response │
│  messages:   ←──┼─── ADD
│    [U, A]       │
│  iter: 2     ←──┼─── REPLACE
└─────────────────┘
```

**Legend:**
- U = User message
- A = Assistant message
- R = Routing decision
- prof = Professional agent

