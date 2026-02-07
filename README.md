# 🤖 AI Digital Twin - Multi-Agent Orchestration

> **AI Digital Twin system with specialized agents using router orchestration pattern**  
> Built with LangChain, LangGraph, and FastAPI

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-latest-orange.svg)](https://python.langchain.com/)

---

## 📋 Overview

This project implements an AI-powered digital twin with **5 specialized agents** that intelligently route queries using LLM-based semantic routing. The system uses **LangGraph** for orchestration and will support **RAG** for personalized knowledge retrieval.

**Current Status:** 🚧 **Phase 5/8 Complete** (62.5%) - LangGraph Orchestration ✅

---

## ✨ Features

- 🎯 **Intelligent Routing** - 95% accuracy with LLM-based semantic understanding
- 🤖 **5 Specialized Agents** - Professional, Communication, Knowledge, Decision, General
- 📊 **StateGraph Workflow** - Visual graph-based orchestration with LangGraph
- 🔄 **Multi-turn Ready** - Foundation for complex conversations (coming soon)
- 🧪 **89 Tests** - Comprehensive test coverage (100% passing)
- 📚 **Rich Documentation** - 15+ guides including frontend integration

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/Zaexv/agentic-orchestration-app.git
cd agentic-orchestration-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_key_here
```

### 3. Run the Server

```bash
# Using Makefile
make run-local

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

🎉 **Visit:** http://localhost:8000/docs for interactive API documentation

---

## 🤖 Specialized Agents

| Agent | Icon | Purpose | Temperature | Example Query |
|-------|------|---------|-------------|---------------|
| **Professional** | 💼 | Technical expertise, coding | 0.3 | "How do I implement OAuth?" |
| **Communication** | ✉️ | Writing assistance, tone | 0.5 | "Help me write an email" |
| **Knowledge** | 🧠 | Personal facts, memories | 0.4 | "What are my hobbies?" |
| **Decision** | ⚖️ | Decision-making, trade-offs | 0.4 | "Should I learn Rust or Go?" |
| **General** | 🌐 | Fallback, conversation | 0.7 | "Hello, how are you?" |

**Routing Accuracy:** ~95% (semantic understanding via LLM)

---

## 🔌 API Usage

### Basic Request

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I implement OAuth in Python?",
    "user_id": "eduardo"
  }'
```

### Response Format

```json
{
  "response": "To implement OAuth in Python...",
  "agent_used": "professional",
  "confidence": 0.95,
  "session_id": "session_xxx",
  "iterations": 1,
  "processing_time_ms": 2107.69
}
```

📖 **Full API Guide:** See [`docs/FRONTEND_INTEGRATION.md`](docs/FRONTEND_INTEGRATION.md)

---

## 📂 Project Structure

```
agentic-orchestration-app/
├── app/
│   ├── api/                # FastAPI routes & models
│   ├── agents/            # 5 specialized agents + router
│   ├── orchestration/     # StateGraph workflow + state management
│   ├── prompts/           # System prompts for each agent
│   └── config/            # Settings & LLM factory
├── data/
│   ├── documents/         # Personal documents (future RAG)
│   └── vector_stores/     # ChromaDB storage (future RAG)
├── docs/                  # 15+ comprehensive guides
├── scripts/               # Utility scripts
├── tests/                 # 89 passing tests
└── project_plan.md        # Complete implementation roadmap
```

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test suites
make test-state         # State management tests
make test-agents        # Agent tests
make test-router        # Router tests
make test-api          # API tests

# Check test coverage
pytest --cov=app tests/
```

**Current Status:** 89/89 tests passing ✅

---

## 📊 Implementation Progress

```
Phase 1: Project Setup              ████████████ 100% ✅
Phase 2: State Management           ████████████ 100% ✅
Phase 3: Specialized Agents         ████████████ 100% ✅
Phase 4: Router Implementation      ████████████ 100% ✅
Phase 5: LangGraph Orchestration    ████████████ 100% ✅
Phase 6: RAG System                 ░░░░░░░░░░░░   0% 🔄 Next
Phase 7: Persistence Layer          ░░░░░░░░░░░░   0%
Phase 8: Testing & Deployment       ░░░░░░░░░░░░   0%
```

**Overall:** 62.5% Complete

See [`project_plan.md`](project_plan.md) for detailed roadmap.

---

## 🔮 Coming Soon (Phase 6+)

**Phase 6 - RAG System:**
- Personal knowledge bases per agent
- Document ingestion pipeline
- Vector search with ChromaDB
- Personalized responses grounded in YOUR data

**Phase 7 - Persistence:**
- Conversation history storage
- Multi-session support
- User profiles

**Phase 8 - Production:**
- Authentication & authorization
- Rate limiting
- Monitoring & alerting
- Docker deployment

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [`project_plan.md`](project_plan.md) | Complete implementation roadmap |
| [`docs/FRONTEND_INTEGRATION.md`](docs/FRONTEND_INTEGRATION.md) | Frontend API guide |
| [`docs/STATEGRAPH_VISUALIZATION.md`](docs/STATEGRAPH_VISUALIZATION.md) | StateGraph architecture |
| [`docs/TESTING.md`](docs/TESTING.md) | Testing guide |
| [`docs/STATE_MANAGEMENT_GUIDE.md`](docs/STATE_MANAGEMENT_GUIDE.md) | State patterns & best practices |
| [`docs/PHASE4_ROUTER.md`](docs/PHASE4_ROUTER.md) | Router implementation details |

---

## 🛠️ Tech Stack

- **Python 3.11+** - Core language
- **LangChain** - LLM framework
- **LangGraph** - Agent orchestration
- **FastAPI** - Modern API framework
- **ChromaDB** - Vector database (Phase 6+)
- **OpenAI** - GPT-4o-mini & embeddings
- **Pydantic** - Data validation

---

## 💻 Development

### Using Makefile

```bash
make help           # Show all commands
make install        # Install dependencies
make run-local      # Run development server
make test           # Run all tests
make lint           # Run linters
make format         # Format code
```

### Manual Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/ tests/
isort app/ tests/
```

---

## 🔑 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | *Required* |
| `OPENAI_API_BASE` | OpenAI API endpoint | `https://api.openai.com/v1` |
| `DEFAULT_LLM_MODEL` | LLM model | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | Default temperature | `0.1` |
| `API_PORT` | Server port | `8000` |
| `VECTOR_STORE_TYPE` | Vector store | `chromadb` |

See [`.env.example`](.env.example) for all options.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)
- Powered by [OpenAI](https://openai.com/)
- API framework by [FastAPI](https://fastapi.tiangolo.com/)

---

## 📞 Support

- **Documentation:** [`docs/`](docs/)
- **Issues:** [GitHub Issues](https://github.com/Zaexv/agentic-orchestration-app/issues)
- **API Docs:** http://localhost:8000/docs (when running)

---

**Built with ❤️ for creating personalized AI digital twins**
