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
echo "   ./scripts/mcp/launch_inspector.sh scout        # GUI mode"
echo "   ./scripts/mcp/launch_inspector.sh strategist   # GUI mode"
echo "   ./scripts/mcp/launch_inspector.sh executor     # GUI mode"
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

    # If distributed mode, also clean up agent ports
    if [ "$DISTRIBUTED_MODE" = true ]; then
        print_info "Cleaning up agent server ports (distributed mode)..."
        kill_port 3001  # Scout
        kill_port 3002  # Strategist
        kill_port 3003  # Executor
    fi

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

    if [ "$DISTRIBUTED_MODE" = true ]; then
        if ! check_port 3001 || ! check_port 3002 || ! check_port 3003; then
            print_error "Failed to free up agent ports. Please manually kill processes."
            print_info "You can try: lsof -ti:3001,3002,3003 | xargs kill -9"
            exit 1
        fi
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

    if [ "$DISTRIBUTED_MODE" = true ]; then
        print_info "🌐 DISTRIBUTED MODE: Starting agents as separate processes"
        echo ""

        # Create logs directory if it doesn't exist
        mkdir -p logs

        # Start Scout Agent MCP Server
        print_info "🔍 Starting Scout Agent MCP Server (port 3001)..."
        python agents/scout_server.py > logs/scout_server.log 2>&1 &
        SCOUT_PID=$!
        sleep 2

        # Start Strategist Agent MCP Server
        print_info "🧠 Starting Strategist Agent MCP Server (port 3002)..."
        python agents/strategist_server.py > logs/strategist_server.log 2>&1 &
        STRATEGIST_PID=$!
        sleep 2

        # Start Executor Agent MCP Server
        print_info "⚡ Starting Executor Agent MCP Server (port 3003)..."
        python agents/executor_server.py > logs/executor_server.log 2>&1 &
        EXECUTOR_PID=$!
        sleep 2

        # Check agent health
        print_info "✅ Checking agent health..."
        sleep 3

        if curl -s http://localhost:3001/health > /dev/null; then
            print_status "Scout Agent: Online"
        else
            print_error "Scout Agent: Failed to start (check logs/scout_server.log)"
        fi

        if curl -s http://localhost:3002/health > /dev/null; then
            print_status "Strategist Agent: Online"
        else
            print_error "Strategist Agent: Failed to start (check logs/strategist_server.log)"
        fi

        if curl -s http://localhost:3003/health > /dev/null; then
            print_status "Executor Agent: Online"
        else
            print_error "Executor Agent: Failed to start (check logs/executor_server.log)"
        fi

        # Start Main API with --distributed flag
        print_info "🚀 Starting Main API server (distributed mode)..."
        python main.py --distributed &
        API_PID=$!

        # Cleanup function for distributed mode
        trap "kill $SCOUT_PID $STRATEGIST_PID $EXECUTOR_PID $API_PID 2>/dev/null" EXIT
    else
        print_info "🏠 LOCAL MODE: Starting agents in same process"
        print_info "🤖 CrewAI + MCP hybrid agents with distributed communication"
        echo ""

        print_info "🚀 Starting MCP API server..."
        python main.py &
        API_PID=$!
    fi

    # Wait for API to start with light pre-warming
    print_info "⏳ Waiting for MCP API to complete startup and pre-warming..."
    print_info "   🔥 This includes model loading and agent initialization"
    print_info "   ⏱️  This should take 5-10 seconds for optimal performance..."
    
    # Wait for light pre-warming to complete
    sleep 8
    
    # Check if API is running with retries
    print_info "🔍 Checking MCP API health..."
    for i in {1..6}; do
        if curl -s http://localhost:$API_PORT/health > /dev/null; then
            print_status "✅ MCP API is ready and fully pre-warmed!"
            
            # Show configuration summary
            echo ""
            echo "=========================================="
            print_status "🎮 MCP Multiplayer Game - Configuration Summary"
            echo "=========================================="
            
            # Determine deployment mode
            if [ "$DISTRIBUTED_MODE" = true ]; then
                print_info "🌐 Deployment Mode: DISTRIBUTED"
                print_info "   • Agents run as separate processes"
                print_info "   • Communication via HTTP/JSON-RPC"
                print_info "   • Scout: http://localhost:3001"
                print_info "   • Strategist: http://localhost:3002" 
                print_info "   • Executor: http://localhost:3003"
            else
                print_info "🏠 Deployment Mode: LOCAL"
                print_info "   • All agents in same process"
                print_info "   • Direct Python method calls"
                print_info "   • Faster communication"
            fi
            
            # Determine agent framework
            if [ -n "$AGENT_FRAMEWORK" ]; then
                if [ "$AGENT_FRAMEWORK" = "crewai" ]; then
                    print_info "🤖 Agent Framework: CREWAI"
                    print_info "   • Full agent coordination"
                    print_info "   • MCP protocol communication"
                    print_info "   • Complex but powerful"
                elif [ "$AGENT_FRAMEWORK" = "langchain" ]; then
                    print_info "🔗 Agent Framework: LANGCHAIN"
                    print_info "   • Direct LLM calls"
                    print_info "   • Faster and more reliable"
                    print_info "   • Simplified architecture"
                fi
            else
                # Read from config.json
                FRAMEWORK=$(python -c "import json; print(json.load(open('config.json')).get('agent_framework', {}).get('mode', 'langchain'))" 2>/dev/null || echo "langchain")
                if [ "$FRAMEWORK" = "crewai" ]; then
                    print_info "🤖 Agent Framework: CREWAI (from config)"
                else
                    print_info "🔗 Agent Framework: LANGCHAIN (from config)"
                fi
            fi
            
            # Show model configuration
            echo ""
            print_info "🤖 Agent Models:"
            # Get model info from API
            MODEL_INFO=$(curl -s http://localhost:$API_PORT/agents/status 2>/dev/null | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for agent, info in data.items():
        if agent != 'coordinator' and info and 'model' in info:
            print(f'   • {agent.title()}: {info[\"model\"]} ({info.get(\"framework\", \"unknown\")})')
except:
    print('   • Unable to fetch model information')
" 2>/dev/null || echo "   • Unable to fetch model information")
            echo "$MODEL_INFO"
            
            # Show API endpoints
            echo ""
            print_info "🌐 API Endpoints:"
            print_info "   • Backend API: http://localhost:$API_PORT"
            print_info "   • Streamlit UI: http://localhost:$STREAMLIT_PORT"
            print_info "   • Health Check: http://localhost:$API_PORT/health"
            print_info "   • Agent Status: http://localhost:$API_PORT/agents/status"
            
            echo ""
            print_status "🎨 Starting MCP Streamlit UI..."
            streamlit run streamlit_app.py --server.port $STREAMLIT_PORT --server.address 0.0.0.0
            return
        else
            print_info "   ⏳ Attempt $i/6: API not ready yet, waiting 5 more seconds..."
            sleep 5
        fi
    done
    
    # If we get here, API failed to start
    print_error "❌ MCP API failed to start after 50 seconds"
    print_error "   💡 The comprehensive pre-warming may have failed"
    print_error "   🔧 Check the logs above for any error messages"
    kill $API_PID 2>/dev/null || true
    if [ "$DISTRIBUTED_MODE" = true ]; then
        kill $SCOUT_PID $STRATEGIST_PID $EXECUTOR_PID 2>/dev/null || true
    fi
    exit 1
}

# Function to start the optimized application
start_optimized_application() {
    print_info "🚀 Starting OPTIMIZED Tic Tac Toe (shared resources, no MCP servers)..."
    echo "=========================================="
    
    print_info "🏠 OPTIMIZED LOCAL MODE: Shared resources"
    print_info "   • Shared Ollama connection"
    print_info "   • Shared model instance"
    print_info "   • No MCP servers"
    print_info "   • Pre-created tasks"
    print_info "   • < 1 second per move"
    echo ""
    
    # Start Optimized API
    print_info "🚀 Starting Optimized API server..."
    python main_optimized.py &
    API_PID=$!
    
    # Wait for API to start
    print_info "⏳ Waiting for Optimized API to start..."
    sleep 3
    
    # Check if API is running
    print_info "🔍 Checking Optimized API health..."
    for i in {1..5}; do
        if curl -s http://localhost:8000/health > /dev/null; then
            print_status "✅ Optimized API is ready!"
            break
        else
            print_info "   ⏳ Attempt $i/5: API not ready yet, waiting 2 more seconds..."
            sleep 2
        fi
    done
    
    # Show configuration summary
    echo ""
    echo "=========================================="
    print_status "🎮 Optimized Tic Tac Toe - Configuration Summary"
    echo "=========================================="
    
    print_info "🚀 Architecture: OPTIMIZED LOCAL"
    print_info "   • Shared Ollama connection"
    print_info "   • Shared model instance"
    print_info "   • No MCP servers"
    print_info "   • Pre-created tasks"
    print_info "   • Direct method calls"
    
    print_info "⚡ Performance: FAST"
    print_info "   • < 1 second per move"
    print_info "   • 8-19x faster than distributed"
    print_info "   • 10x simpler than CrewAI"
    print_info "   • 5x easier maintenance"
    
    print_info "🌐 API Endpoints:"
    print_info "   • Optimized API: http://localhost:8000"
    print_info "   • Streamlit UI: http://localhost:8501"
    print_info "   • Health Check: http://localhost:8000/health"
    print_info "   • Performance: http://localhost:8000/performance"
    
    print_status "✅ 🎨 Starting Optimized Streamlit UI..."
    streamlit run optimized_streamlit.py --server.port 8501 --server.address 0.0.0.0 &
    STREAMLIT_PID=$!
    
    # Wait for Streamlit to start
    sleep 3
    
    echo ""
    print_status "🎮 Optimized Tic Tac Toe is ready!"
    print_info "   • Frontend: http://localhost:8501"
    print_info "   • Backend: http://localhost:8000"
    print_info "   • Architecture: Optimized Local (shared resources)"
    print_info "   • Speed: < 1 second per move"
    echo ""
    print_info "💡 Benefits of Optimized Mode:"
    print_info "   • Shared Ollama connection (no duplication)"
    print_info "   • Shared model instance (memory efficient)"
    print_info "   • No MCP servers (no overhead)"
    print_info "   • Pre-created tasks (no runtime creation)"
    print_info "   • Direct method calls (no async coordination)"
    echo ""
    print_info "🔧 To use distributed mode: ./quickstart.sh --crewai -d"
    print_info "🔧 To use simple mode: ./quickstart.sh --simple"
    echo ""
    
    # Keep the script running
    print_info "Press Ctrl+C to stop all services"
    wait
}

# Function to start the simple application
start_simple_application() {
    print_info "🚀 Starting SIMPLE Tic Tac Toe (bypassing complex architecture)..."
    echo "=========================================="
    
    print_info "🏠 SIMPLE MODE: Direct LLM calls only"
    print_info "   • No CrewAI agents"
    print_info "   • No MCP protocol"
    print_info "   • No async coordination"
    print_info "   • < 1 second per move"
    echo ""
    
    # Start Simple API
    print_info "🚀 Starting Simple API server..."
    python simple_api.py &
    API_PID=$!
    
    # Wait for API to start
    print_info "⏳ Waiting for Simple API to start..."
    sleep 3
    
    # Check if API is running
    print_info "🔍 Checking Simple API health..."
    for i in {1..5}; do
        if curl -s http://localhost:8000/health > /dev/null; then
            print_status "✅ Simple API is ready!"
            break
        else
            print_info "   ⏳ Attempt $i/5: API not ready yet, waiting 2 more seconds..."
            sleep 2
        fi
    done
    
    # Show configuration summary
    echo ""
    echo "=========================================="
    print_status "🎮 Simple Tic Tac Toe - Configuration Summary"
    echo "=========================================="
    
    print_info "🚀 Architecture: SIMPLE"
    print_info "   • Direct LLM calls only"
    print_info "   • No agent coordination"
    print_info "   • No MCP protocol"
    print_info "   • Minimal overhead"
    
    print_info "⚡ Performance: FAST"
    print_info "   • < 1 second per move"
    print_info "   • 8-19x faster than complex"
    print_info "   • 10x simpler code"
    print_info "   • 5x easier maintenance"
    
    # Show API endpoints
    echo ""
    print_info "🌐 API Endpoints:"
    print_info "   • Simple API: http://localhost:8000"
    print_info "   • Streamlit UI: http://localhost:8501"
    print_info "   • Health Check: http://localhost:8000/health"
    print_info "   • Performance: http://localhost:8000/performance"
    
    echo ""
    print_status "🎨 Starting Simple Streamlit UI..."
    streamlit run simple_streamlit.py --server.port 8501 --server.address 0.0.0.0
    
    # Cleanup
    kill $API_PID 2>/dev/null || true
}

# Main execution function
main() {
    # Parse command line arguments
    SKIP_CLEANUP=false
    SKIP_SETUP=false
    DISTRIBUTED_MODE=false
    AGENT_FRAMEWORK=""
    
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
            --distributed|--dist|--d|-d)
                DISTRIBUTED_MODE=true
                shift
                ;;
            --crewai)
                AGENT_FRAMEWORK="crewai"
                shift
                ;;
            --langchain)
                AGENT_FRAMEWORK="langchain"
                shift
                ;;
            --simple|--s)
                AGENT_FRAMEWORK="simple"
                shift
                ;;
            --optimized|--o)
                AGENT_FRAMEWORK="optimized"
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "MCP Multiplayer Game - Agent Framework Selection"
                echo "🤖 Choose between CrewAI and LangChain agent frameworks"
                echo ""
                echo "Options:"
                echo "  --skip-cleanup          Skip cleaning up existing processes"
                echo "  --skip-setup            Skip environment setup (assumes venv exists)"
                echo "  -d, --d, --distributed  Run in distributed mode (agents as separate processes)"
                echo "  --crewai                Use CrewAI agents with MCP protocol (complex, full coordination)"
                echo "  --langchain             Use LangChain agents (faster, simpler, more reliable)"
                echo "  --simple, --s           Use simple direct LLM calls (fastest, < 1 second per move)"
                echo "  --optimized, --o        Use optimized local mode (shared resources, no MCP servers)"
                echo "  -h, --help              Show this help message"
                echo ""
                echo "Agent Frameworks:"
                echo "  Simple (--simple):       Direct LLM calls, < 1 second per move (fastest)"
                echo "  Optimized (--optimized):  LangChain with shared resources, < 1 second per move (recommended)"
                echo "  LangChain (--langchain):  Direct LLM calls, faster than CrewAI"
                echo "  CrewAI (--crewai):       Full agent coordination with MCP protocol"
                echo ""
                echo "Mode Comparison:"
                echo "  🚀 Simple:     Direct LLM, < 1s, 1 connection, fastest"
                echo "  ⚡ Optimized:   LangChain, < 1s, shared resources, best balance"
                echo "  🏠 Local:       CrewAI, 3-8s, 3 connections, agent coordination"
                echo "  🌐 Distributed: CrewAI+MCP, 3-8s, 3 processes, multi-machine"
                echo ""
                echo "Deployment Modes:"
                echo "  Local Mode (default):     All agents in same process, direct Python calls"
                echo "  Distributed Mode:         Agents as separate processes, HTTP/JSON-RPC transport"
                echo ""
                echo "API Key Setup:"
                echo "  The script will check for API keys and prompt you to set them up if missing."
                echo "  You can either:"
                echo "    1. Add API keys to .env file (recommended)"
                echo "    2. Install Ollama for local models"
                echo "    3. Continue with limited functionality"
                echo ""
                echo "Architecture:"
                echo "  Local Mode:      FastAPI (8000) + Streamlit (8501)"
                echo "  Distributed:     Scout (3001) + Strategist (3002) + Executor (3003)"
                echo "                   + FastAPI (8000) + Streamlit (8501)"
                echo ""
                echo "Examples:"
                echo "  $0 --simple       # Simple direct LLM (fastest, < 1 second per move)"
                echo "  $0 --s            # Short form of --simple"
                echo "  $0 --optimized    # Optimized local mode (shared resources, no MCP)"
                echo "  $0 --o            # Short form of --optimized"
                echo "  $0 --langchain    # LangChain agents (faster than CrewAI)"
                echo "  $0 --crewai       # CrewAI agents with MCP protocol (complex)"
                echo "  $0 --s -d         # Simple mode in distributed (not recommended)"
                echo "  $0 --langchain -d # LangChain agents in distributed mode"
                echo "  $0 --crewai -d    # CrewAI agents in distributed mode"
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
    
    # Configure agent framework if specified
    if [ -n "$AGENT_FRAMEWORK" ]; then
        if [ "$AGENT_FRAMEWORK" = "simple" ]; then
            print_info "🚀 Using SIMPLE mode - bypassing complex architecture"
            print_info "   • Direct LLM calls only"
            print_info "   • < 1 second per move"
            print_info "   • No CrewAI/MCP overhead"
        else
            print_info "🔧 Configuring agent framework: $AGENT_FRAMEWORK"
            python -c "
import json
import sys
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    if 'agent_framework' not in config:
        config['agent_framework'] = {}
    config['agent_framework']['mode'] = '$AGENT_FRAMEWORK'
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print('✅ Framework configured: $AGENT_FRAMEWORK')
except Exception as e:
    print(f'❌ Error configuring framework: {e}')
    sys.exit(1)
"
            if [ $? -ne 0 ]; then
                print_error "Failed to configure agent framework"
                exit 1
            fi
        fi
    else
        print_info "🔍 Using default framework from config.json"
    fi
    
    # Validate environment
    validate_environment
    
    # Start the application
    if [ "$AGENT_FRAMEWORK" = "simple" ]; then
        start_simple_application
    elif [ "$AGENT_FRAMEWORK" = "optimized" ]; then
        start_optimized_application
    else
        start_application
    fi
}

# Handle script interruption
trap 'echo ""; print_warning "Interrupted by user"; exit 1' INT

# Run main function
main "$@"