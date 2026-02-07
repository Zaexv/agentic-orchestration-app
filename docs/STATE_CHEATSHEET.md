# State Management Cheat Sheet 🚀

## Quick Decision Tree

```
Do you need history/audit trail?
├─ YES → Use Annotated[list, add]
│         Example: messages, routing_history
│
└─ NO → Is it a single current value?
    ├─ YES → Use default (replace)
    │         Example: current_agent, iterations
    │
    └─ NO → Need custom merge logic?
        └─ YES → Use Annotated[list, custom_func]
                  Example: deduplicate docs
```

## The Three Patterns

### 1️⃣ REPLACE (Default)
```python
current_agent: str  # No annotation = replace
iterations: int     # 0 → 1 → 2 → 3
```

### 2️⃣ ADD (Accumulate)
```python
messages: Annotated[list[Message], add]
# [A] → [A,B] → [A,B,C]
```

### 3️⃣ CUSTOM (Your Logic)
```python
def dedupe(a, b):
    return list(set(a + b))

docs: Annotated[list, dedupe]
```

## Common Field Types

| Field | Pattern | Why |
|-------|---------|-----|
| `messages` | ADD | Need full conversation |
| `current_agent` | REPLACE | Only current matters |
| `iterations` | REPLACE | Counter |
| `routing_history` | ADD | Audit trail |
| `final_response` | REPLACE | One answer |
| `error` | REPLACE | Latest error |
| `retrieved_docs` | REPLACE | New each query |

## Agent Pattern

```python
def my_agent(state: AgentState) -> AgentState:
    # 1. Read from state
    query = state["user_query"]
    
    # 2. Do work
    result = do_something(query)
    
    # 3. Update state
    state["messages"].append(Message(...))  # ADD
    state["current_agent"] = "my_agent"     # REPLACE
    
    # 4. Always return
    return state
```

## Safety Check

```python
# ✅ ALWAYS add max iterations
state["iterations"] = 0
state["max_iterations"] = 10

# ✅ ALWAYS check should_continue
if state["iterations"] >= state["max_iterations"]:
    state["should_continue"] = False
```

## Memory Warning

⚠️ Lists with `add` grow forever!

**Solution:** Compress periodically
```python
if len(state["messages"]) > 50:
    # Keep last 20, summarize rest
    state["messages"] = compress(state["messages"])
```

## Quick Reference

```python
from typing import TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    # History (accumulate)
    messages: Annotated[list, add]
    routing_history: Annotated[list, add]
    
    # Current values (replace)
    current_agent: str
    iterations: int
    final_response: Optional[str]
```

## Testing Your State

```bash
# Run state tests
make test-state

# See working example
python scripts/example_state.py
```

---
**Read Full Guide:** `docs/STATE_MANAGEMENT_GUIDE.md`
