#!/usr/bin/env python
"""
Run tests with coverage and generate a report.
"""
import os
import sys
import subprocess

def run_coverage():
    """Run pytest with coverage and generate a report."""
    # Run pytest with coverage
    cmd = [
        "pytest",
        "--cov=app",
        "--cov-report=term",
        "--cov-report=html:coverage_html",
        "tests/"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the output
    print(result.stdout)
    
    if result.stderr:
        print("Errors:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
    
    # Return the exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_coverage())
