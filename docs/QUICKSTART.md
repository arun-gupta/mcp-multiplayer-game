# Quick Start Guide

Get the Multi-Agent Game Simulation running in 5 minutes!

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.11+
- OpenAI API key (for Scout Agent)
- Anthropic API key (for Strategist Agent)
- Ollama (for local models)

### 2. Install Ollama

Ollama is required for running local models (like Llama2, Llama3, Mistral) that can be used by any of the agents.

#### **macOS:**

**Method 1: Install using Homebrew (recommended)**
```bash
brew install ollama
```

**Method 2: Download from website**
1. Visit [https://ollama.ai/download](https://ollama.ai/download)
2. Download the macOS installer (.pkg file)
3. Run the installer and follow the setup wizard
4. Restart your terminal

#### **Linux:**

**Method 1: Install using curl (works on all Linux distributions)**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Method 2: Install using package manager**

*Ubuntu/Debian:*
```bash
sudo apt-get install ollama
```

*Fedora:*
```bash
sudo dnf install ollama
```

#### **Windows:**
1. Visit [https://ollama.ai/download](https://ollama.ai/download)
2. Download the Windows installer (.exe file)
3. Run the installer and follow the setup wizard
4. Restart your terminal/command prompt

#### **Verify Installation:**
```bash
# Check if Ollama is installed
ollama --version

# Start Ollama service (if not already running)
ollama serve
```

### 3. Install Ollama Models
```bash
ollama pull llama2:7b llama3:latest mistral:latest
```

### 4. Setup Python Environment

**Clone the repository:**
```bash
git clone https://github.com/arun-gupta/mcp-multiplayer-game.git
cd mcp-multiplayer-game
```

**Create virtual environment and install dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Set Environment Variables

**Copy the example environment file:**
```bash
cp .env.example .env
```

**Edit the .env file and add your API keys:**
```bash
# Open .env in your preferred editor
nano .env
# or
code .env
# or
vim .env
```

**Replace the placeholder values with your actual API keys:**
```
OPENAI_API_KEY=your-actual-openai-api-key-here
ANTHROPIC_API_KEY=your-actual-anthropic-api-key-here
```

> **💡 Note:** If you don't have API keys, the application will still run but with limited AI functionality. You can use local models with Ollama instead.

### 6. Test Installation
```bash
python test_installation.py
```

### 7. Running Without API Keys

If you don't have API keys, the application will still work with some limitations:

**What works:**
- ✅ Web interface loads
- ✅ Game board displays
- ✅ Human can make moves
- ✅ Local models (if Ollama is installed)

**What doesn't work:**
- ❌ AI won't make moves (no cloud models)
- ❌ MCP coordination will be limited
- ❌ Some features may show errors

**To enable full functionality:**
1. **Add API keys** (recommended):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Use local models** (alternative):
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model
   ollama pull llama3.2:3b
   ```

### 7. Choose Deployment Mode

This project supports two deployment modes:

#### **🏠 Local Mode (Default, Recommended)**
All agents run in the same Python process with direct method calls. Better performance, simpler setup.

```bash
# Option 1: Quick Start Script
./quickstart.sh

# Option 2: Manual Start
python main.py &           # Start API server
python run_streamlit.py    # Start UI
```

**Ports:**
- **8000** - Main API Server
- **8501** - Streamlit UI

#### **🌐 Distributed Mode**
Agents run as separate processes communicating via HTTP/JSON-RPC (true MCP transport). Use this to demonstrate the actual MCP protocol transport layer.

```bash
# Quick Start Script (Recommended)
./quickstart.sh -d  # or --d, --dist, --distributed
```

This automatically starts:
- **3001** - Scout Agent Server
- **3002** - Strategist Agent Server
- **3003** - Executor Agent Server
- **8000** - Main API Server (with `--distributed` flag)
- **8501** - Streamlit UI

**Manual Distributed Mode:**
```bash
# Terminal 1: Start Scout Agent
python agents/scout_server.py

# Terminal 2: Start Strategist Agent
python agents/strategist_server.py

# Terminal 3: Start Executor Agent
python agents/executor_server.py

# Terminal 4: Start Main API (distributed mode)
python main.py --distributed

# Terminal 5: Start Streamlit UI
python run_streamlit.py
```

### 8. Access the Application

**Both modes use the same URLs:**
- **Frontend**: http://localhost:8501 (Streamlit)
- **Backend**: http://localhost:8000 (FastAPI)
- **API Docs**: http://localhost:8000/docs

**Distributed mode additional endpoints:**
- **Scout Agent**: http://localhost:3001/mcp
- **Strategist Agent**: http://localhost:3002/mcp
- **Executor Agent**: http://localhost:3003/mcp

## 🎮 How to Play

1. **View the Game**: Open http://localhost:8501 (Streamlit Frontend)
2. **Play Tic-Tac-Toe**: You play as X against the AI team (Double-O-AI)
3. **Watch the Agents**: See the three agents work together:
   - **Scout** analyzes the game state
   - **Strategist** creates a strategy
   - **Executor** makes the move
4. **Monitor Progress**: Check game history, metrics, and MCP logs
5. **Switch Models**: Try different AI models for each agent
6. **New Game**: Start over with "New Game" button

## 🔍 Understanding the Flow

Each AI move follows this sequence:

```
Scout Agent (Available Model) → Strategist Agent (Available Model) → Executor Agent (Available Model)
     ↓                              ↓                              ↓
  Analyzes                    Creates Strategy                 Makes the Move
  Game State                  Based on                        Updates Board
  (Current Board)             Analysis
```

## 📡 API Quick Test

```bash
# Get current game state
curl http://localhost:8000/state

# Simulate a turn
curl -X POST http://localhost:8000/simulate-turn

# Get agent information
curl http://localhost:8000/agents

# View MCP protocol logs
curl http://localhost:8000/mcp-logs
```

## 🛠️ Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not set"**
   - Set your OpenAI API key: `export OPENAI_API_KEY="your-key"`

2. **"Ollama not found"**
   - Install Ollama: https://ollama.ai/
   - Pull models: `ollama pull llama2:7b llama3:latest mistral:latest`

3. **"Module not found"**
   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

4. **"Connection refused"**
   - Make sure Ollama is running: `ollama serve`

5. **"Address already in use"**
   - Use the start script: `./start.sh` (automatically kills existing processes)
   - Or manually kill processes: `lsof -ti:8000 | xargs kill -9`

6. **"Virtual environment not detected"**
   - Activate your virtual environment: `source venv/bin/activate`
   - Then run: `./start.sh`

### Test Your Setup

```bash
# Run comprehensive test
python test_installation.py

# Check if all components work
python -c "
from game.state import GameStateManager
from agents.scout import ScoutAgent
print('✅ Basic setup works!')
"
```

## 🎯 What You'll See

### Game Map
```
   0 1 2 3 4
 0 P . . . .
 1 . # . # .
 2 . . I . .
 3 . # . # .
 4 . . . . E
```

### Agent Communication
```
[SCOUT] Turn 1 - 1 enemies, 1 items detected
[STRATEGIST] Turn 1 - Created plan with 2 actions
[EXECUTOR] Turn 1 - Executed 2 actions, Success rate: 2/2
```

### Turn Results
- Player movement and positioning
- Combat with enemies
- Item collection
- Health changes
- Victory/defeat conditions

## 🔮 Next Steps

1. **Explore the Code**: Check out the agent implementations
2. **Modify the Game**: Add new actions or map features
3. **Customize Agents**: Adjust agent behaviors and strategies
4. **Scale Up**: Add more players or complex scenarios

## 📚 Learn More

- **Full Documentation**: README.md
- **API Reference**: http://localhost:8000/docs
- **Architecture**: See README.md for detailed diagrams
- **Development**: Check the project structure and code comments

---

**Happy Gaming! 🎮**

Need help? Check the full README.md or create an issue in the repository. 