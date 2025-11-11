# Debug Instructions for Mismatch Tests

## Overview

The `test_mismatch_debug.py` file contains unit tests for the 9 mismatched moves when using `multi_pv=2` and `depth=16`. Each test provides detailed debug output showing exactly what values are being used in the classification calculation.

## Prerequisites

```bash
# Make sure you're in the move-classifier directory
cd /Users/kiran/Desktop/code/playground/pgn-analyzeV2/move-classifier

# Activate virtual environment
source ../venv/bin/activate

# Install pytest if not already installed
pip install pytest
```

## Running Tests

### 1. Run All Tests (Shows Debug Output)

```bash
python tests/test_mismatch_debug.py
```

This will run all 9 mismatch tests sequentially and show detailed debug output for each.

### 2. Run With Pytest (Verbose)

```bash
python -m pytest tests/test_mismatch_debug.py -v -s
```

- `-v`: Verbose mode (shows each test name)
- `-s`: Don't capture output (shows all print statements)

### 3. Run a Single Test

```bash
python -m pytest tests/test_mismatch_debug.py::test_move_6_bg4 -v -s
```

Available test functions:
- `test_move_6_bg4` - Move 6: Bg4 (mistake vs excellent/okay)
- `test_move_7_dxe5` - Move 7: dxe5 (mistake vs best/excellent)
- `test_move_8_bxf3` - Move 8: Bxf3 (blunder vs best)
- `test_move_12_nf6` - Move 12: Nf6 (blunder vs best/excellent)
- `test_move_17_bg5` - Move 17: Bg5 (best vs critical)
- `test_move_18_b5` - Move 18: b5 (blunder vs inaccuracy)
- `test_move_20_cxb5` - Move 20: cxb5 (blunder vs okay/inaccuracy)
- `test_move_21_bxb5_check` - Move 21: Bxb5+ (best vs critical)
- `test_move_28_qe6` - Move 28: Qe6 (blunder vs inaccuracy/okay)

### 4. Run in Debug Mode (Interactive Debugger)

```bash
python -m pytest tests/test_mismatch_debug.py::test_move_6_bg4 -v -s --pdb
```

The `--pdb` flag will drop you into the Python debugger when an assertion fails or an exception occurs.

**Useful pdb commands:**
- `l` (list) - Show current code location
- `n` (next) - Execute next line
- `s` (step) - Step into function
- `c` (continue) - Continue execution
- `p variable_name` - Print variable value
- `pp variable_name` - Pretty-print variable
- `q` (quit) - Exit debugger

### 5. Debug with VS Code

1. Open VS Code in the move-classifier directory
2. Set breakpoints in `test_mismatch_debug.py` or `src/classification/point_loss.py`
3. Use the "Run and Debug" panel
4. Create a launch configuration:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Mismatch Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "tests/test_mismatch_debug.py::test_move_6_bg4",
                "-v",
                "-s"
            ],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

5. Run the configuration and step through the code

### 6. Debug with PyCharm

1. Open the project in PyCharm
2. Right-click on `test_mismatch_debug.py`
3. Select "Debug 'test_mismatch_debug'"
4. Or right-click on a specific test function and select "Debug"

## Understanding the Debug Output

Each test outputs the following sections:

### 1. Engine Analysis
```
Analyzing parent position: [FEN]
Found 2 engine lines
  Line 1: Nf6 eval=centipawn:48
  Line 2: Bg4 eval=centipawn:35
```

### 2. Extracted Node Data
```
PREVIOUS NODE (before move):
  Player color: BLACK
  Top line eval: centipawn:-48
  Subjective eval: centipawn:48
  Top move: Nf6
  Played move: Bg4
  Played move eval: FOUND/NOT FOUND in multi-PV
```

### 3. Point Loss Calculation
```
Using SAME-POSITION comparison (move found in multi-PV):
  eval_before (top move): centipawn:48
  eval_after (played move): centipawn:35
  EP(top move): 0.5581
  EP(played move): 0.5413
  Point loss: 0.0168 (1.68%)
```

OR

```
Using FALLBACK comparison (move NOT in multi-PV):
  eval_before (raw): centipawn:-48
  eval_after (raw): centipawn:110
  EP(before): 0.4581
  EP(after): 0.5951
  (EP_before - EP_after) * -1 = 0.1370
  Point loss (after max): 0.1370 (13.70%)
```

### 4. Result
```
RESULT:
  Classification: mistake
  Accuracy: 86.30%
  Expected: excellent/okay
  Match: ✗
```

## What to Look For

### For Moves NOT in Multi-PV (Fallback Logic)

1. **Check if played move appears in multi-PV lines**
   - Look for "Played move eval: NOT FOUND in multi-PV"
   - These use the fallback comparison

2. **Verify the fallback calculation**
   - Are the raw evaluations correct?
   - Is the color multiplier applied correctly?
   - Does the point loss match JavaScript's expected behavior?

3. **Compare with JavaScript output**
   - Check if the engine evaluations match what JavaScript gets
   - Small differences in evaluations can cause classification differences

### For CRITICAL Classification Issues (Moves 17, 21)

1. **Check second-best move**
   - Is there a second line in multi-PV?
   - What's the evaluation gap between first and second?

2. **Verify CRITICAL conditions**
   - Is the move the top move? (should be)
   - Is second-best move losing ≥10% expected points?
   - Check `src/classification/critical.py` logic

## Troubleshooting

### Test fails with "Stockfish not found"
```bash
# Update the stockfish_path in the test
# Edit line in test_mismatch_debug.py:
stockfish_path = "/path/to/your/stockfish"
```

### Import errors
```bash
# Make sure you're in the move-classifier directory
cd /Users/kiran/Desktop/code/playground/pgn-analyzeV2/move-classifier

# Activate venv
source ../venv/bin/activate

# Run from correct directory
python tests/test_mismatch_debug.py
```

### Want more detailed output?
Add more print statements in the test or in `src/classification/point_loss.py`:

```python
print(f"DEBUG: eval_before = {eval_before}")
print(f"DEBUG: eval_after = {eval_after}")
print(f"DEBUG: point_loss = {point_loss}")
```

## Next Steps

After running the tests and examining the output:

1. **Identify patterns** - Are all mismatches using fallback logic?
2. **Compare engine evals** - Do they match JavaScript's engine output?
3. **Check thresholds** - Are classifications mapping to correct buckets?
4. **Verify perspective handling** - Are subjective evaluations calculated correctly?

## Example Debug Session

```bash
# 1. Run a single test
cd /Users/kiran/Desktop/code/playground/pgn-analyzeV2/move-classifier
source ../venv/bin/activate
python -m pytest tests/test_mismatch_debug.py::test_move_6_bg4 -v -s

# 2. Observe the output - look for:
#    - Is Bg4 in the multi-PV lines?
#    - What's the point loss calculation?
#    - Why is it "mistake" instead of "excellent/okay"?

# 3. Run with debugger to step through
python -m pytest tests/test_mismatch_debug.py::test_move_6_bg4 -v -s --pdb

# 4. In pdb, examine variables:
(Pdb) p previous.played_move_evaluation
(Pdb) p ep_before
(Pdb) p point_loss
```

