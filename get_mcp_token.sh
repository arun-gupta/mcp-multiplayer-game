#!/bin/bash
# Get MCP Inspector session token

echo "🔑 Getting MCP Inspector Session Token"
echo "======================================"

# Kill any existing inspector processes
pkill -f "inspector" 2>/dev/null || true
sleep 2

# Launch MCP Inspector and capture the session token
echo "🚀 Launching MCP Inspector..."
DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector --transport http --server-url "http://localhost:8000/mcp/scout" 2>&1 | tee /tmp/mcp_inspector.log &
sleep 5

# Extract session token from logs
TOKEN=$(grep -o "MCP_PROXY_AUTH_TOKEN=[a-f0-9]*" /tmp/mcp_inspector.log | head -1 | cut -d'=' -f2)

if [ ! -z "$TOKEN" ]; then
    echo ""
    echo "✅ Session Token Found:"
    echo "   $TOKEN"
    echo ""
    echo "🔧 To use this token:"
    echo "   1. Open http://localhost:6274"
    echo "   2. Click 'Configuration' button"
    echo "   3. Add proxy session token: $TOKEN"
    echo "   4. Click Connect"
    echo ""
    echo "📋 Or use this URL directly:"
    echo "   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=$TOKEN"
else
    echo "❌ Could not find session token in logs"
    echo "📋 Check /tmp/mcp_inspector.log for details"
fi
