"""
MCP Streamlit Launcher
Launches the MCP Streamlit app with proper configuration
"""
import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def check_mcp_api():
    """Check if MCP API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_mcp_api():
    """Start the MCP API server"""
    print("🚀 Starting MCP API server...")
    try:
        # Start the MCP API server in the background
        process = subprocess.Popen([
            sys.executable, "main_mcp.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for API to be ready
        print("⏳ Waiting for MCP API to start...")
        for i in range(30):  # Wait up to 30 seconds
            if check_mcp_api():
                print("✅ MCP API is ready!")
                return process
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ MCP API failed to start")
        return None
        
    except Exception as e:
        print(f"❌ Error starting MCP API: {e}")
        return None

def start_streamlit():
    """Start the Streamlit app"""
    print("🎨 Starting MCP Streamlit app...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--theme.base", "dark"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def main():
    """Main launcher function"""
    print("🤖 MCP CrewAI Tic Tac Toe Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main_mcp.py").exists():
        print("❌ main_mcp.py not found. Please run from the project root directory.")
        sys.exit(1)
    
    # Check if MCP API is already running
    if check_mcp_api():
        print("✅ MCP API is already running!")
    else:
        # Start MCP API
        api_process = start_mcp_api()
        if not api_process:
            print("❌ Failed to start MCP API. Please check the logs.")
            sys.exit(1)
    
    # Start Streamlit
    try:
        start_streamlit()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
