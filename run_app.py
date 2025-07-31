#!/usr/bin/env python3
"""
Launcher script for MCP Multiplayer Game
Starts both the FastAPI backend and Streamlit frontend
"""
import subprocess
import time
import sys
import os
import signal
import threading
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    try:
        # Start the backend server
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server started successfully
        if backend_process.poll() is None:
            print("✅ Backend server started successfully!")
            print("📍 Backend URL: http://localhost:8000")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend server: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎮 Starting Streamlit frontend...")
    try:
        # Start the Streamlit app
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for app to start
        time.sleep(5)
        
        # Check if app started successfully
        if frontend_process.poll() is None:
            print("✅ Streamlit frontend started successfully!")
            print("📍 Frontend URL: http://localhost:8501")
            return frontend_process
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"❌ Frontend failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ main.py not found!")
        return False
    
    # Check if streamlit_app.py exists
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found!")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected. Make sure to activate your virtual environment first!")
        print("   Run: source venv/bin/activate")
    
    print("✅ Dependencies check passed!")
    return True

def main():
    """Main launcher function"""
    print("🎮 MCP Multiplayer Game Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend. Exiting...")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend. Stopping backend...")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Both servers started successfully!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:8501")
    print("🔧 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print("Press Ctrl+C to stop both servers")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                # Check if backend is actually down by testing the health endpoint
                import requests
                try:
                    response = requests.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        print("🔄 Backend server auto-reloaded (normal behavior)")
                        # Continue monitoring - server is still running
                        continue
                    else:
                        print("❌ Backend server stopped unexpectedly")
                        break
                except requests.exceptions.RequestException:
                    print("❌ Backend server stopped unexpectedly")
                    break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        
        # Stop backend
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            print("✅ Backend server stopped")
        
        # Stop frontend
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 