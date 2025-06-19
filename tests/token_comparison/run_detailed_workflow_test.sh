#!/bin/bash

# Comprehensive Token Analysis Test Runner
# Executes detailed workflow analysis with full request/response documentation

echo "🚀 KPATH Enterprise - Comprehensive Token Usage Analysis"
echo "======================================================="
echo "Date: $(date)"
echo "Environment: pyenv torch-env"
echo ""

# Check if we're in the right directory
if [ ! -f "tests/token_comparison/test_detailed_workflows.py" ]; then
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

echo ""
echo "🧪 Starting Comprehensive Workflow Analysis Tests..."
echo "This will test multiple approaches with detailed step-by-step documentation:"
echo "  • Traditional (agents_only) workflow"
echo "  • Tools Full workflow with complete metadata"
echo "  • Tools Compact workflow (optimized)"
echo "  • Tools Minimal workflow (ultra-optimized)"
echo ""
echo "Each test will capture:"
echo "  ✓ Complete HTTP requests and responses"
echo "  ✓ Step-by-step token breakdown"
echo "  ✓ Timing analysis for each operation"
echo "  ✓ Success/failure status tracking"
echo "  ✓ Detailed workflow documentation"
echo ""

# Run the comprehensive test
cd tests/token_comparison
python3 test_detailed_workflows.py

# Check if test completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Comprehensive workflow analysis completed successfully!"
    echo ""
    echo "📊 Results include:"
    echo "  • Complete workflow documentation"
    echo "  • Token usage breakdown by step"
    echo "  • HTTP request/response details"
    echo "  • Performance comparison analysis"
    echo "  • Production recommendations"
    echo ""
    echo "💡 Use this data to:"
    echo "  • Understand exact token consumption patterns"
    echo "  • Optimize production implementations"
    echo "  • Validate API efficiency improvements"
    echo "  • Document complete system workflows"
else
    echo "❌ Test execution failed. Check the error messages above."
    exit 1
fi
