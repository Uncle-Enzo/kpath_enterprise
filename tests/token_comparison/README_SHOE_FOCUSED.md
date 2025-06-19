📊 KPATH Enterprise Token Comparison Tests - Shoe-Focused Edition
================================================================

## Overview
This directory contains comprehensive token usage testing focused on shoe-related scenarios, optimized for the ShoesAgent - the only real operational agent in the KPATH Enterprise system.

## Updated Test Focus (June 19, 2025)
All test scenarios have been updated to focus exclusively on shoe-related queries since the ShoesAgent is the only fully functional agent available. This provides more realistic and relevant testing.

## Test Scenarios

### 🥾 Shoe-Focused Test Scenarios
1. **Shoe Shopping - General**: "I want to buy some shoes"
2. **Shoe Shopping - Running**: "find running shoes under $150"  
3. **Shoe Shopping - Work Boots**: "I need steel toe work boots"
4. **Shoe Shopping - Dress**: "formal dress shoes for wedding"
5. **Shoe Shopping - Size Check**: "check if Nike Air Max size 10 is available"
6. **Shoe Store Locator**: "find shoe stores near me"
7. **Shoe Buying Advice**: "what shoes are best for flat feet"
8. **Shoe Delivery Tracking**: "track my shoe order delivery"

### Why Shoe-Only Testing?
- **ShoesAgent** (Service ID 93) is the only fully operational AI agent
- Has 5 specialized tools: product_search, product_availability, store_location_search, shoe_buying_guide, delivery_tracker
- Provides realistic test scenarios for actual system capabilities
- Eliminates false positives from non-existent services

## Test Files Updated

### Primary Test Files
- **`test_detailed_workflows_with_logging.py`** - Main comprehensive test with detailed logging
- **`test_detailed_workflows.py`** - Basic detailed workflow tests
- **`test_optimized_comparison.py`** - Token optimization comparison tests
- **`generate_report.py`** - Test report generation with scenarios

### Secondary Test Files  
- **`test_agent_to_agent_workflows.py`** - Already shoe-focused (no changes needed)
- **`archive/test_simple.py`** - Simple token comparison tests
- **`archive/visualize_results.py`** - Results visualization

## Expected Results

### ShoesAgent Tool Discovery
Each shoe-related query should return the ShoesAgent with relevant tools:

- **General Shopping** → product_search, shoe_buying_guide
- **Running Shoes** → product_search with athletic filter
- **Work Boots** → product_search with safety category
- **Size Check** → product_availability for specific items
- **Store Locator** → store_location_search
- **Buying Advice** → shoe_buying_guide for recommendations
- **Delivery Tracking** → delivery_tracker for orders

### Performance Expectations
- **Tools Minimal**: ~913 tokens (fastest, most efficient)
- **Tools Compact**: ~1,584 tokens (production balanced)  
- **Tools Full**: ~4,622 tokens (complete metadata)
- **Response Time**: 70-100ms for tools search modes

## Running the Tests

### Comprehensive Testing
```bash
# Run all tests with detailed logging (recommended)
./run_all_token_tests.sh

# Run individual test files
python test_detailed_workflows_with_logging.py
python test_optimized_comparison.py
python generate_report.py
```

### Quick Testing
```bash
# Simple token comparison
python archive/test_simple.py

# Visualization of results
python archive/visualize_results.py
```

## Test Output

### Log Files
- **`test_logs/*.log`** - Individual session logs with complete HTTP capture
- **`test_logs/*_results.json`** - Structured results for analysis
- **`test_reports/`** - Generated HTML and text reports

### Key Metrics Tracked
- **Token Usage**: Input, output, and total tokens per approach
- **Response Time**: API call timing and total workflow time
- **Success Rate**: Completion rate for each scenario
- **Tool Discovery**: Which tools are recommended for each query
- **Cost Analysis**: Estimated OpenAI API costs per approach

## Recent Changes (June 19, 2025)

### Files Modified
✅ **Updated all test scenarios** from generic business operations to shoe-specific queries
✅ **Maintained 8 diverse test scenarios** covering different shoe shopping needs
✅ **Preserved all testing infrastructure** - only scenarios changed
✅ **Updated visualization data** to reflect shoe-focused testing

### Benefits of Shoe-Only Testing
- **Realistic Results**: Tests actual available functionality
- **Accurate Metrics**: Token counts reflect real service responses
- **Better Insights**: Performance data relevant to production usage
- **Focused Analysis**: Clear understanding of ShoesAgent capabilities

## Usage Guidelines

### For Development
- Use these tests to optimize ShoesAgent performance
- Measure token usage for different query types
- Identify most efficient search approaches
- Validate new features against existing benchmarks

### For Production Planning
- **Recommended Mode**: `tools_only` with `response_mode: "minimal"`
- **Expected Performance**: 70-100ms response time, 900-1600 tokens
- **Cost Planning**: ~$0.009-0.016 per 1000 requests (GPT-4o pricing)
- **Scaling**: Tests provide baseline for load planning

## Test Results Location
- **Latest Results**: `test_logs/` directory
- **Session Logs**: Individual `.log` files with complete workflow documentation
- **JSON Data**: Structured results in `*_results.json` files
- **Reports**: HTML reports in `test_reports/` directory

---

**Last Updated**: June 19, 2025  
**Test Focus**: Shoe-related scenarios only  
**Target Agent**: ShoesAgent (Service ID 93)  
**Test Coverage**: 8 realistic shoe shopping scenarios