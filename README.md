# 🎮 Agentic Tic-Tac-Toe: MCP Protocol

[![YouTube Demo](https://img.shields.io/badge/YouTube-Demo%20Video-red?style=for-the-badge&logo=youtube)](https://youtu.be/6kMry-zlO3U)

A **Multi-Context Protocol (MCP) demonstration** featuring an interactive Tic Tac Toe game where **three AI agents work together** using **CrewAI** as the agent framework and **MCP** for distributed communication. This project showcases how multiple LLMs can collaborate through structured communication protocols - each agent runs as both a CrewAI Agent and an MCP Server.

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
- **[🐳 Docker Deployment](docs/DOCKER_README.md)** - Containerized deployment options
- **[⚡ GitHub Actions CI/CD](docs/GITHUB_ACTIONS_SETUP.md)** - Automated testing and deployment

### **📚 Documentation**
- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - System architecture and design
- **[📡 API Reference](docs/API.md)** - Complete API documentation and examples
- **[🎮 User Guide](docs/USER_GUIDE.md)** - Game experience and setup instructions
- **[🚀 Features](docs/FEATURES.md)** - Detailed feature explanations and capabilities
- **[🛠️ Development](docs/DEVELOPMENT.md)** - Development workflow and contribution guidelines

### **🔧 Development & Deployment**
- **Local Development**: Use the quickstart script or manual setup
- **Docker Deployment**: Containerized deployment with API key management
- **CI/CD Pipeline**: Automated testing, building, and Docker image publishing
- **Production Ready**: Security best practices and monitoring included

## 🔑 API Keys Setup

To use the AI agents, you'll need API keys for the LLM providers. See the **[User Guide](docs/USER_GUIDE.md)** for detailed setup instructions.

---

## 🏗️ Architecture

The system uses **MCP (Multi-Context Protocol)** for distributed communication between CrewAI agents. Each agent runs as both a CrewAI Agent and an MCP Server, enabling modular, scalable deployment.

**Key Components**:
- **🤖 MCP Agents**: Scout, Strategist, Executor (Ports 3001-3003)
- **🌐 FastAPI Server**: Main application server (Port 8000)
- **🎨 Streamlit UI**: Interactive game interface (Port 8501)
- **📡 MCP Coordinator**: Orchestrates agent communication

**📚 [Detailed Architecture Documentation](docs/ARCHITECTURE.md)** - Complete architecture diagrams, communication flows, and component details.

---

## 📡 API Architecture

The system has **two types of endpoints**:

### 🌐 **FastAPI Server Endpoints** (Port 8000)
*Main application server that coordinates everything*

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/state` | GET | Get current game state |
| `/make-move` | POST | Make a player move |
| `/reset-game` | POST | Reset game |
| `/agents/status` | GET | Get all agent status |
| `/agents/{agent_id}/switch-model` | POST | Switch agent model |
| `/mcp-logs` | GET | Get MCP protocol logs |
| `/agents/{agent_id}/metrics` | GET | Get agent performance metrics |
| `/health` | GET | Health check |

### 🤖 **MCP Agent Server Tools** (Ports 3001-3003)
*Individual agent MCP servers exposing tools for direct communication*

> **📝 MCP Tools**: These are **tools** (actions/operations) that agents can perform, representing capabilities like "analyze", "create", "execute".

**📚 [Complete API Documentation](docs/API.md)** - Detailed API reference with examples and MCP protocol details.

---

## 📊 Monitoring & Analytics

The Streamlit dashboard provides comprehensive monitoring with real-time analytics, performance tracking, and MCP protocol logging.

**📚 [Features Documentation](docs/FEATURES.md)** - Detailed monitoring capabilities, analytics, and feature status.

---

## 🛠️ Development

**📚 [Development Guide](docs/DEVELOPMENT.md)** - Complete development workflow, project structure, and contribution guidelines.

---

## 📄 License

This project is licensed under the **Apache License, Version 2.0** - see the [LICENSE](LICENSE) file for details. 