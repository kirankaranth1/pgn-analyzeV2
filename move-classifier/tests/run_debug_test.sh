#!/bin/bash

# Helper script to run debug tests easily
# Usage: ./tests/run_debug_test.sh [test_name]

cd "$(dirname "$0")/.."
source ../venv/bin/activate

if [ -z "$1" ]; then
    echo "Running ALL mismatch tests..."
    python tests/test_mismatch_debug.py
else
    echo "Running test: $1"
    python -m pytest "tests/test_mismatch_debug.py::$1" -v -s
fi

