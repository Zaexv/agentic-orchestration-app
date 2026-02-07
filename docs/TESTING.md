# Test Suite Documentation

## Overview

Comprehensive test suite for the Digital Twin AI system covering all Phase 3 functionality.

**Test Summary:**
- ✅ **73 tests passing**
- 🧪 **4 test modules** (test_state, test_agents, test_routing, test_api)
- 📊 **Coverage:** State management, agents, routing, API endpoints
- ⚡ **Execution time:** ~7 seconds

## Test Files

### 1. tests/test_state.py (13 tests)
**Coverage:** State management system (Phase 2)

Tests:
- State creation and initialization
- Message accumulation with ADD reducer
- Routing decision tracking
- Iteration counting and limits
- Safety mechanisms (max_iterations)
- Helper functions
- Type validation

**Run:** `make test-state`

### 2. tests/test_agents.py (17 tests)
**Coverage:** All 5 specialized agents (Phase 3)

Tests for each agent:
- Message processing and state updates
- Correct temperature settings
- System prompt usage
- Error handling (string responses)
- Empty message handling

Agents tested:
- General Agent (temp: 0.7)
- Professional Agent (temp: 0.3)
- Communication Agent (temp: 0.5)
- Knowledge Agent (temp: 0.4)
- Decision Agent (temp: 0.4)

**Features:**
- ✅ All LLM calls mocked (no API costs during testing)
- ✅ Parametrized tests for efficiency
- ✅ Comprehensive error handling tests

**Run:** `make test-agents`

### 3. tests/test_routing.py (25 tests)
**Coverage:** Keyword-based routing logic (Phase 3)

Tests:
- Single keyword routing
- Multiple keyword routing
- Confidence calculation formula
- Edge cases (empty string, no keywords, ties)
- Case insensitivity
- Confidence capping at 0.95
- Realistic queries for all agents

**Agent-specific tests:**
- Professional: Technical queries (code, Python, API, debugging)
- Communication: Writing tasks (email, drafts, tone)
- Knowledge: Personal queries (preferences, background)
- Decision: Choice queries (pros/cons, recommendations)
- General: Fallback for unmatched queries

**Run:** `make test-routing`

### 4. tests/test_api.py (18 tests)
**Coverage:** FastAPI endpoints (Phase 3)

Endpoints tested:
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/state/example` - State structure example
- `POST /api/chat` - Main chat endpoint

**Test categories:**
- Request validation (required fields, formats)
- Response structure and content
- Routing integration
- Error handling (invalid JSON, validation errors)
- Optional vs required parameters

**Run:** `make test-api`

## Test Execution

### Run All Tests
```bash
# Standard run
make test

# With detailed output
make test-all

# With coverage report
make test-coverage
```

### Run Individual Test Modules
```bash
make test-state      # State management tests
make test-agents     # Agent unit tests
make test-routing    # Routing logic tests
make test-api        # API endpoint tests
```

### Run Specific Test
```bash
# Run a specific test file
pytest tests/test_agents.py -v

# Run a specific test class
pytest tests/test_agents.py::TestGeneralAgent -v

# Run a specific test function
pytest tests/test_agents.py::TestGeneralAgent::test_general_agent_adds_message -v

# Run tests matching a pattern
pytest tests/ -k "routing" -v
```

## Test Strategy

### Unit Tests (test_agents.py)
- **Isolation:** Each agent tested independently
- **Mocking:** All LLM calls mocked to avoid API costs
- **Focus:** Verify agent behavior, not LLM quality
- **Speed:** Fast execution (~0.6s)

### Integration Tests (test_routing.py)
- **Scope:** Tests routing logic without actual agent execution
- **Coverage:** All routing paths and edge cases
- **Validation:** Confidence calculations and agent selection

### API Tests (test_api.py)
- **Approach:** Integration tests using TestClient
- **Coverage:** Request/response validation, routing, error handling
- **Note:** Some tests make real LLM calls (slower, ~6s)

## Key Testing Patterns

### 1. Mocking LLM Calls
```python
@patch('app.agents.general.get_llm')
def test_general_agent(mock_get_llm):
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Test response")
    mock_get_llm.return_value = mock_llm
    
    result = general_agent(state)
    assert len(result["messages"]) == 2
```

### 2. Parametrized Tests
```python
@pytest.mark.parametrize("agent_func,agent_name", [
    (general_agent, "general"),
    (professional_agent, "professional"),
    # ...
])
def test_all_agents(agent_func, agent_name):
    # Test runs once per agent
```

### 3. Fixture Reuse
```python
@pytest.fixture
def base_state() -> AgentState:
    return {...}  # Reusable test state
```

## Test Coverage by Component

| Component | Tests | Coverage |
|-----------|-------|----------|
| State Management | 13 | ✅ Complete |
| General Agent | 4 | ✅ Complete |
| Professional Agent | 2 | ✅ Complete |
| Communication Agent | 2 | ✅ Complete |
| Knowledge Agent | 2 | ✅ Complete |
| Decision Agent | 2 | ✅ Complete |
| Cross-agent error handling | 5 | ✅ Complete |
| Routing Logic | 25 | ✅ Complete |
| API Endpoints | 18 | ✅ Complete |
| **TOTAL** | **73** | **✅ Complete** |

## Coverage Gaps & Future Tests

### Phase 4 (Router Agent) - Not Yet Implemented
Will need tests for:
- LLM-based routing decisions
- Confidence calibration
- Multi-agent consultation
- Fallback logic

### Phase 5+ (Graph, RAG, Persistence)
Will need tests for:
- LangGraph workflow execution
- RAG document retrieval
- Vector store operations
- Database persistence
- ChromaDB integration

## Best Practices

### ✅ DO
- Mock external dependencies (LLM, databases)
- Test one thing per test function
- Use descriptive test names
- Test edge cases and error conditions
- Keep tests fast (mock expensive operations)
- Use fixtures for common setup

### ❌ DON'T
- Test implementation details
- Make tests depend on each other
- Use hardcoded timestamps (use datetime.now())
- Skip error handling tests
- Test library code (LangChain, FastAPI)
- Make real API calls in unit tests

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing
make test-all
```

### CI/CD Pipeline (Future)
```yaml
# .github/workflows/test.yml
- run: pip install -r requirements.txt
- run: pytest tests/ --cov=app
```

## Troubleshooting

### Issue: Tests hang or timeout
**Solution:** Check for unmocked LLM calls, increase timeout

### Issue: Import errors
**Solution:** Ensure virtual environment is activated: `source venv/bin/activate`

### Issue: Test fails with "module not found"
**Solution:** Install test dependencies: `pip install -r requirements.txt`

### Issue: Flaky API tests
**Solution:** API tests make real LLM calls, may be slow or fail due to network

## Test Maintenance

### When Adding New Agents
1. Add tests to `test_agents.py` following existing pattern
2. Add routing keywords to `test_routing.py`
3. Update routing integration tests in `test_api.py`

### When Modifying State
1. Update fixtures in `test_agents.py` and `test_api.py`
2. Update `test_state.py` if structure changes
3. Verify all tests still pass

### When Changing API
1. Update `test_api.py` request/response tests
2. Update integration tests
3. Update documentation

## Performance Benchmarks

| Test Suite | Time | LLM Calls |
|------------|------|-----------|
| test_state.py | 0.05s | 0 (all mocked) |
| test_agents.py | 0.58s | 0 (all mocked) |
| test_routing.py | 0.66s | 0 (pure logic) |
| test_api.py | 6.50s | ~5-10 (real calls) |
| **Total** | **~7.5s** | **5-10 real calls** |

## Summary

✅ **73 comprehensive tests** covering all Phase 3 functionality  
✅ **All tests passing** with minimal warnings  
✅ **Fast execution** (~7 seconds total)  
✅ **Mocked LLM calls** in unit tests (no API costs)  
✅ **Integration tests** verify end-to-end functionality  
✅ **Makefile commands** for easy execution  
✅ **Comprehensive coverage** of agents, routing, and API  

The test suite provides confidence for refactoring and future development! 🚀
