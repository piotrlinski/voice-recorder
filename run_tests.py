#!/usr/bin/env python3
"""
Test runner script for voice recorder application.
"""

import sys
import subprocess
import argparse


def run_tests(test_type="all", coverage=False, verbose=False):
    """Run tests with specified options."""
    cmd = ["python", "-m", "pytest"]
    
    if test_type == "unit":
        cmd.extend(["tests/unit/"])
    elif test_type == "integration":
        cmd.extend(["tests/integration/"])
    else:
        cmd.extend(["tests/"])
    
    if coverage:
        cmd.extend(["--cov=src/voice_recorder", "--cov-report=html", "--cov-report=term"])
    
    if verbose:
        cmd.append("-v")
    
    print(f"Running tests: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run voice recorder tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    exit_code = run_tests(args.type, args.coverage, args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 