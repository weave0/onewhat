#!/usr/bin/env python3
"""Startup test script - verifies the API can start without loading models."""

import sys
import time
import subprocess
import requests

def test_startup():
    """Test that the API starts successfully."""
    print("🧪 Testing OneWhat API startup...")
    print("=" * 50)
    
    # Start uvicorn
    print("\n📡 Starting uvicorn...")
    proc = subprocess.Popen(
        [
            "uvicorn",
            "src.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--log-level", "info",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    
    # Wait for startup
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Test health endpoint
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            proc.terminate()
            return False
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        proc.terminate()
        return False
    
    # Test root endpoint
    print("\n🌐 Testing root endpoint...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint OK!")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Root endpoint error: {e}")
    
    # Test docs
    print("\n📚 Testing API docs...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs accessible!")
        else:
            print(f"❌ Docs failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Docs error: {e}")
    
    print("\n🎉 API startup test PASSED!")
    print("   Server is running on http://localhost:8000")
    print("   Press Ctrl+C to stop")
    
    # Keep running
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        proc.terminate()
        proc.wait()
        print("✅ Server stopped")
    
    return True

if __name__ == "__main__":
    success = test_startup()
    sys.exit(0 if success else 1)
