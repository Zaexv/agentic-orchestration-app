# Checkpoint Database Bloat Fix

## Problem Summary

The checkpoint database was growing to abnormal sizes:
- **Old behavior**: 649 MB per checkpoint after ~100 messages
- **Expected**: < 1 MB per checkpoint
- **Root cause**: Unbounded accumulation in state fields

## Root Cause

The `AgentState` TypedDict used `Annotated[list, add]` reducers that accumulated items **indefinitely**:

```python
# BEFORE (❌ Unbounded growth)
messages: Annotated[list[Message], add]              # All messages forever
routing_history: Annotated[list[RoutingDecision], add]  # All routing decisions
iteration_log: Annotated[list[IterationLog], add]   # All iteration logs
```

Each checkpoint saved the **entire history**, so:
- After 1,000 messages: 1,000 messages in every checkpoint
- After 10,000 routing decisions: 10,000 decisions in every checkpoint
- Database grew exponentially: 5 GB → 13 GB → 60+ GB

## Solution

### 1. Custom Size-Limited Reducers

Created custom reducers that keep only the last N items:

```python
# AFTER (✅ Bounded growth)
MAX_MESSAGES = 100
MAX_ROUTING_HISTORY = 50
MAX_ITERATION_LOG = 100

def add_and_limit(existing: list, new: list, max_size: int) -> list:
    """Adds items but keeps only last max_size items"""
    combined = existing + new
    if len(combined) > max_size:
        return combined[-max_size:]
    return combined

messages: Annotated[list[Message], add_messages]              # Last 100
routing_history: Annotated[list[RoutingDecision], add_routing_history]  # Last 50
iteration_log: Annotated[list[IterationLog], add_iteration_log]  # Last 100
```

### 2. Fixed Checkpoint Continuation

The API was creating **full initial state** every time, causing state duplication when merged with checkpoints.

**Before (❌ Duplicated state):**
```python
# Always created full state, even when continuing
state = create_initial_state(user_query=request.message, ...)
final_state = run_workflow(state, thread_id=thread_id)
```

**After (✅ Only new data):**
```python
# Check if checkpoint exists
checkpoint = workflow_app.get_state(config)

if checkpoint.values:
    # Continuing: only add new message
    state_input = {"messages": [Message(role="user", content=request.message)]}
else:
    # New conversation: create full state
    state_input = create_initial_state(user_query=request.message, ...)
```

## Results

### Before Fix
```
Thread: be0f5c6d-9cec-4ddd-9ccc-9b90d06e9937
  Checkpoints: 5
  Total size: 3.2 GB (649 MB per checkpoint)
  Database size: 13.2 GB

Thread: e0c2cb59-f101-4cf6-830f-3dcdbab079c6
  Checkpoints: 35
  Total size: 2.1 GB (62 MB per checkpoint)
```

### After Fix
```
15 messages in conversation:
  Checkpoints: 60
  First checkpoint: 0.89 KB
  Final checkpoint: 81.22 KB
  Total size: ~4 MB
  Growth per message: ~5 KB
  
✅ Checkpoint size stayed < 100 KB even after 15 messages
```

### Size Comparison
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg checkpoint size | 649 MB | 11-81 KB | **8,000x smaller** |
| Database after 100 msgs | 60+ GB | < 10 MB | **6,000x smaller** |
| Growth per message | ~650 MB | ~5 KB | **130,000x better** |

## Technical Details

### Files Modified

1. **`app/orchestration/state.py`**
   - Added `add_and_limit()` helper function
   - Created `add_messages()`, `add_routing_history()`, `add_iteration_log()` reducers
   - Updated `AgentState` to use size-limited reducers
   - Set limits: MAX_MESSAGES=100, MAX_ROUTING_HISTORY=50, MAX_ITERATION_LOG=100

2. **`app/api/routes.py`**
   - Imported `workflow_app` for checkpoint state inspection
   - Modified `/chat/graph` endpoint to check for existing checkpoints
   - Modified `/chat` endpoint similarly
   - Only pass new message when continuing, not full state

### State Size Limits

| Field | Max Items | Typical Size | Reason |
|-------|-----------|--------------|---------|
| `messages` | 100 | ~50 KB | Recent conversation context |
| `routing_history` | 50 | ~5 KB | Recent routing decisions |
| `iteration_log` | 100 | ~10 KB | Recent execution logs |
| `retrieved_docs` | No limit | ~5-20 KB | Replaced per query, not accumulated |

**Total expected checkpoint size**: 50-100 KB under normal usage

### Why These Limits?

- **100 messages**: Provides ~50 back-and-forth exchanges (enough context)
- **50 routing decisions**: Tracks recent agent selections
- **100 iteration logs**: Debugging recent executions

Older items are automatically pruned when limits are exceeded.

## Testing

### Unit Tests
```bash
pytest tests/test_checkpointing.py -v
# All 7 tests pass
```

### Growth Test
```bash
python << 'EOF'
from app.orchestration.graph import workflow_app
# Send 20 messages...
# Final checkpoint: 62.22 KB ✅
EOF
```

### API Stress Test
```bash
# 15 consecutive messages
# Final checkpoint: 81.22 KB ✅
# No errors, no bloat
```

## Migration

The fix is **automatic** - no migration needed:

1. Old bloated checkpoints remain in database (but ignored)
2. New checkpoints use size-limited reducers automatically
3. Clean up old checkpoints with:

```bash
python scripts/manage_checkpoints.py cleanup --keep 5
python scripts/manage_checkpoints.py vacuum
```

Or delete and recreate:

```bash
rm data/database/checkpoints.db
# Database recreates on next request
```

## Configuration

To adjust size limits, edit `app/orchestration/state.py`:

```python
MAX_MESSAGES = 100        # Increase for longer context
MAX_ROUTING_HISTORY = 50  # Increase for detailed routing history
MAX_ITERATION_LOG = 100   # Increase for debugging
```

**Warning**: Larger limits = larger checkpoints. Keep under 1 MB per checkpoint.

## Monitoring

Check checkpoint health:

```bash
python scripts/manage_checkpoints.py stats
```

Expected output:
```
Total checkpoints: 150
Database size: 25.3 MB
Average checkpoint size: 172.8 KB  # Should be < 1 MB
```

If average > 1 MB, investigate:
1. Check if limits are set correctly
2. Look for large objects in state
3. Verify reducers are working

## Related Issues

- **Issue**: "System breaks after a couple of messages"
  - **Cause**: State duplication in API causing merge conflicts
  - **Fix**: Only pass new message when continuing conversation

- **Issue**: "Checkpoint database too big to commit"
  - **Cause**: Unbounded state accumulation
  - **Fix**: Size-limited reducers + proper checkpoint continuation

## References

- LangGraph Checkpointing: https://langchain-ai.github.io/langgraph/concepts/persistence/
- State Reducers: https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers
- Implementation: `app/orchestration/state.py`, `app/api/routes.py`
