# Quick Start Guide

Get the Multi-Agent Game Simulation running in 5 minutes!

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.11+
- OpenAI API key (for Scout Agent)
- Ollama (for local models)

### 2. Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### 3. Install Ollama Models
```bash
ollama pull mistral
ollama pull llama2:7b
```

### 4. Setup Python Environment
```bash
# Clone and setup
git clone <repository-url>
cd mcp-multiplayer-game

# Run automated setup
python setup.py

# Or manual setup:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Set Environment Variables
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### 6. Test Installation
```bash
python test_installation.py
```

### 7. Run the Application
```bash
python main.py
```

### 8. Open in Browser
- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎮 How to Play

1. **View the Game**: Open http://localhost:8000
2. **Simulate a Turn**: Click "Simulate Turn" button
3. **Watch the Agents**: See the three agents work together:
   - **Scout** observes the environment
   - **Strategist** creates a plan
   - **Executor** carries out the plan
4. **Monitor Progress**: Check turn history and game state
5. **Reset**: Start over with "Reset Game"

## 🔍 Understanding the Flow

Each turn follows this sequence:

```
Scout Agent (Claude) → Strategist Agent (Mistral) → Executor Agent (Llama2:7B)
     ↓                        ↓                        ↓
  Observes              Creates Plan              Executes Actions
  Environment           Based on                  Updates Game State
  (Limited View)        Observations
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
   - Pull models: `ollama pull mistral llama2:7b`

3. **"Module not found"**
   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

4. **"Connection refused"**
   - Make sure Ollama is running: `ollama serve`

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