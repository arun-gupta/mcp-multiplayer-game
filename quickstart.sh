#!/bin/bash

# MCP Multiplayer Game - MCP Hybrid Architecture Launcher
# CrewAI + MCP hybrid agents with distributed communication

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

echo "🎮 MCP Multiplayer Game - MCP Hybrid Architecture"
echo "================================================"
echo "🤖 CrewAI + MCP hybrid agents with distributed communication"
echo ""

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        print_info "Killing processes on port $port: $pids"
        kill -9 $pids 2>/dev/null || true
        sleep 2
    else
        print_status "Port $port is free"
    fi
}

# Function to check if a port is free
check_port() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        print_error "Port $port is still in use"
        return 1
    else
        print_status "Port $port is free"
        return 0
    fi
}

# Function to check if virtual environment exists
check_venv() {
    if [ -d "venv" ]; then
        print_status "Virtual environment found"
        return 0
    else
        print_warning "Virtual environment not found"
        return 1
    fi
}

# Function to create virtual environment and install dependencies
setup_environment() {
    print_info "Setting up virtual environment..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    if [[ $(echo "$python_version >= 3.11" | bc -l 2>/dev/null || echo "0") -eq 0 ]]; then
        print_error "Python 3.11+ is required. Current version: $python_version"
        exit 1
    fi
    print_status "Python version $python_version is compatible"
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_status "Virtual environment created"
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip and install dependencies
    print_info "Installing Python dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install dependencies"
        exit 1
    fi
    print_status "Dependencies installed"
    
    # Install additional dependencies that might be missing
    print_info "Installing additional dependencies..."
    pip install psutil streamlit
    
    # Check for Ollama (optional)
    if command -v ollama &> /dev/null; then
        print_status "Ollama found - installing models..."
        ollama pull mistral 2>/dev/null || print_warning "Failed to pull mistral model"
        ollama pull llama2:7b 2>/dev/null || print_warning "Failed to pull llama2:7b model"
    else
        print_warning "Ollama not found - local models won't be available"
        print_info "Install from: https://ollama.ai/"
    fi
    
    print_status "Environment setup completed!"
}

# Function to clean up existing processes
cleanup_processes() {
    print_info "Cleaning up existing processes..."
    kill_port 8000
    kill_port 8501
    
    # Wait for processes to fully terminate
    print_info "Waiting for processes to terminate..."
    sleep 3
    
    # Verify ports are free
    print_info "Verifying ports are free..."
    if ! check_port 8000 || ! check_port 8501; then
        print_error "Failed to free up ports. Please manually kill processes and try again."
        print_info "You can try: lsof -ti:8000,8501 | xargs kill -9"
        exit 1
    fi
}

# Function to validate environment
validate_environment() {
    # Check if virtual environment is activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Virtual environment not detected!"
        print_info "Please activate your virtual environment first:"
        print_info "source venv/bin/activate"
        exit 1
    fi
    
    print_status "Virtual environment is active: $VIRTUAL_ENV"
    
    # Check if required files exist
    print_info "Checking required files..."
    if [ ! -f "main.py" ]; then
        print_error "main.py not found!"
        exit 1
    fi
    
    if [ ! -f "streamlit_app.py" ]; then
        print_error "streamlit_app.py not found!"
        exit 1
    fi
    
    if [ ! -f "run_streamlit.py" ]; then
        print_error "run_streamlit.py not found!"
        exit 1
    fi
    
    print_status "All required MCP hybrid files found"
}

# Function to start the MCP application
start_application() {
    print_info "🚀 Starting MCP Hybrid Architecture..."
    echo "=========================================="
    print_info "🤖 CrewAI + MCP hybrid agents with distributed communication"
    echo ""
    
    print_info "🚀 Starting MCP API server..."
    python main.py &
    API_PID=$!
    
    # Wait for API to start
    print_info "⏳ Waiting for MCP API to start..."
    sleep 5
    
    # Check if API is running
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "✅ MCP API is ready!"
        print_info "🎨 Starting MCP Streamlit UI..."
        python run_streamlit.py
    else
        print_error "❌ MCP API failed to start"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
}

# Main execution function
main() {
    # Parse command line arguments
    SKIP_CLEANUP=false
    SKIP_SETUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-cleanup)
                SKIP_CLEANUP=true
                shift
                ;;
            --skip-setup)
                SKIP_SETUP=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "MCP Multiplayer Game - MCP Hybrid Architecture"
                echo "🤖 CrewAI + MCP hybrid agents with distributed communication"
                echo ""
                echo "Options:"
                echo "  --skip-cleanup    Skip cleaning up existing processes"
                echo "  --skip-setup      Skip environment setup (assumes venv exists)"
                echo "  --help, -h        Show this help message"
                echo ""
                echo "Architecture:"
                echo "  MCP Hybrid:      CrewAI + MCP hybrid agents with distributed communication"
                echo "                   - Scout Agent (MCP Server on port 3001)"
                echo "                   - Strategist Agent (MCP Server on port 3002)"
                echo "                   - Executor Agent (MCP Server on port 3003)"
                echo "                   - FastAPI Coordinator (port 8000)"
                echo "                   - Streamlit UI (port 8501)"
                echo ""
                echo "Examples:"
                echo "  $0                # Full setup and launch MCP hybrid system"
                echo "  $0 --skip-setup   # Launch only (venv must exist)"
                echo "  $0 --skip-cleanup # Setup and launch without cleanup"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                print_info "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Clean up existing processes (unless skipped)
    if [ "$SKIP_CLEANUP" = false ]; then
        cleanup_processes
    else
        print_warning "Skipping process cleanup"
    fi
    
    # Setup environment (unless skipped)
    if [ "$SKIP_SETUP" = false ]; then
        if ! check_venv; then
            print_info "Virtual environment not found. Setting up..."
            setup_environment
        else
            print_status "Using existing virtual environment"
            # Activate existing virtual environment
            print_info "Activating existing virtual environment..."
            source venv/bin/activate
        fi
    else
        print_warning "Skipping environment setup"
        # Still need to activate virtual environment if it exists
        if [ -d "venv" ]; then
            print_info "Activating existing virtual environment..."
            source venv/bin/activate
        fi
    fi
    
    # Validate environment
    validate_environment
    
    # Start the application
    start_application
}

# Handle script interruption
trap 'echo ""; print_warning "Interrupted by user"; exit 1' INT

# Run main function
main "$@"