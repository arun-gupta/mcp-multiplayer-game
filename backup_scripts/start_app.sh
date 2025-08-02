#!/bin/bash

# MCP Multiplayer Game Launcher Script
echo "🎮 MCP Multiplayer Game Launcher"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup.py first to create the virtual environment."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found in virtual environment!"
    exit 1
fi

# Start the launcher script
echo "🚀 Starting MCP Multiplayer Game..."
python run_app.py 