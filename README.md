# 🎮 Agentic Tic-Tac-Toe: MCP Protocol Showcase

A **Multi-Context Protocol (MCP) demonstration** featuring an interactive Tic Tac Toe game where **three AI agents work together** using **CrewAI** as the agentic framework. This project showcases how multiple LLMs can collaborate through structured communication protocols - each agent runs on different models and communicates only through standardized JSON schemas.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agentic%20Framework-orange.svg)](https://github.com/joaomdmoura/crewAI)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## 🎯 Quick Overview

- **🎮 Game**: Interactive Tic Tac Toe vs AI team
- **🤖 AI Team**: Three specialized agents (Scout, Strategist, Executor)
- **🔄 Hot-Swappable Models**: Switch LLMs mid-game without restart
- **📊 Real-time Metrics**: MCP protocol monitoring and performance analytics
- **🎨 Modern UI**: Streamlit dashboard with live updates

## 🚀 Quick Start

**Get started in 5 minutes!**

### 🎯 **One-Command Setup (Recommended)**

```bash
# Clone and setup everything automatically
git clone https://github.com/arun-gupta/mcp-multiplayer-game.git
cd mcp-multiplayer-game
chmod +x launch.sh
./launch.sh
```

**Access the game**: http://localhost:8501

### 🔧 **Manual Setup (Alternative)**

```bash
# Clone and setup
git clone https://github.com/arun-gupta/mcp-multiplayer-game.git
cd mcp-multiplayer-game

# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Ollama models (optional)
ollama pull llama2:7b
ollama pull llama3:latest

# Run the application
python run_app.py
```

### 🎮 **What the Launch Script Does**

The `launch.sh` script automatically:
- ✅ **Process cleanup** - Kills existing processes on ports 8000/8501
- ✅ **Environment setup** - Creates venv and installs dependencies
- ✅ **Python version checking** - Validates Python 3.11+
- ✅ **Dependency installation** - Installs all requirements with Python 3.13 compatibility
- ✅ **Ollama model setup** - Optional local model installation
- ✅ **File validation** - Checks for all required files
- ✅ **Application startup** - Starts both backend and frontend services
- ✅ **Error handling** - Comprehensive error checking and colored output

### 🚀 **Advanced Usage**

```bash
# Full setup and launch (default)
./launch.sh

# Launch only (skip setup, venv must exist)
./launch.sh --skip-setup

# Setup and launch without cleanup
./launch.sh --skip-cleanup

# Show help
./launch.sh --help
```

📖 **[Complete Setup Guide](QUICKSTART.md)** - Detailed instructions and troubleshooting

---

## 🎮 Game Experience

### How to Play

1. **You play as X** against the AI team "Double-O-AI"
2. **Click any empty cell** to place your X
3. **Watch the AI team work**:
   - **Scout Agent** analyzes the board and threats
   - **Strategist Agent** creates a strategic plan
   - **Executor Agent** makes the AI's move (O)
4. **Continue until someone wins** or it's a draw

### AI Team Composition

| Agent | Model | Role | Capabilities |
|-------|-------|------|--------------|
| **Scout** | Llama2 7B | Observer | Board analysis, threat detection, pattern recognition |
| **Strategist** | Llama3 Latest | Planner | Strategic planning, move selection, confidence assessment |
| **Executor** | Llama2 7B | Executor | Move execution, validation, state updates |

### Victory Conditions

- **Player Win**: Three X's in a row (horizontal, vertical, or diagonal)
- **AI Win**: Three O's in a row (horizontal, vertical, or diagonal)  
- **Draw**: All 9 cells filled with no winner

---

## 🔄 Hot-Swappable Models

**The most powerful feature** - dynamically change which LLM each agent uses without restarting the game!

### ✅ Implemented Features

- **🔄 Runtime Model Switching**: Swap any agent's LLM mid-game
- **🏪 Model Registry**: Centralized registry of available models
- **📊 Performance Comparison**: A/B test different models for each role
- **⚙️ Configuration API**: REST endpoints for model management
- **✅ Model Validation**: Automatic compatibility checking
- **📈 Performance Tracking**: Monitor model impact on agent performance

### 🌐 Supported Models

**Legend:**
- ☁️ **Cloud**: Hosted models requiring API keys and internet connection
- 🖥️ **Local**: Models running on your machine via Ollama (offline capable)

| Provider | Models | Type |
|----------|--------|------|
| **OpenAI** | GPT-4, GPT-4 Turbo, GPT-3.5 Turbo | ☁️ Cloud |
| **Anthropic** | Claude 3 Sonnet, Claude 3 Haiku | ☁️ Cloud |
| **Ollama** | Llama2 7B/13B, Llama3 Latest, Mistral 7B | 🖥️ Local |

### 🎯 Use Cases

- **Performance Testing**: Compare GPT-4 vs Llama3 in strategy planning
- **Cost Optimization**: Switch between expensive cloud and free local models
- **Specialization**: Use different models optimized for specific tasks
- **Redundancy**: Fallback to local models if cloud APIs are unavailable

---

## 🏗️ Architecture

### CrewAI Agentic Framework

Built on **CrewAI** for sophisticated multi-agent orchestration:

- **Agent Management**: Structured agent creation with roles and goals
- **Task Delegation**: Automatic workflow management
- **LLM Integration**: Seamless multi-provider support
- **Communication Protocols**: Built-in agent-to-agent communication

### Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Agentic Framework** | [CrewAI](https://github.com/joaomdmoura/crewAI) | Multi-agent orchestration |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance web framework |
| **Frontend** | [Streamlit](https://streamlit.io/) | Interactive web dashboard |
| **LLM Integration** | [LangChain](https://langchain.com/) | LLM provider abstraction |
| **Local Models** | [Ollama](https://ollama.ai/) | Local LLM deployment |
| **Data Validation** | [Pydantic](https://pydantic.dev/) | Schema validation |

### MCP-Style Communication

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scout Agent   │    │ Strategist Agent│    │ Executor Agent  │
│  (Llama2 7B)    │───▶│  (Llama3 Latest)│───▶│  (Llama2 7B)    │
│                 │    │                 │    │                 │
│ • Observes      │    │ • Analyzes      │    │ • Executes      │
│ • Reports       │    │ • Plans         │    │ • Updates       │
│ • Pattern Rec.  │    │ • Prioritizes   │    │ • Validates     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Game State Manager                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Game State  │  │ Game Engine │  │ Move History│            │
│  │ (TTT Logic) │  │ (TTT Rules) │  │ (Logging)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints

### Core Game Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Game dashboard with visualization |
| `/state` | GET | Current game state |
| `/make-move` | POST | Make a player move |
| `/simulate-turn` | POST | Simulate a complete AI turn |
| `/reset-game` | POST | Reset game to initial state |

### Agent & Model Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents` | GET | Information about all agents |
| `/models` | GET | Available models for switching |
| `/switch-model` | POST | Switch agent to different model |
| `/mcp-logs` | GET | MCP protocol message logs |
| `/metrics` | GET | Performance metrics and analytics |

### Example Usage

```bash
# Get current game state
curl http://localhost:8000/state

# Make a move (row=0, col=0)
curl -X POST http://localhost:8000/make-move \
  -H "Content-Type: application/json" \
  -d '{"row": 0, "col": 0}'

# Switch Scout agent to GPT-4
curl -X POST http://localhost:8000/switch-model \
  -H "Content-Type: application/json" \
  -d '{"agent": "scout", "model": "gpt-4"}'

# Get agent information
curl http://localhost:8000/agents
```

---

## 📊 Monitoring & Analytics

### Real-time Dashboard

The Streamlit dashboard provides comprehensive monitoring:

- **🎮 Game Tab**: Interactive game board and move history
- **🤖 AI Agents & Models**: Agent information and model switching
- **📡 MCP Logs**: Real-time protocol communication logs
- **📊 Metrics**: Performance analytics and system monitoring

### Key Metrics Tracked

| Metric | Description |
|--------|-------------|
| **Total Messages** | All system and agent messages |
| **Agent Messages** | Inter-agent communication only |
| **GameEngine Messages** | System events and state updates |
| **Response Times** | Per-agent performance tracking |
| **Token Usage** | LLM consumption per agent |
| **Model Switches** | History of model changes |

### MCP Protocol Logging

All agent communications are logged in structured JSON:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "agent": "Scout",
  "message_type": "Observation",
  "data": {
    "current_board": [["X", "", ""], ["", "O", ""], ["", "", ""]],
    "current_player": "ai",
    "move_number": 2,
    "available_moves": [...],
    "threats": [...],
    "blocking_moves": [...]
  }
}
```

---

## 🛠️ Development

### Project Structure

```
mcp-multiplayer-game/
├── main.py                 # FastAPI application
├── streamlit_app.py        # Streamlit dashboard
├── run_app.py             # Unified launcher script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── QUICKSTART.md         # Detailed setup guide
├── schemas/              # MCP-style communication schemas
│   ├── observation.py    # Scout observations
│   ├── plan.py          # Strategist plans
│   └── action_result.py # Executor results
├── agents/              # CrewAI agent implementations
│   ├── scout.py        # Scout agent
│   ├── strategist.py   # Strategist agent
│   └── executor.py     # Executor agent
└── game/               # Game logic and state
    └── state.py       # Tic Tac Toe game state management
```

### Running in Development

```bash
# Start both backend and frontend
python run_app.py

# Or start separately
python main.py          # Backend API (port 8000)
streamlit run streamlit_app.py  # Frontend (port 8501)
```

### Adding New Features

1. **New Agents**: Create agent class in `agents/` directory
2. **New Models**: Add to `ModelRegistry` in agent files
3. **New Game Mechanics**: Extend `game/state.py`
4. **New Metrics**: Add tracking in `game/state.py`

---

## 🔮 Feature Status

**Legend:**
- ✅ **Implemented**: Fully functional and available
- ⏳ **In Progress**: Partially implemented
- 🔮 **Planned**: Future development

### ✅ Implemented Features

#### 🎮 Game Features
- ✅ Interactive Tic Tac Toe gameplay
- ✅ Move history and replay
- ✅ Real-time game state updates
- ✅ Win/draw detection and game over handling

#### 🔄 MCP Protocol Features
- ✅ Hot-swappable LLMs with runtime switching
- ✅ Model registry with validation
- ✅ Performance comparison and tracking
- ✅ Configuration API endpoints
- ✅ Real-time model switching UI

#### 📊 Monitoring & Analytics
- ✅ MCP protocol message logging
- ✅ Agent performance metrics
- ✅ Response time tracking
- ✅ Token usage monitoring
- ✅ Model switch history
- ✅ Real-time dashboard updates

### ⏳ In Progress

- ⏳ Preset model configurations
- ⏳ Enhanced performance analytics
- ⏳ Advanced agent strategies

### 🔮 Planned Features

- 🔮 Multiple game modes (Connect Four, Chess)
- 🔮 Real-time multiplayer support
- 🔮 Advanced MCP protocol features
- 🔮 Machine learning pattern recognition

---

## 📄 License

This project is licensed under the **Apache License, Version 2.0** - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Issues**: Create an issue in the repository
- **Documentation**: Check `/docs` for API documentation
- **Debugging**: Review MCP logs for troubleshooting

---

**Happy Gaming! 🎮**

*Experience the power of multi-agent collaboration with hot-swappable models!* 