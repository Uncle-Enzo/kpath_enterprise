#!/bin/bash
# Agent-to-Agent Workflow Test Runner

echo "🤖 KPATH Enterprise Agent-to-Agent Workflow Token Test"
echo "====================================================="

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

# Run the agent workflow test
echo "🧪 Starting agent-to-agent workflow token consumption test..."
echo ""
python3 test_agent_to_agent_workflows.py

echo ""
echo "✅ Agent workflow test completed!"
echo ""
echo "📊 Reports generated:"
echo "   • agent_workflow_comparison_report.md - Detailed analysis"
echo "   • Console output - Summary statistics"
echo ""
echo "🔍 Key Metrics Measured:"
echo "   • Discovery phase tokens (KPATH API + reasoning)"
echo "   • Agent communication tokens (Agent 1 → Agent 2)"
echo "   • Agent execution tokens (Agent 2 task processing)"
echo "   • Agent response tokens (Agent 2 → Agent 1)"
echo "   • Final processing tokens (Agent 1 completion)"
echo "   • Total workflow tokens (complete end-to-end)"
