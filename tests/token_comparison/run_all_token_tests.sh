#!/bin/bash
# Comprehensive Token Consumption Test Runner
# Runs detailed workflow analysis with comprehensive logging by default
# Includes individual log files, complete HTTP capture, and structured JSON results

echo "🚀 KPATH Enterprise Comprehensive Token Analysis Suite"
echo "===================================================="
echo "Default: Enhanced analysis with detailed logging and HTTP capture"
echo "Use --simple flag for basic unified report only"
echo ""

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

echo "🔍 System Health Check..."
# Quick health check
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Error: KPATH API is not accessible at http://localhost:8000"
    echo "Please ensure the backend is running with: ./restart.sh"
    exit 1
fi

echo "✅ KPATH API is accessible"
echo ""

# Run the unified test suite
echo "🧪 Starting COMPREHENSIVE TOKEN ANALYSIS..."
echo ""
echo "Running enhanced analysis with:"
echo "  ✓ Detailed workflow step-by-step documentation"
echo "  ✓ Complete HTTP request/response capture"
echo "  ✓ Individual log files with full session tracking"
echo "  ✓ Structured JSON results for analysis"
echo "  ✓ Token breakdown for each operation"
echo "  ✓ Performance timing analysis"
echo "  ✓ Error handling with debugging context"
echo ""

# Check for legacy flag support (optional)
if [ "$1" = "--simple" ] || [ "$1" = "-s" ]; then
    echo "📊 Running SIMPLIFIED TOKEN TESTS (legacy mode)..."
    echo "This will run basic unified report only."
    echo ""
    
    python3 generate_unified_report.py
else
    echo "📝 Running COMPREHENSIVE ANALYSIS with detailed logging..."
    echo "This provides complete workflow documentation including:"
    echo "  • Full HTTP requests and responses"
    echo "  • Token breakdown for each step"
    echo "  • Workflow timing analysis"
    echo "  • Individual log file for each test session"
    echo "  • Structured JSON results for analysis"
    echo "  • Session-specific tracking and debugging"
    echo ""
    
    python3 test_detailed_workflows_with_logging.py
fi

echo ""
echo "✅ Comprehensive analysis completed!"
echo ""
echo "📁 Generated Files:"
if [ "$1" = "--simple" ] || [ "$1" = "-s" ]; then
    echo "   📊 test_reports/UNIFIED_TOKEN_ANALYSIS_REPORT.md - Complete analysis"
    echo "   📊 test_reports/agent_workflow_comparison_report.md - Agent workflow details"
    echo "   📊 Console output - Executive summary"
else
    echo "   📝 Session Logs: tests/token_comparison/test_logs/*.log"
    echo "   📊 JSON Results: tests/token_comparison/test_logs/*_results.json"
    echo "   📋 Console output - Executive summary with detailed metrics"
    echo ""
    echo "🔍 To view the latest detailed log:"
    echo "   tail -f tests/token_comparison/test_logs/$(ls -t tests/token_comparison/test_logs/*.log 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'latest.log')"
fi
echo ""
echo "🔍 Test Coverage:"
echo "   • PA Discovery: Traditional vs Direct Tool Search with full HTTP details"
echo "   • Agent Workflows: Standard vs Tool Search communication patterns"
echo "   • Complete token accounting from discovery to task completion"
echo "   • Step-by-step workflow analysis with precise timing"
echo "   • Production-ready optimization recommendations"
echo ""
echo "💡 Use these results to optimize your agent architecture and production deployments!"
