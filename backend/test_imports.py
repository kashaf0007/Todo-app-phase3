#!/usr/bin/env python3
"""
Test script to check for import errors in the application
"""
import sys
import traceback

def test_imports():
    print("Testing imports...")
    
    try:
        print("Testing: from fastapi import FastAPI")
        from fastapi import FastAPI
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import FastAPI: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("Testing: from src.main import app")
        sys.path.insert(0, './')
        from src.main import app
        print("✓ Main app imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import main app: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ Error importing main app: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✓ All imports successful!")
    else:
        print("\n✗ Some imports failed!")
        sys.exit(1)