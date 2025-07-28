#!/usr/bin/env python3
"""
Streamlit MCP Multiplayer Game Launcher

This script provides instructions for running the Streamlit version of the MCP multiplayer game.
"""

import subprocess
import sys
import time
import requests
import os

def check_api_server():
    """Check if the API server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("🎮 MCP Multiplayer Game - Streamlit Version")
    print("=" * 50)
    
    # Check if API server is running
    if not check_api_server():
        print("⚠️  API server is not running!")
        print("\n📋 Setup Instructions:")
        print("1. First, start the API server in one terminal:")
        print("   python main.py")
        print("\n2. Then, in another terminal, start the Streamlit app:")
        print("   streamlit run streamlit_app.py")
        print("\n3. Or install Streamlit dependencies first:")
        print("   pip install -r requirements_streamlit.txt")
        print("   streamlit run streamlit_app.py")
        
        # Ask if user wants to start the API server
        response = input("\nWould you like to start the API server now? (y/n): ")
        if response.lower() == 'y':
            print("\n🚀 Starting API server...")
            try:
                subprocess.Popen([sys.executable, "main.py"])
                print("✅ API server started!")
                print("⏳ Waiting for server to be ready...")
                
                # Wait for server to be ready
                for i in range(30):
                    if check_api_server():
                        print("✅ API server is ready!")
                        break
                    time.sleep(1)
                    print(f"⏳ Waiting... ({i+1}/30)")
                else:
                    print("❌ API server failed to start properly")
                    return
                    
            except Exception as e:
                print(f"❌ Error starting API server: {e}")
                return
        else:
            return
    
    # Start Streamlit
    print("\n🚀 Starting Streamlit application...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

if __name__ == "__main__":
    main() 