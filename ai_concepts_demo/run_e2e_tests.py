#!/usr/bin/env python3
"""E2E Test Runner script for AI Concepts Interactive Demo project."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(PROJECT_ROOT / "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


def main():
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
