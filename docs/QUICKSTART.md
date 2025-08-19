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

### 6. Test Installation
```bash
python test_installation.py
```

### 7. Run the Application

**Option 1: Quick Start (Recommended)**
```bash
./start.sh
```
This script will:
- Kill any existing processes on ports 8000 and 8501
- Verify your virtual environment is active
- Start both backend and frontend servers
- Open the application in your browser

**Option 2: Manual Start**
```bash
# Start backend only
python main.py

# Or use the Python launcher (starts both servers)
python run_app.py
```

### 8. Open in Browser
- **Frontend**: http://localhost:8501 (Streamlit)
- **Backend**: http://localhost:8000 (FastAPI)
- **API Docs**: http://localhost:8000/docs

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