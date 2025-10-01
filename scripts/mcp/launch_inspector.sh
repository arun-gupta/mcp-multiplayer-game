#!/bin/bash
# Launch MCP Inspector for different agents
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        print_info "Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null || true
        sleep 1
    fi
}

# Function to clean up MCP Inspector ports
cleanup_inspector_ports() {
    print_info "Cleaning up MCP Inspector ports..."
    kill_port 6274  # MCP Inspector GUI port
    kill_port 6277  # MCP Inspector proxy port
    
    # Kill any remaining inspector processes
    pkill -f "inspector" 2>/dev/null || true
    sleep 2
    print_success "Port cleanup complete"
}

# Check if backend is running
check_backend() {
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_error "Backend not running on localhost:8000"
        print_status "Please start the backend first:"
        echo "  cd /Users/arungupta/workspaces/mcp-multiplayer-game"
        echo "  source venv/bin/activate"
        echo "  python main.py"
        exit 1
    fi
    print_success "Backend is running"
}

# Show usage
show_usage() {
    echo "🔍 MCP Inspector Launcher"
    echo "========================="
    echo ""
    echo "Usage: $0 [agent] [mode] [--force]"
    echo ""
    echo "Agents:"
    echo "  scout      - Scout Agent (board analysis, threat detection)"
    echo "  strategist - Strategist Agent (strategy creation, move planning)"
    echo "  executor   - Executor Agent (move execution, validation)"
    echo ""
    echo "Modes:"
    echo "  gui        - Launch GUI inspector (default)"
    echo "  cli        - Launch CLI inspector"
    echo ""
    echo "Options:"
    echo "  --force    - Force kill existing processes and restart"
    echo ""
    echo "Examples:"
    echo "  $0 scout           # Launch GUI for Scout Agent"
    echo "  $0 strategist cli  # Launch CLI for Strategist Agent"
    echo "  $0 executor gui    # Launch GUI for Executor Agent"
    echo "  $0 scout gui --force  # Force restart with port cleanup"
    echo ""
    echo "Available MCP Endpoints:"
    echo "  http://localhost:8000/mcp/scout"
    echo "  http://localhost:8000/mcp/strategist"
    echo "  http://localhost:8000/mcp/executor"
}

# Main function
main() {
    # Check arguments
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi
    
    # Parse arguments
    AGENT=""
    MODE="gui"
    FORCE=false
    
    for arg in "$@"; do
        case $arg in
            --force)
                FORCE=true
                ;;
            scout|strategist|executor)
                AGENT=$arg
                ;;
            gui|cli)
                MODE=$arg
                ;;
        esac
    done
    
    # Validate agent
    case $AGENT in
        scout|strategist|executor)
            ;;
        *)
            print_error "Invalid agent: $AGENT"
            show_usage
            exit 1
            ;;
    esac
    
    # Validate mode
    case $MODE in
        gui|cli)
            ;;
        *)
            print_error "Invalid mode: $MODE"
            show_usage
            exit 1
            ;;
    esac
    
    # Check if backend is running
    check_backend
    
    # Clean up any existing MCP Inspector processes (always do this now)
    cleanup_inspector_ports
    
    # Set up environment
    cd /Users/arungupta/workspaces/mcp-multiplayer-game
    source venv/bin/activate
    
    # Launch inspector
    print_status "Launching MCP Inspector for $AGENT agent in $MODE mode..."
    print_status "Endpoint: http://localhost:8000/mcp/$AGENT"
    print_status "SSE Endpoint: http://localhost:8000/mcp/$AGENT/sse"
    
    if [ "$MODE" = "cli" ]; then
        print_status "Starting CLI inspector..."
        DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector --transport http --server-url "http://localhost:8000/mcp/$AGENT" --cli
    else
        print_status "Starting GUI inspector..."
        print_status "The inspector will open in your browser"
        print_status "Note: In the GUI, select 'Direct' connection type (not 'Via Proxy')"
        DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector --transport http --server-url "http://localhost:8000/mcp/$AGENT"
    fi
}

# Run main function with all arguments
main "$@"
