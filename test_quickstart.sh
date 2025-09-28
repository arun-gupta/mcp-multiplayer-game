#!/bin/bash

# Test script for quickstart.sh with MCP hybrid architecture
echo "🧪 Testing quickstart.sh with MCP hybrid architecture..."

# Test help
echo "Testing help option..."
./quickstart.sh --help

echo ""
echo "Testing MCP hybrid option..."
./quickstart.sh --mcp-hybrid --help

echo ""
echo "Testing original option..."
./quickstart.sh --original --help

echo ""
echo "✅ quickstart.sh tests completed!"
echo ""
echo "Usage examples:"
echo "  ./quickstart.sh                # Interactive architecture selection"
echo "  ./quickstart.sh --mcp-hybrid   # Force MCP Hybrid Architecture"
echo "  ./quickstart.sh --original     # Force Original Architecture"
echo "  ./quickstart.sh --skip-setup   # Launch only (venv must exist)"
