#!/usr/bin/env python3
"""
Basic test script for web framework functionality
"""
import requests
import time
import sys

def test_basic_functionality():
    """Test basic web framework functionality"""
    try:
        # Test if the server is running
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Basic web framework test passed")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing basic web framework functionality...")
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
