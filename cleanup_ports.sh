#!/bin/bash
# Clean up MCP Inspector port conflicts

echo "🧹 Cleaning up MCP Inspector ports..."

# Kill processes on MCP Inspector ports
for port in 6274 6277; do
    pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "✅ Port $port is free"
    else
        echo "🔪 Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null || true
    fi
done

# Kill any remaining inspector processes
pkill -f "inspector" 2>/dev/null || true

echo "✅ Port cleanup complete!"
echo ""
echo "🚀 You can now launch MCP Inspector:"
echo "   ./launch_inspector.sh scout"
echo "   ./launch_inspector.sh strategist"
echo "   ./launch_inspector.sh executor"
