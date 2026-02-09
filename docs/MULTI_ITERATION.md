# Multi-Iteration Agent System

## Overview

Agents can now iterate **multiple times within a single request** to:
- Refine responses
- Gather additional information
- Perform complex multi-step reasoning
- Retry with different agents if confidence is low

## How It Works

### Iteration Logic

The system continues iterating when:

1. **Low Confidence Retry** (< 70% confidence)
   - Automatically routes to a different agent
   - Maximum 2 iterations for low confidence

2. **Agent Continuation Signals**
   - Agent response contains: "let me", "I'll also", "additionally", etc.
   - Indicates the agent wants to provide more information
   - Up to 3 iterations allowed

3. **Complex Query Handling**
   - Multi-part questions can trigger multiple agent calls
   - Each iteration can route to a different specialized agent

### Default Limits

```python
max_iterations: 5  # Default per request
- Low confidence: up to 2 iterations
- Complex queries: up to 3 iterations
- Confidence >= 70%: usually 1 iteration
```

## Example Flows

### Example 1: Low Confidence Retry
```
User: "How do I optimize this?"
Iteration 1:
  → Router: General (60% confidence) ← LOW!
  → General responds
  → should_continue: "continue" (low confidence)

Iteration 2:
  → Router: Re-evaluate with response
  → Professional (85% confidence)
  → Professional provides better answer
  → should_continue: "end" (high confidence)
```

### Example 2: Multi-Part Response
```
User: "Explain Python decorators and show examples"
Iteration 1:
  → Router: Professional (90%)
  → Professional: "Here's the explanation. Let me also show you examples..."
  → should_continue: "continue" (found "let me also")

Iteration 2:
  → Router: Same agent continues
  → Professional: Provides code examples
  → should_continue: "end"
```

### Example 3: Single Iteration (Typical)
```
User: "Write a Python function"
Iteration 1:
  → Router: Professional (95%)
  → Professional: Provides complete answer
  → should_continue: "end" (high confidence, complete)
```

## Configuration

### In API Request
```json
{
  "message": "Your query",
  "user_id": "user",
  "max_iterations": 5
}
```

### Per Agent (can set should_continue flag)
```python
# Agent can signal to stop early
state["should_continue"] = False
return state
```

## Benefits

✅ **Better Accuracy**: Retry with different agent if confidence is low
✅ **Complete Responses**: Agents can provide multi-part answers
✅ **Adaptive**: System adjusts based on query complexity
✅ **Controlled**: Max iterations prevent infinite loops
✅ **Transparent**: Routing history shows all iterations

## Monitoring

The response includes iteration details:

```json
{
  "response": "...",
  "iterations": 2,
  "routing_history": [
    {
      "agent_name": "general",
      "confidence": 0.60,
      "reasoning": "Generic query",
      "timestamp": "..."
    },
    {
      "agent_name": "professional",
      "confidence": 0.85,
      "reasoning": "Re-routed for better accuracy",
      "timestamp": "..."
    }
  ]
}
```

## Technical Details

### should_continue() Logic
```python
def should_continue(state):
    # Max iterations check
    if state["iterations"] >= state["max_iterations"]:
        return "end"
    
    # Low confidence retry (<70%, max 2 iterations)
    if latest_confidence < 0.7 and iterations < 2:
        return "continue"
    
    # Agent signals more work
    if "let me" or "I'll also" in last_message:
        return "continue"
    
    # Default: end
    return "end"
```

### State Updates
- `iterations`: Incremented after each agent execution
- `routing_history`: Appends each routing decision
- `messages`: Accumulates all responses
- `should_continue`: Can be set by agents

## Best Practices

1. **Set appropriate max_iterations**
   - Simple queries: 1-2
   - Complex queries: 3-5
   - Research tasks: 5-10

2. **Monitor routing_history**
   - Check if multiple agents were used
   - Verify confidence scores improved

3. **Agent design**
   - Complete answers in one iteration when possible
   - Use continuation signals sparingly
   - Set `should_continue = False` when done

## Differences from Before

**Before**: Always 1 iteration (hardcoded `return "end"`)
**Now**: Dynamic 1-5 iterations based on confidence and signals

This enables more intelligent, adaptive responses! 🚀
