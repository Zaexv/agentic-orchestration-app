#!/bin/bash
# Setup Python 3.12 environment

set -e

echo "Setting up Python 3.12.8 environment..."

cd /Users/eduardo.pertierrapuche/Development/mw-randd/agent-orchestration-app

# Set Python version
echo "3.12.8" > .python-version

# Remove old venv
echo "Removing old venv..."
rm -rf venv

# Create new venv with Python 3.12.8
echo "Creating new venv with Python 3.12.8..."
~/.pyenv/versions/3.12.8/bin/python3 -m venv venv

# Upgrade pip
echo "Upgrading pip..."
./venv/bin/pip install --upgrade pip setuptools wheel -q

# Install dependencies
echo "Installing dependencies..."
./venv/bin/pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Python version in venv:"
./venv/bin/python --version
echo ""
echo "To activate the venv, run:"
echo "  source venv/bin/activate"
