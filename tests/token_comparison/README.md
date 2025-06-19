📊 Shoe-Focused Token Testing
================================

## Updated Focus (June 19, 2025)
All test scenarios updated to focus on shoe-related queries since ShoesAgent is the only operational agent.

## Test Scenarios
1. **Shoe Shopping - General**: "I want to buy some shoes"
2. **Shoe Shopping - Running**: "find running shoes under $150"  
3. **Shoe Shopping - Work Boots**: "I need steel toe work boots"
4. **Shoe Shopping - Dress**: "formal dress shoes for wedding"
5. **Shoe Shopping - Size Check**: "check if Nike Air Max size 10 is available"
6. **Shoe Store Locator**: "find shoe stores near me"
7. **Shoe Buying Advice**: "what shoes are best for flat feet"
8. **Shoe Delivery Tracking**: "track my shoe order delivery"

## Quick Start
```bash
# Run comprehensive tests
./run_all_token_tests.sh

# View results
ls test_logs/
```

## Key Files Updated
- `test_detailed_workflows_with_logging.py` - Main test file
- `test_optimized_comparison.py` - Token optimization tests
- `generate_report.py` - Report generation
- `archive/test_simple.py` - Simple tests

## Expected Results
- ShoesAgent discovery with relevant tools
- ~913-4622 tokens depending on response mode
- 70-100ms response times
- 100% success rate for shoe queries

See `README_SHOE_FOCUSED.md` for complete documentation.