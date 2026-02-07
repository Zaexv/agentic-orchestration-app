#!/bin/bash
# Verification script for OpenAI integration

echo "🔍 Verifying OpenAI Integration..."
echo ""

cd "$(dirname "$0")/.." || exit 1
source venv/bin/activate

echo "1️⃣ Testing LLM Configuration..."
python scripts/test_llm.py
if [ $? -eq 0 ]; then
    echo "✅ LLM test passed"
else
    echo "❌ LLM test failed"
    exit 1
fi

echo ""
echo "2️⃣ Testing API Health..."
response=$(curl -s http://localhost:8000/health)
if echo "$response" | grep -q "healthy"; then
    echo "✅ API health check passed"
    echo "$response" | python3 -m json.tool
else
    echo "❌ API health check failed"
    exit 1
fi

echo ""
echo "3️⃣ Testing Direct Invocation..."
python -c "from app.config.llm import get_llm; llm = get_llm(); print('✅ Direct invocation: ' + llm.invoke('Say OK').content)" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Direct invocation passed"
else
    echo "❌ Direct invocation failed"
    exit 1
fi

echo ""
echo "✅ All integration tests passed!"
echo ""
echo "Configuration:"
grep "OPENAI_API_BASE" .env
grep "DEFAULT_LLM_MODEL" .env
grep "LLM_TEMPERATURE" .env
