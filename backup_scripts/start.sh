#!/bin/bash

# MCP Multiplayer Game - Start Script
# Kills existing processes and starts the application

echo "🎮 MCP Multiplayer Game - Starting Application"
echo "=============================================="

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "🛑 Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null
        sleep 2
    else
        echo "✅ Port $port is free"
    fi
}

# Function to check if a port is free
check_port() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        echo "❌ Port $port is still in use"
        return 1
    else
        echo "✅ Port $port is free"
        return 0
    fi
}

# Kill existing processes
echo ""
echo "🔧 Cleaning up existing processes..."
kill_port 8000
kill_port 8501

# Wait a bit longer for processes to fully terminate
echo ""
echo "⏳ Waiting for processes to terminate..."
sleep 3

# Verify ports are free
echo ""
echo "🔍 Verifying ports are free..."
if ! check_port 8000 || ! check_port 8501; then
    echo "❌ Failed to free up ports. Please manually kill processes and try again."
    echo "   You can try: lsof -ti:8000,8501 | xargs kill -9"
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo ""
    echo "⚠️  Virtual environment not detected!"
    echo "   Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

echo ""
echo "✅ Virtual environment is active: $VIRTUAL_ENV"

# Check if required files exist
echo ""
echo "🔍 Checking required files..."
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found!"
    exit 1
fi

if [ ! -f "streamlit_app.py" ]; then
    echo "❌ streamlit_app.py not found!"
    exit 1
fi

echo "✅ All required files found"

# Start the application using the Python launcher
echo ""
echo "🚀 Starting MCP Multiplayer Game..."
echo "=============================================="

# Use the Python launcher script
python run_app.py

echo ""
echo "👋 Application stopped" 