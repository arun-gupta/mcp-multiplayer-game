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

echo "🎮 MCP Multiplayer Game - MCP Protocol"
echo "======================================"
echo "🤖 CrewAI agents with MCP distributed communication"
echo ""
echo "🔍 MCP Inspector available:"
echo "   ./launch_inspector.sh scout        # GUI mode"
echo "   ./launch_inspector.sh strategist   # GUI mode"
echo "   ./launch_inspector.sh executor     # GUI mode"
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

# Function to load configuration
load_config() {
    # Load ports from config.json if it exists
    if [ -f "config.json" ]; then
        API_PORT=$(python -c "import json; print(json.load(open('config.json'))['api']['port'])" 2>/dev/null || echo "8000")
        STREAMLIT_PORT=$(python -c "import json; print(json.load(open('config.json'))['streamlit']['port'])" 2>/dev/null || echo "8501")
    elif [ -f "config.example.json" ]; then
        API_PORT=$(python -c "import json; print(json.load(open('config.example.json'))['api']['port'])" 2>/dev/null || echo "8000")
        STREAMLIT_PORT=$(python -c "import json; print(json.load(open('config.example.json'))['streamlit']['port'])" 2>/dev/null || echo "8501")
    else
        API_PORT=8000
        STREAMLIT_PORT=8501
    fi
    
    print_info "Using ports - API: $API_PORT, Streamlit: $STREAMLIT_PORT"
}

# Function to clean up existing processes
cleanup_processes() {
    print_info "Cleaning up existing processes..."
    
    # Load config to get ports
    load_config
    
    kill_port $API_PORT
    kill_port $STREAMLIT_PORT
    
    # Wait for processes to fully terminate
    print_info "Waiting for processes to terminate..."
    sleep 3
    
    # Verify ports are free
    print_info "Verifying ports are free..."
    if ! check_port $API_PORT || ! check_port $STREAMLIT_PORT; then
        print_error "Failed to free up ports. Please manually kill processes and try again."
        print_info "You can try: lsof -ti:$API_PORT,$STREAMLIT_PORT | xargs kill -9"
        exit 1
    fi
}

# Function to check API keys and environment setup
check_api_keys() {
    print_info "Checking API key configuration..."
    
    local has_openai_key=false
    local has_anthropic_key=false
    local has_ollama=false
    local missing_keys=()
    
    # Check for OpenAI API key
    if [ -n "$OPENAI_API_KEY" ]; then
        has_openai_key=true
        print_status "OpenAI API key found"
    else
        missing_keys+=("OpenAI")
        print_warning "OpenAI API key not found"
    fi
    
    # Check for Anthropic API key
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        has_anthropic_key=true
        print_status "Anthropic API key found"
    else
        missing_keys+=("Anthropic")
        print_warning "Anthropic API key not found"
    fi
    
    # Check for Ollama
    if command -v ollama &> /dev/null; then
        has_ollama=true
        print_status "Ollama found - local models available"
    else
        print_warning "Ollama not found - local models unavailable"
    fi
    
    # Determine available model types
    if [ "$has_openai_key" = true ] || [ "$has_anthropic_key" = true ]; then
        print_status "Cloud models will be available"
    else
        print_warning "No cloud models available (missing API keys)"
    fi
    
    if [ "$has_ollama" = true ]; then
        print_status "Local models will be available"
    else
        print_warning "No local models available (Ollama not installed)"
    fi
    
    # Check if any models are available
    if [ "$has_openai_key" = false ] && [ "$has_anthropic_key" = false ] && [ "$has_ollama" = false ]; then
        print_error "No models available! You need either:"
        print_info "1. API keys for cloud models (OpenAI/Anthropic), OR"
        print_info "2. Ollama installed with local models"
        echo ""
        
        # Interactive setup prompt
        if [ ${#missing_keys[@]} -gt 0 ] && [ -f ".env.example" ]; then
            echo ""
            print_info "🔧 Would you like to set up API keys now?"
            echo ""
            print_info "This will:"
            print_info "  1. Copy .env.example to .env"
            print_info "  2. Open .env in your default editor"
            print_info "  3. Wait for you to add your API keys"
            echo ""
            read -p "Set up API keys now? (y/n): " -n 1 -r
            echo ""
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                setup_env_file
                # Reload environment variables
                if [ -f ".env" ]; then
                    print_info "Reloading environment variables..."
                    set -a  # automatically export all variables
                    source .env
                    set +a
                    print_status "Environment variables reloaded"
                    
                    # Re-check API keys
                    return check_api_keys
                fi
            fi
        fi
        
        # Show setup instructions
        print_info "Setup instructions:"
        if [ ${#missing_keys[@]} -gt 0 ]; then
            print_info "• Create .env file with API keys:"
            print_info "  cp .env.example .env"
            print_info "  # Edit .env and add your API keys"
        fi
        if [ "$has_ollama" = false ]; then
            print_info "• Install Ollama: https://ollama.ai/"
            print_info "  ollama pull llama3.2:3b"
        fi
        echo ""
        
        # Ask if user wants to continue anyway
        print_warning "⚠️  Without models, the AI features won't work properly."
        echo ""
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Setup cancelled. Please set up models and try again."
            exit 1
        fi
        
        print_warning "Continuing with limited functionality..."
        return 1
    fi
    
    # Show setup recommendations for missing keys
    if [ ${#missing_keys[@]} -gt 0 ]; then
        echo ""
        print_info "💡 To enable cloud models, create .env file:"
        print_info "   cp .env.example .env"
        print_info "   # Edit .env and add your API keys"
        echo ""
    fi
    
    return 0
}

# Function to set up .env file interactively
setup_env_file() {
    print_info "Setting up .env file..."
    
    # Copy .env.example to .env
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Copied .env.example to .env"
    else
        print_error ".env.example not found!"
        return 1
    fi
    
    # Determine the best editor to use
    local editor=""
    if command -v code &> /dev/null; then
        editor="code"
    elif command -v nano &> /dev/null; then
        editor="nano"
    elif command -v vim &> /dev/null; then
        editor="vim"
    else
        print_warning "No suitable editor found. Please edit .env manually."
        print_info "Open .env in your preferred editor and add your API keys:"
        print_info "  OPENAI_API_KEY=your-key-here"
        print_info "  ANTHROPIC_API_KEY=your-key-here"
        return 0
    fi
    
    print_info "Opening .env in $editor..."
    print_info "Please add your API keys and save the file."
    echo ""
    print_info "Required keys:"
    print_info "  OPENAI_API_KEY=sk-proj-..."
    print_info "  ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
    print_info "Press Enter when you're ready to open the editor..."
    read -r
    
    # Open editor
    $editor .env
    
    print_info "Editor closed. Checking if API keys were added..."
    
    # Check if keys were added
    if grep -q "your-.*-api-key-here" .env; then
        print_warning "It looks like you still have placeholder values in .env"
        print_info "Please edit .env again and replace the placeholder values with your actual API keys."
        echo ""
        read -p "Open editor again? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            $editor .env
        fi
    fi
    
    print_status ".env setup completed"
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
    
    if [ ! -f ".env.example" ]; then
        print_error ".env.example not found!"
        print_info "This file is required for API key setup."
        exit 1
    fi
    
    print_status "All required files found"
    
    # Check API keys and model availability
    check_api_keys
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
    
    # Check if API is running (use configured port)
    if curl -s http://localhost:$API_PORT/health > /dev/null; then
        print_status "✅ MCP API is ready!"
        print_info "🎨 Starting MCP Streamlit UI..."
        streamlit run streamlit_app.py --server.port $STREAMLIT_PORT --server.address 0.0.0.0
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
                echo "MCP Multiplayer Game - MCP Protocol"
                echo "🤖 CrewAI agents with MCP distributed communication"
                echo ""
                echo "Options:"
                echo "  --skip-cleanup    Skip cleaning up existing processes"
                echo "  --skip-setup      Skip environment setup (assumes venv exists)"
                echo "  --help, -h        Show this help message"
                echo ""
                echo "API Key Setup:"
                echo "  The script will check for API keys and prompt you to set them up if missing."
                echo "  You can either:"
                echo "    1. Add API keys to .env file (recommended)"
                echo "    2. Install Ollama for local models"
                echo "    3. Continue with limited functionality"
                echo ""
                echo "Architecture:"
                echo "  MCP Protocol:    CrewAI agents with MCP distributed communication"
                echo "                   - Scout Agent (MCP Server on port 3001)"
                echo "                   - Strategist Agent (MCP Server on port 3002)"
                echo "                   - Executor Agent (MCP Server on port 3003)"
                echo "                   - FastAPI Coordinator (port 8000)"
                echo "                   - Streamlit UI (port 8501)"
                echo ""
                echo "Examples:"
                echo "  $0                # Full setup and launch MCP system"
                echo "  $0 --skip-setup   # Launch only (venv must exist)"
                echo "  $0 --skip-cleanup # Setup and launch without cleanup"
                echo ""
                echo "First Time Setup:"
                echo "  1. Run: $0"
                echo "  2. Follow prompts to set up API keys"
                echo "  3. Or install Ollama for local models"
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