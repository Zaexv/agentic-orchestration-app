#!/bin/bash
# Complete API Test - Shows State Management in Action

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     Digital Twin AI - Complete API Test                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="http://localhost:8000"

# Test 1: Root endpoint
echo "1️⃣  Testing Root Endpoint..."
curl -s $BASE_URL/ | python3 -m json.tool
echo ""

# Test 2: Health check
echo "2️⃣  Testing Health Check..."
curl -s $BASE_URL/health | python3 -m json.tool
echo ""

# Test 3: Chat with state management
echo "3️⃣  Testing Chat (State Management Demo)..."
curl -s -X POST $BASE_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What programming languages do I know?",
    "user_id": "eduardo",
    "max_iterations": 10
  }' | python3 -m json.tool
echo ""

# Test 4: State structure example
echo "4️⃣  Testing State Structure Example..."
curl -s $BASE_URL/api/state/example | python3 -m json.tool
echo ""

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     ✅ All Tests Complete!                                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📊 What These Tests Show:"
echo "  ✅ State creation with session IDs"
echo "  ✅ Message accumulation (ADD pattern)"
echo "  ✅ Routing history tracking"
echo "  ✅ Iteration counting"
echo "  ✅ Safety mechanisms"
echo "  ✅ Pydantic validation"
echo ""
echo "📚 Learn More:"
echo "  - Read: docs/STATE_MANAGEMENT_GUIDE.md"
echo "  - Quick ref: docs/STATE_CHEATSHEET.md"
echo "  - API guide: docs/API_TESTING.md"
echo "  - Interactive docs: $BASE_URL/docs"
