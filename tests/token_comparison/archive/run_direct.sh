#!/bin/bash
# Direct run command for token consumption test

cd /Users/james/claude_development/kpath_enterprise
source ~/.pyenv/versions/torch-env/bin/activate
cd tests/token_comparison
python3 test_token_consumption_fixed.py
