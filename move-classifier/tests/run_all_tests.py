#!/usr/bin/env python3
"""Master test runner - runs all tests in sequence."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess


def run_test_file(test_file: str) -> bool:
    """Run a single test file."""
    print(f"\n{'='*70}")
    print(f"Running {test_file}")
    print('='*70)
    
    test_path = Path(__file__).parent / test_file
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {test_file} PASSED")
            return True
        else:
            print(f"❌ {test_file} FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {test_file} TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {test_file} ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("CHESS MOVE CLASSIFIER - TEST SUITE")
    print("="*70)
    
    test_files = [
        "test_01_imports.py",
        "test_02_core_data_structures.py",
        "test_03_formulas.py",
        "test_04_classification_logic.py",
        "test_05_pgn_parsing.py",
        "test_06_documented_examples.py",
        "test_07_advanced_examples.py",
    ]
    
    results = {}
    
    for test_file in test_files:
        results[test_file] = run_test_file(test_file)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r)
    failed = len(results) - passed
    
    for test_file, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_file:45} {status}")
    
    print("="*70)
    print(f"TOTAL: {passed}/{len(results)} tests passed")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

