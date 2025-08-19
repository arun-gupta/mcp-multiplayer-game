#!/bin/bash

# Docker Run Script for MCP Multiplayer Game
# This script demonstrates different ways to handle API keys

set -e

echo "🐳 MCP Multiplayer Game - Docker Runner"
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env.example template..."
    cat > .env.example << EOF
# API Keys for LLM Providers
# Copy this file to .env and fill in your actual API keys

# OpenAI API Key (Required for Scout Agent)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API Key (Required for Strategist Agent)  
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: Custom port for the application
PORT=8000

# Optional: Environment (development, production, staging)
ENVIRONMENT=development
EOF
    echo "📋 Please create a .env file with your API keys:"
    echo "   cp .env.example .env"
    echo "   # Then edit .env with your actual API keys"
    exit 1
fi

# Load environment variables
source .env

# Check if API keys are set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo "❌ OPENAI_API_KEY not set in .env file"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your-anthropic-api-key-here" ]; then
    echo "❌ ANTHROPIC_API_KEY not set in .env file"
    exit 1
fi

echo "✅ API keys found in .env file"

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t mcp-multiplayer-game .

# Run the container
echo "🚀 Starting container..."
echo "🌐 Application will be available at:"
echo "   - Backend API: http://localhost:8000"
echo "   - Frontend UI: http://localhost:8501"
echo "   - API Docs: http://localhost:8000/docs"
echo ""

# Method 1: Using environment variables from .env file
docker run -d \
    --name mcp-game \
    --env-file .env \
    -p 8000:8000 \
    -p 8501:8501 \
    --restart unless-stopped \
    mcp-multiplayer-game

echo "✅ Container started successfully!"
echo ""
echo "📊 Container status:"
docker ps --filter "name=mcp-game"

echo ""
echo "🔍 To view logs:"
echo "   docker logs -f mcp-game"
echo ""
echo "🛑 To stop:"
echo "   docker stop mcp-game"
echo ""
echo "🗑️  To remove:"
echo "   docker rm mcp-game"
