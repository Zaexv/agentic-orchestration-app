# Testing the Checkpointing Feature

This guide shows you how to test conversation memory in the running application.

## Quick Start

### Option 1: Interactive Test Script (Recommended)

Run the automated test script:

```bash
cd /Users/eduardo.pertierrapuche/Development/mw-randd/agent-orchestration-app
uv run python scripts/test_checkpointing.py
```

This script will:
- ✅ Test conversation memory across multiple turns
- ✅ Verify thread isolation
- ✅ Show clear pass/fail results
- ✅ Display agent responses in real-time

### Option 2: Manual API Testing with curl

**Step 1: Start a conversation**

```bash
# First message - introduce yourself
curl -X POST http://localhost:8000/api/chat/graph \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Alice and I love Python programming",
    "user_id": "test_user"
  }' | jq -r '.session_id, .response'
```

**Save the `session_id` from the response!**

**Step 2: Test memory - use the same session_id**

```bash
# Replace SESSION_ID with the actual ID from step 1
curl -X POST http://localhost:8000/api/chat/graph \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my name?",
    "user_id": "test_user",
    "conversation_id": "SESSION_ID"
  }' | jq -r '.response'
```

**Expected:** Agent should respond with "Alice" or mention your name!

**Step 3: Test memory again**

```bash
curl -X POST http://localhost:8000/api/chat/graph \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What programming language did I mention?",
    "user_id": "test_user",
    "conversation_id": "SESSION_ID"
  }' | jq -r '.response'
```

**Expected:** Agent should mention "Python"!

### Option 3: Using the API Documentation (Swagger UI)

1. **Open the API docs:**
   ```
   http://localhost:8000/docs
   ```

2. **Find the `/api/chat/graph` endpoint**

3. **Send first message:**
   ```json
   {
     "message": "My name is Bob and I work with React",
     "user_id": "test_user",
     "max_iterations": 5
   }
   ```
   
4. **Copy the `session_id` from the response**

5. **Send second message with the same `session_id`:**
   ```json
   {
     "message": "What framework did I mention?",
     "user_id": "test_user",
     "conversation_id": "paste-session-id-here",
     "max_iterations": 5
   }
   ```

6. **Verify:** Agent should mention "React"!

### Option 4: Frontend Testing (if React app is running)

1. **Start the frontend:**
   ```bash
   cd front_end
   npm run dev
   ```

2. **Open in browser:**
   ```
   http://localhost:5173
   ```

3. **Have a multi-turn conversation:**
   - Message 1: "My favorite movie is The Matrix"
   - Message 2: "What movie did I just mention?"
   - **Expected:** Agent remembers "The Matrix"

4. **Start a new conversation** (refresh page or new tab)
   - Different conversation should NOT know about The Matrix

## Verification Checklist

Test these scenarios to confirm checkpointing works:

### ✅ Basic Memory Test
- [ ] Agent remembers your name across turns
- [ ] Agent remembers facts you shared earlier
- [ ] Agent can reference previous messages

### ✅ Multi-Turn Context
- [ ] Start with: "I have 3 dogs"
- [ ] Follow up: "and 2 cats"
- [ ] Ask: "How many pets do I have?"
- [ ] **Expected:** Agent should say "5 pets" (3 dogs + 2 cats)

### ✅ Thread Isolation
- [ ] Start Conversation A: "I like coffee"
- [ ] Start Conversation B: "I like tea"  
- [ ] In Conversation A ask: "What do I like?"
- [ ] **Expected:** "Coffee" (not tea)

### ✅ Complex Reasoning
- [ ] Share multiple facts in turn 1
- [ ] Ask about combinations in turn 2
- [ ] Agent should integrate information from turn 1

## Troubleshooting

### Agent doesn't remember previous messages

**Check 1: Using correct conversation_id?**
```bash
# Make sure you're passing the same session_id/conversation_id
# in subsequent requests
```

**Check 2: Is checkpointing enabled?**
```bash
uv run python -c "
from app.orchestration.graph import workflow_app
print(f'Checkpointer enabled: {workflow_app.checkpointer is not None}')
"
```

**Check 3: Check the database**
```bash
ls -lh data/database/checkpoints.db
# Should exist and grow with each conversation
```

### "Connection refused" error

**Solution:** Start the backend server:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Agent response is generic/doesn't use context

**This is expected sometimes!** The agent might:
- Not need previous context for simple questions
- Choose to respond generally

Try more specific memory tests like:
- "My name is [unique name]"
- "What name did I just tell you?"

## Advanced: Inspect the Checkpoint Database

```bash
# Install sqlite3 (if not already installed)
# brew install sqlite3  # macOS

# View checkpoint data
sqlite3 data/database/checkpoints.db "
SELECT 
  thread_id,
  checkpoint_ns,
  checkpoint_id,
  length(checkpoint) as checkpoint_size_bytes
FROM checkpoints 
ORDER BY checkpoint_id DESC 
LIMIT 5;
"
```

## Success Indicators

When checkpointing is working, you'll see:

1. ✅ **Growing database file:** `data/database/checkpoints.db` increases in size
2. ✅ **Context awareness:** Agent references previous turns naturally
3. ✅ **Accumulating messages:** Response includes "I remember you mentioned..."
4. ✅ **Thread isolation:** Different session_ids maintain separate contexts

## Example Success Output

```
Turn 1:
👤 User: My name is Alice
🤖 Assistant: Nice to meet you, Alice!

Turn 2 (same session_id):
👤 User: What's my name?
🤖 Assistant: Your name is Alice! You introduced yourself in our previous message.

✅ Checkpointing is working!
```

## Next Steps

- Try complex multi-turn conversations
- Test with different agents (professional, communication, etc.)
- Monitor database growth
- Experiment with conversation branching

---

**Need help?** Check `docs/CHECKPOINTING.md` for detailed documentation.
