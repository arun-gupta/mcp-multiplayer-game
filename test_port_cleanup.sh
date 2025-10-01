#!/bin/bash
# Test port cleanup functionality

echo "🧪 Testing MCP Inspector Port Cleanup"
echo "====================================="

# Check if ports are in use
check_ports() {
    echo "📊 Checking port usage:"
    for port in 6274 6277; do
        pids=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pids" ]; then
            echo "  Port $port: IN USE (PIDs: $pids)"
        else
            echo "  Port $port: FREE"
        fi
    done
}

echo ""
echo "1. Initial port status:"
check_ports

echo ""
echo "2. Launching MCP Inspector..."
./launch_inspector.sh scout &
sleep 5

echo ""
echo "3. Port status after launch:"
check_ports

echo ""
echo "4. Testing port cleanup..."
./launch_inspector.sh scout
sleep 3

echo ""
echo "5. Final port status:"
check_ports

echo ""
echo "✅ Port cleanup test complete!"
