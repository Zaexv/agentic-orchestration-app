#!/bin/bash
# Quick fix for langchain import error

echo "Installing missing langchain-text-splitters package..."

cd /Users/eduardo.pertierrapuche/Development/mw-randd/agent-orchestration-app

# Install the missing package
uv pip install langchain-text-splitters>=0.3.0

echo ""
echo "✅ Fix complete!"
echo ""
echo "Now try starting the server again:"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
