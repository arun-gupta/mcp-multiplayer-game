# 🎮 Agentic Tic-Tac-Toe with CrewAI and MCP

[![YouTube Demo](https://img.shields.io/badge/YouTube-Demo%20Video-red?style=for-the-badge&logo=youtube)](https://youtu.be/6kMry-zlO3U)
[![Version](https://img.shields.io/badge/Demo%20Version-v1.0-orange?style=for-the-badge)](https://youtu.be/6kMry-zlO3U)
[![Latest](https://img.shields.io/badge/Current-v2.0-brightgreen?style=for-the-badge)](#-quick-overview)

An interactive Tic Tac Toe game where **three AI agents work together** using **CrewAI** as the agent framework and **MCP (Multi-Context Protocol)** for distributed communication. This project showcases how multiple LLMs can collaborate through structured communication protocols - each agent runs as both a CrewAI Agent and an MCP Server.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agentic%20Framework-orange.svg)](https://github.com/joaomdmoura/crewAI)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## 🎯 Quick Overview

- **🎮 Game**: Interactive Tic Tac Toe vs AI team
- **🤖 AI Team**: Three MCP agents (Scout, Strategist, Executor) - each a CrewAI Agent + MCP Server
- **🔄 Hot-Swappable Models**: Switch LLMs mid-game without restart via MCP protocol
- **📊 Real-time Analytics**: MCP protocol monitoring and performance analytics
- **🎨 Modern UI**: Streamlit dashboard with live updates
- **🌐 Distributed**: Each agent runs as independent MCP server for scalable deployment

## 🚀 Quick Start

**Get started in 5 minutes!**

### 🎯 **One-Command Setup (Recommended)**

```bash
# Clone and setup MCP hybrid architecture automatically
git clone https://github.com/arun-gupta/mcp-multiplayer-game.git
cd mcp-multiplayer-game
chmod +x quickstart.sh
./quickstart.sh
```

**Access the game**: http://localhost:8501  
**API Documentation**: http://localhost:8000/docs

### 🔧 **Manual Setup (Alternative)**

```bash
# Clone and setup MCP hybrid architecture
git clone https://github.com/arun-gupta/mcp-multiplayer-game.git
cd mcp-multiplayer-game

# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Ollama models (optional)
ollama pull llama2:7b
ollama pull mistral

# Start MCP API server
python main.py &

# Start Streamlit UI (in another terminal)
python run_streamlit.py
```

### 🎮 **What the Quickstart Script Does**

The `quickstart.sh` script automatically:
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
./quickstart.sh

# Launch only (skip setup, venv must exist)
./quickstart.sh --skip-setup

# Setup and launch without cleanup
./quickstart.sh --skip-cleanup

# Show help
./quickstart.sh --help
```

📖 **[Complete Setup Guide](docs/QUICKSTART.md)** - Detailed instructions and troubleshooting

## 📚 Documentation

### **📖 Guides & Tutorials**
- **[📋 Quick Start Guide](docs/QUICKSTART.md)** - Complete setup and troubleshooting
- **[🎨 Streamlit UI Guide](docs/README_STREAMLIT.md)** - Frontend features and customization

### **📚 Reference Documentation**
- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - System architecture and design
- **[📡 API Reference](docs/API.md)** - Complete API documentation and examples
- **[🎮 User Guide](docs/USER_GUIDE.md)** - Game experience and setup instructions
- **[🚀 Features](docs/FEATURES.md)** - Detailed feature explanations and capabilities
- **[🛠️ Development](docs/DEVELOPMENT.md)** - Development workflow and contribution guidelines

### **🔗 MCP Protocol Documentation**
- **[🔍 MCP Query Guide](docs/MCP_QUERY_GUIDE.md)** - All methods to query MCP servers (Recommended starting point)
- **[🌐 REST API Guide](docs/MCP_REST_API_GUIDE.md)** - Detailed REST/HTTP API reference with Python examples
- **[📋 MCP Protocol](docs/MCP_PROTOCOL.md)** - Complete MCP protocol implementation details

## 🔑 API Keys Setup

To use the AI agents, you'll need API keys for the LLM providers. See the **[User Guide](docs/USER_GUIDE.md)** for detailed setup instructions.

## ⚙️ Configuration

The application uses `config.json` for all configuration settings. Copy the example file and customize as needed:

```bash
cp config.example.json config.json
```

### Configuration Options:

```json
{
  "mcp": {
    "ports": {
      "scout": 3001,       // MCP server port for Scout agent
      "strategist": 3002,  // MCP server port for Strategist agent
      "executor": 3003     // MCP server port for Executor agent
    },
    "host": "localhost",
    "protocol": "http"
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000           // FastAPI server port
  },
  "streamlit": {
    "host": "0.0.0.0",
    "port": 8501           // Streamlit UI port
  },
  "models": {
    "default": "gpt-5-mini",  // Default model for all agents
    "fallback": ["gpt-4", "claude-3-sonnet", "llama3.2:3b"]
  },
  "performance": {
    "mcp_coordination_timeout": 15,     // Timeout for MCP coordination (seconds)
    "agent_execution_timeout": 8,       // Timeout for individual agent tasks (seconds)
    "enable_metrics": true              // Enable/disable performance metrics
  }
}
```

**Note:** `config.json` is gitignored for security. Always use `config.example.json` as a template.

---

## 🏗️ Architecture

The system uses **MCP (Multi-Context Protocol)** for distributed communication between CrewAI agents. Each agent runs as both a CrewAI Agent and an MCP Server, enabling modular, scalable deployment.

### **Key Components**
- **🤖 MCP Agents**: Scout, Strategist, Executor (Ports 3001-3003)
- **🌐 FastAPI Server**: Main application server (Port 8000)
- **🎨 Streamlit UI**: Interactive game interface (Port 8501)
- **📡 MCP Coordinator**: Orchestrates agent communication with streamlined real-time coordination

### **🚀 Streamlined MCP Coordination**

For optimal real-time gaming performance, the system uses a **lightweight MCP coordination approach**:

- **⚡ Fast Response Times**: Sub-second AI moves via optimized agent communication
- **🎯 Strategic Logic**: Direct blocking/winning move detection for immediate threats
- **📊 Real-Time Metrics**: Accurate request tracking with microsecond precision
- **🔄 Auto-AI Moves**: Automatic AI turn triggering via dedicated `/ai-move` endpoint
- **🎮 Seamless UX**: No delays or timeouts during gameplay

### **API Endpoints**

#### 🌐 **FastAPI Server Endpoints** (Port 8000)
*Main application server that coordinates everything*

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/state` | GET | Get current game state |
| `/make-move` | POST | Make a player move and get AI response |
| `/ai-move` | POST | Trigger AI move (auto-called when AI's turn) |
| `/reset-game` | POST | Reset game |
| `/agents/status` | GET | Get all agent status |
| `/agents/{agent_id}/switch-model` | POST | Switch agent model |
| `/mcp-logs` | GET | Get MCP protocol logs |
| `/agents/{agent_id}/metrics` | GET | Get agent performance metrics (real-time) |
| `/health` | GET | Health check |

#### 🤖 **MCP Agent Server Tools** (Ports 3001-3003)
*Individual agent MCP servers exposing tools for direct communication*

> **📝 MCP Tools**: These are **tools** (actions/operations) that agents can perform, representing capabilities like "analyze", "create", "execute".

### **🔍 Scout Agent MCP Server** (Port 3001)
The Scout agent analyzes the game board and identifies patterns, threats, and opportunities.

| Tool | Description | Parameters |
|------|-------------|------------|
| `analyze_board` | Analyze board state and provide comprehensive insights | `board`, `current_player`, `move_number` |
| `detect_threats` | Identify immediate threats from opponent | `board_state` |
| `identify_opportunities` | Find winning opportunities and strategic positions | `board_state` |
| `get_pattern_analysis` | Analyze game patterns and trends | `board_state`, `move_history` |

### **🧠 Strategist Agent MCP Server** (Port 3002)
The Strategist agent creates game plans and recommends optimal moves.

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_strategy` | Generate strategic plan based on Scout's analysis | `observation_data` |
| `evaluate_position` | Evaluate current position strength | `board_state`, `player` |
| `recommend_move` | Recommend best move with detailed reasoning | `board_state`, `available_moves` |
| `assess_win_probability` | Calculate win probability for current state | `board_state`, `player` |

### **⚡ Executor Agent MCP Server** (Port 3003)
The Executor agent validates and executes moves on the game board.

| Tool | Description | Parameters |
|------|-------------|------------|
| `execute_move` | Execute strategic move on the board | `move_data`, `board_state` |
| `validate_move` | Validate move legality and game rules | `move`, `board_state` |
| `update_game_state` | Update game state after move execution | `move`, `current_state` |
| `confirm_execution` | Confirm move execution and return results | `execution_result` |

### **🔄 Common Agent Tools** (All Ports)
All agents share these standard MCP capabilities:

| Tool | Description | Purpose |
|------|-------------|---------|
| `execute_task` | Execute CrewAI task via MCP protocol | Task execution |
| `get_status` | Get agent status and current state | Health monitoring |
| `get_memory` | Retrieve agent memory and context | State management |
| `switch_model` | Hot-swap LLM model without restart | Model switching |
| `get_metrics` | Get real-time performance metrics | Performance tracking |

**📚 [Complete Architecture & API Documentation](docs/ARCHITECTURE.md)** - Detailed architecture diagrams, communication flows, and complete API reference.

---

## 📊 Monitoring & Analytics

The Streamlit dashboard provides comprehensive monitoring with real-time analytics, performance tracking, and MCP protocol logging.

**📚 [Features Documentation](docs/FEATURES.md)** - Detailed monitoring capabilities, analytics, and feature status.

---

## 📄 License

This project is licensed under the **Apache License, Version 2.0** - see the [LICENSE](LICENSE) file for details. 