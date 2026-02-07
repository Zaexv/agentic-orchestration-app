#!/bin/bash
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🧪 Digital Twin AI - Testing All Agents               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

BASE_URL="http://localhost:8000/api/chat"

# Test General Agent
echo "1️⃣  General Agent (Miscellaneous queries):"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! How are you today?", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, reasoning: .routing_history[0].reasoning, response_preview: .response[:150]}'
echo ""

# Test Professional Agent
echo "2️⃣  Professional Agent (Technical queries):"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I implement error handling in Python code?", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, reasoning: .routing_history[0].reasoning, response_preview: .response[:150]}'
echo ""

# Test Communication Agent
echo "3️⃣  Communication Agent (Writing assistance):"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me write a professional email to decline a meeting", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, reasoning: .routing_history[0].reasoning, response_preview: .response[:150]}'
echo ""

# Test Knowledge Agent
echo "4️⃣  Knowledge Agent (Personal info):"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "What do I prefer for programming languages?", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, reasoning: .routing_history[0].reasoning, response_preview: .response[:150]}'
echo ""

# Test Decision Agent
echo "5️⃣  Decision Agent (Decision-making):"
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{"message": "Should I learn Rust or Go? Help me decide the pros and cons.", "user_id": "eduardo"}' \
  | jq '{agent: .agent_used, confidence: .confidence, reasoning: .routing_history[0].reasoning, response_preview: .response[:150]}'
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     ✅ All Agents Tested!                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Summary:"
echo "  ✅ General Agent - Fallback for misc queries"
echo "  ✅ Professional Agent - Technical expertise"
echo "  ✅ Communication Agent - Writing assistance"
echo "  ✅ Knowledge Agent - Personal knowledge"
echo "  ✅ Decision Agent - Decision-making"
echo ""
echo "📖 See full testing guide: docs/PHASE3_TESTING_GUIDE.md"
