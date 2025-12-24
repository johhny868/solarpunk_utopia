#!/bin/bash
# Test Analysis Script
# Runs full test suite and generates a summary

echo "========================================="
echo "Running Full Test Suite"
echo "========================================="
echo ""

source venv/bin/activate

# Run tests with brief output
python -m pytest tests/ --tb=no -v 2>&1 | tee test_output_full.txt

echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo ""

# Extract summary
grep -E "(passed|failed|error)" test_output_full.txt | tail -5

echo ""
echo "Full output saved to: test_output_full.txt"
