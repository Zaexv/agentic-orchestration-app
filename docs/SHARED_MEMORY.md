# Shared Memory System

## Overview

All agents now share a **common conversation state**, enabling seamless multi-turn conversations where different agents can participate based on context.

## How It Works

### 1. **Conversation History is Shared**
- All messages (from any agent) are stored in the conversation
- When you respond, the router sees the **full conversation history**
- The router picks the **most appropriate agent** for your new message

### 2. **Context-Aware Routing**
```
User: "How do I write a Python function?"
Router → Professional Agent responds

User: "Can you make the tone more casual?"
Router → Communication Agent responds (sees Professional's code)

User: "What do I usually prefer for coding style?"
Router → Knowledge Agent responds (sees entire conversation)
```

### 3. **Agent Can See Previous Responses**
Each agent receives:
- **Last 10 messages** from the conversation
- Messages from **all agents** (not just their own)
- **Full context** to provide coherent responses

## Architecture Changes

### State Management
```python
# Conversation history includes all agents
state["messages"] = [
    Message(role="user", content="Write code"),
    Message(role="assistant", content="...", agent="professional"),
    Message(role="user", content="Make it casual"),
    Message(role="assistant", content="...", agent="communication"),
]
```

### Router Decision
```python
# Router sees last 5 messages for context
conversation_context = "\n".join([
    f"{msg.role}: {msg.content}" 
    for msg in history_messages[-5:]
])

# Routes to best agent for current message + context
target_agent = router_agent_with_fallback(
    f"Context:\n{conversation_context}\n\nCurrent: {message}"
)
```

### Agent Execution
```python
# Each agent sees conversation history
llm_messages = [
    {"role": "system", "content": system_prompt},
    # Last 10 messages from conversation
    *[{"role": msg.role, "content": msg.content} for msg in messages[-10:]]
]
```

## Benefits

✅ **Seamless Handoffs**: Conversation flows naturally between agents
✅ **Context Preservation**: Each agent understands what happened before
✅ **Smart Routing**: Router picks best agent based on conversation flow
✅ **No Memory Loss**: Full conversation history maintained across agents
✅ **Natural Dialogue**: Multi-turn conversations work as expected

## Example Flow

```
Turn 1:
User: "Debug this Python code: [code]"
→ Router: Chooses Professional (technical query)
→ Professional: Analyzes and fixes code

Turn 2:
User: "Can you explain it more simply?"
→ Router: Chooses Communication (tone/style)
→ Communication: Sees Professional's fix, explains simply

Turn 3:
User: "What's my preferred Python style?"
→ Router: Chooses Knowledge (personal preferences)
→ Knowledge: Retrieves user preferences from RAG

Turn 4:
User: "Should I use this approach?"
→ Router: Chooses Decision (evaluation)
→ Decision: Reviews previous conversation, provides recommendation
```

## Technical Details

- **Database**: Conversations stored in SQLite with full history
- **Loading**: Previous messages loaded when `conversation_id` provided
- **Routing**: Last 5 messages used as context for routing decision
- **Execution**: Last 10 messages passed to agent LLM
- **No Isolation**: Agents are NOT isolated - they share state
- **Single Turn**: Each API call = one routing + one agent response

## Testing

```bash
# Start conversation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Write a Python function", "user_id": "test"}'

# Continue with different topic (same conversation_id)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Make it more readable", 
    "user_id": "test",
    "conversation_id": "previous-conv-id"
  }'
```

The router will see both messages and pick the appropriate agent!
