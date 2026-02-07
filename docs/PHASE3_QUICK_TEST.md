# 🧪 Phase 3 - Quick Testing Guide

## ✅ Phase 3 Complete!

**Implemented:** 5 specialized agents with keyword-based routing, LLM integration, and state management.

---

## �� Start Server

```bash
cd agent-orchestration-app
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🎯 Test Commands

### 1. General Agent
```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message":"Hello!","user_id":"eduardo"}'
```

### 2. Professional Agent  
```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message":"How do I debug Python code?","user_id":"eduardo"}'
```

### 3. Communication Agent
```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message":"Help me write a professional email","user_id":"eduardo"}'
```

### 4. Knowledge Agent
```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message":"What do I prefer for breakfast?","user_id":"eduardo"}'
```

### 5. Decision Agent
```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message":"Should I learn Rust or Go?","user_id":"eduardo"}'
```

---

## 📚 Full Guide

See `docs/PHASE3_TESTING_GUIDE.md` for comprehensive documentation with all details, troubleshooting, and examples.

---

**Phase 3 Status:** ✅ Complete - Ready for Phase 4!
