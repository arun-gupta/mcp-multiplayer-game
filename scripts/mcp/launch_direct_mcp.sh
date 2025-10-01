#!/bin/bash
# Launch MCP Inspector with direct connection (no proxy)

echo "🔗 Launching MCP Inspector with Direct Connection"
echo "================================================"

# Kill any existing inspector processes
pkill -f "inspector" 2>/dev/null || true
sleep 2

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend not running. Please start it first:"
    echo "   cd /Users/arungupta/workspaces/mcp-multiplayer-game"
    echo "   source venv/bin/activate"
    echo "   python main.py"
    exit 1
fi

echo "✅ Backend is running"

# Launch MCP Inspector with direct connection
echo "🚀 Starting MCP Inspector with direct connection..."
echo ""
echo "📋 IMPORTANT: In the MCP Inspector GUI:"
echo "   1. Transport Type: Streamable HTTP"
echo "   2. URL: http://localhost:8000/mcp/scout"
echo "   3. Connection Type: Direct (NOT Via Proxy)"
echo "   4. Click Connect"
echo ""

DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector --transport http --server-url "http://localhost:8000/mcp/scout"
