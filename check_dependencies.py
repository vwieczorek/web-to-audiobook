#!/usr/bin/env python3
"""
Check if all required dependencies are installed.
"""

import importlib.util
import sys


def check_module(module_name):
    """Check if a module is installed."""
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ {module_name} is NOT installed")
        return False
    else:
        print(f"✅ {module_name} is installed")
        return True


def main():
    """Check all required dependencies."""
    required_modules = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic_settings",
        "dotenv",
        "httpx",
    ]
    
    all_installed = True
    for module in required_modules:
        if not check_module(module):
            all_installed = False
    
    if all_installed:
        print("\nAll required dependencies are installed! 🎉")
    else:
        print("\nSome dependencies are missing. Please install them with:")
        print("pip install -r requirements.txt")
        print("or")
        print("pip install fastapi uvicorn pydantic pydantic-settings python-dotenv httpx")
    
    return 0 if all_installed else 1


if __name__ == "__main__":
    sys.exit(main())
