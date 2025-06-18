#!/bin/bash
# Test runner for token consumption comparison

echo "🚀 KPATH Enterprise Token Consumption Test Runner"
echo "================================================"

# Set up pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv init --path)"

# Activate the virtual environment
echo "⚠️  Activating torch-env virtual environment..."
pyenv activate torch-env

# Verify Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python not found in virtual environment"
    exit 1
fi

# Install required dependencies
echo "📦 Installing dependencies..."
python3 -m pip install tiktoken requests --quiet

# Navigate to test directory
cd /Users/james/claude_development/kpath_enterprise/tests/token_comparison

# Run the test
echo "🧪 Starting token consumption test..."
echo ""
python3 test_token_consumption_fixed.py

echo ""
echo "✅ Test completed!"
