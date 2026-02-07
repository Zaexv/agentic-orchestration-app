# OpenAI Integration Setup Guide

## ✅ Integration Status

The OpenAI integration is **correctly configured** and ready to use. The system supports both:
1. **Standard OpenAI API** (default)
2. **OpenAI Proxy** (when on VPN)

## 🔧 Configuration

### Option 1: Standard OpenAI API (Default)

```bash
# .env file
OPENAI_API_KEY=your-actual-openai-key
OPENAI_API_BASE=https://api.openai.com/v1
DEFAULT_LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
```

### Option 2: OpenAI Proxy (VPN Required)

```bash
# .env file
OPENAI_API_KEY=your-mw-api-key
OPENAI_API_BASE=https://aikeys.maibornwolff.de/
DEFAULT_LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
```

## 🧪 Testing the Integration

### 1. Quick Test Script

```bash
cd /Users/eduardo.pertierrapuche/Development/mw-randd/agent-orchestration-app
source venv/bin/activate
python scripts/test_llm.py
```

**Expected Output:**
```
🔧 Testing LLM Configuration...
API Base: https://api.openai.com/v1
Model: gpt-4o-mini
Temperature: 0.1

✅ LLM Instance Created:
  - Model: gpt-4o-mini
  - Temperature: 0.1
  - Max Tokens: 4096

✅ Test Response: Hello from OpenAI API!
```

### 2. API Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model": "gpt-4o-mini",
  "vector_store": "chromadb",
  "api_base": "https://api.openai.com/v1"
}
```

## 📝 Usage in Code

The `get_llm()` factory automatically uses your configured settings:

```python
from app.config.llm import get_llm, get_embedding_model

# Default LLM (uses settings)
llm = get_llm()

# Override temperature for specific use cases
creative_llm = get_llm(temperature=0.7)  # More creative
precise_llm = get_llm(temperature=0.0)   # Deterministic

# Get embeddings
embeddings = get_embedding_model()
```

## 🔍 Verification Checklist

- [x] ✅ Settings module loads configuration
- [x] ✅ LLM factory creates instances with correct parameters
- [x] ✅ Supports both standard OpenAI and OpenAI API
- [x] ✅ FastAPI server reports configuration in health check
- [ ] ⚠️ **API Key Required** - Replace `OPENAI_API_KEY` in `.env` with valid key

## ⚠️ Current Status

**Integration Code:** ✅ Working  
**API Connection:** ⚠️ Pending valid API key

### Next Steps:

1. **Get Valid API Key:**
   - For Standard OpenAI: https://platform.openai.com/api-keys
   - For MW Proxy: Contact your MW admin

2. **Update `.env` file:**
   ```bash
   # Replace with your actual key
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **Test Connection:**
   ```bash
   make run-local  # Server auto-reloads with new config
   python scripts/test_llm.py
   ```

## 🔒 Security Notes

- Never commit `.env` file (already in `.gitignore`)
- API key in `.env` is local only
- OpenAI API requires VPN connection
- Standard OpenAI works from anywhere

## 📊 Test Results

```
Connection Test: ✅ PASSED (reaches API endpoint)
Authentication: ⚠️ PENDING (valid key needed)
Configuration: ✅ PASSED (all settings loaded)
Factory Pattern: ✅ PASSED (creates LLM instances)
```
