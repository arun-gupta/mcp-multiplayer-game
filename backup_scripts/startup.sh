#!/bin/bash

# MCP Multiplayer Game - Complete Startup Script
echo "🎮 MCP Multiplayer Game - Complete Startup"
echo "=================================================="

# Function to check if virtual environment exists
check_venv() {
    if [ -d "venv" ]; then
        echo "✅ Virtual environment found"
        return 0
    else
        echo "❌ Virtual environment not found"
        return 1
    fi
}

# Function to create virtual environment and install dependencies
setup_environment() {
    echo "🔧 Setting up virtual environment..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 0 ]]; then
        echo "❌ Python 3.11+ is required. Current version: $python_version"
        exit 1
    fi
    echo "✅ Python version $python_version is compatible"
    
    # Create virtual environment
    echo "🔄 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
    
    # Activate virtual environment
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo "🔄 Installing Python dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
    
    # Check for Ollama (optional)
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama found - installing models..."
        ollama pull mistral 2>/dev/null || echo "⚠️  Failed to pull mistral model"
        ollama pull llama2:7b 2>/dev/null || echo "⚠️  Failed to pull llama2:7b model"
    else
        echo "⚠️  Ollama not found - local models won't be available"
        echo "   Install from: https://ollama.ai/"
    fi
    
    echo "✅ Environment setup completed!"
}

# Function to start the application
start_app() {
    echo "🚀 Starting MCP Multiplayer Game..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if required files exist
    if [ ! -f "main.py" ]; then
        echo "❌ main.py not found!"
        exit 1
    fi
    
    if [ ! -f "streamlit_app.py" ]; then
        echo "❌ streamlit_app.py not found!"
        exit 1
    fi
    
    # Start the application using the existing launcher
    python run_app.py
}

# Main execution
main() {
    # Check if virtual environment exists
    if ! check_venv; then
        echo "🔄 Virtual environment not found. Setting up..."
        setup_environment
    else
        echo "✅ Using existing virtual environment"
    fi
    
    # Start the application
    start_app
}

# Run main function
main 