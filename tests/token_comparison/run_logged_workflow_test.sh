#!/bin/bash

# Enhanced Token Analysis Test Runner with Comprehensive Logging
# Executes detailed workflow analysis with individual log files for each test run

echo "🚀 KPATH Enterprise - Enhanced Token Usage Analysis with Logging"
echo "=============================================================="
echo "Date: $(date)"
echo "Environment: pyenv torch-env"
echo ""

# Check if we're in the right directory
if [ ! -f "tests/token_comparison/test_detailed_workflows_with_logging.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating pyenv torch-env..."
eval "$(pyenv init -)"
pyenv activate torch-env

# Check API connectivity
echo "🔗 Checking KPATH API connectivity..."
curl -s http://localhost:8000/health > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ KPATH API is not running. Please start the backend first."
    echo "   Run: ./restart.sh"
    exit 1
fi
echo "✅ KPATH API is accessible"

# Install required packages if needed
echo "📦 Checking dependencies..."
python3 -c "import tiktoken, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "🔄 Installing required packages..."
    pip install tiktoken requests
fi

# Create logs directory if it doesn't exist
mkdir -p tests/token_comparison/test_logs

echo ""
echo "📝 ENHANCED LOGGING FEATURES:"
echo "  ✓ Individual log file for each test session"
echo "  ✓ Complete HTTP request/response capture"
echo "  ✓ Step-by-step token breakdown logging"
echo "  ✓ Detailed error tracking and debugging"
echo "  ✓ Structured JSON results for analysis"
echo "  ✓ Session-specific unique identifiers"
echo ""
echo "🧪 Starting Enhanced Workflow Analysis Tests..."
echo "This will test multiple approaches with comprehensive logging:"
echo "  • Traditional (agents_only) workflow"
echo "  • Tools Full workflow with complete metadata"
echo "  • Tools Compact workflow (optimized)"
echo "  • Tools Minimal workflow (ultra-optimized)"
echo ""
echo "Each test will generate:"
echo "  📝 Detailed log file with all operations"
echo "  📊 JSON results file for structured analysis"
echo "  🔍 Console output with key metrics"
echo ""

# Run the comprehensive test with logging
cd tests/token_comparison
python3 test_detailed_workflows_with_logging.py

# Check if test completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Enhanced workflow analysis with logging completed successfully!"
    echo ""
    echo "📁 Generated Files:"
    echo "  📝 Session Logs: tests/token_comparison/test_logs/*.log"
    echo "  📊 JSON Results: tests/token_comparison/test_logs/*_results.json"
    echo ""
    echo "🔍 To view the latest log:"
    echo "  tail -f tests/token_comparison/test_logs/$(ls -t tests/token_comparison/test_logs/*.log | head -1 | xargs basename)"
    echo ""
    echo "📊 Results include:"
    echo "  • Complete workflow documentation with HTTP details"
    echo "  • Token usage breakdown by step with precise counting"
    echo "  • Performance comparison analysis with timing"
    echo "  • Production recommendations based on efficiency"
    echo "  • Structured data for further analysis and automation"
    echo ""
    echo "💡 Use this data to:"
    echo "  • Understand exact token consumption patterns"
    echo "  • Optimize production implementations"
    echo "  • Validate API efficiency improvements"
    echo "  • Debug workflow issues with detailed logs"
    echo "  • Generate automated reports from JSON data"
else
    echo "❌ Test execution failed. Check the error messages above."
    echo "📝 Check the log files in tests/token_comparison/test_logs/ for details."
    exit 1
fi
