#!/bin/bash
# Test MCP Inspector without authentication

echo "🔓 Testing MCP Inspector with Authentication Disabled"
echo "=================================================="

# Kill any existing inspector processes
pkill -f "inspector" 2>/dev/null || true
sleep 2

echo "🚀 Launching MCP Inspector without authentication..."
DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector --transport sse --server-url "http://localhost:8000/mcp/scout/sse" &
sleep 5

echo "📊 Checking MCP Inspector status:"
if curl -s http://localhost:6274 > /dev/null; then
    echo "✅ MCP Inspector GUI: http://localhost:6274"
    echo "✅ Authentication: DISABLED"
    echo "✅ Connection: Should work without token issues"
else
    echo "❌ MCP Inspector not accessible"
fi

echo ""
echo "🎯 You can now access the MCP Inspector at:"
echo "   http://localhost:6274"
echo ""
echo "💡 No authentication token required!"
