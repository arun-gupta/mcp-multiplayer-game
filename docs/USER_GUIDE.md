# 🎮 User Guide

This guide provides comprehensive information for users of the MCP Protocol Tic Tac Toe game.

## 🔑 API Keys Setup

To use the AI agents, you'll need API keys for the LLM providers:

### **OpenAI API Key** (Required for Scout Agent)
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Add to your `.env` file: `OPENAI_API_KEY=sk-your-key-here`

### **Anthropic API Key** (Required for Strategist Agent)
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign in or create an account
3. Click "Create Key"
4. Copy the key (starts with `sk-ant-`)
5. Add to your `.env` file: `ANTHROPIC_API_KEY=sk-ant-your-key-here`

### **Local Models** (Optional - for Executor Agent)
- Install [Ollama](https://ollama.ai/) for local model support
- Pull models: `ollama pull llama2:7b mistral:latest`
- No API keys required for local models

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
| **Scout** | Available Model | Observer | Board analysis, threat detection, pattern recognition |
| **Strategist** | Available Model | Planner | Strategic planning, move selection, confidence assessment |
| **Executor** | Available Model | Executor | Move execution, validation, state updates |

### Victory Conditions

- **Player Win**: Three X's in a row (horizontal, vertical, or diagonal)
- **AI Win**: Three O's in a row (horizontal, vertical, or diagonal)  
- **Draw**: All 9 cells filled with no winner

## 🎯 Game Features

### Interactive Gameplay
- **Real-time Updates**: See the AI team's decision-making process
- **Move History**: Track all moves and AI reasoning
- **Model Switching**: Change AI models mid-game without restart
- **Performance Analytics**: Monitor agent response times and performance

### AI Team Capabilities
- **Scout Agent**: Analyzes board state, detects threats, identifies opportunities
- **Strategist Agent**: Creates strategic plans, evaluates positions, recommends moves
- **Executor Agent**: Executes moves, validates decisions, updates game state

### Hot-Swappable Models
- **Runtime Switching**: Change which LLM each agent uses without restart
- **Performance Comparison**: A/B test different models for each role
- **Cost Optimization**: Switch between expensive cloud and free local models
- **Specialization**: Use different models optimized for specific tasks

## 📊 Monitoring & Analytics

### Real-time Dashboard
The Streamlit dashboard provides comprehensive monitoring:

- **🎮 Game Tab**: Interactive game board and move history
- **🤖 AI Agents & Models**: Agent information and model switching
- **📡 MCP Logs**: Real-time protocol communication logs
- **📊 Analytics**: Performance analytics and system monitoring

### Key Metrics Tracked
- **Response Times**: Per-agent performance tracking
- **Message Latency**: Inter-agent communication latency
- **Token Usage**: LLM consumption per agent
- **Model Switches**: History of model changes
- **Resource Utilization**: System CPU and memory usage
- **LLM Costs**: Real-time cost tracking per model

## 🚀 Getting Started

### Quick Start
1. **Clone the repository**: `git clone https://github.com/arungupta/mcp-multiplayer-game.git`
2. **Run the setup**: `./quickstart.sh`
3. **Access the game**: http://localhost:8501
4. **API Documentation**: http://localhost:8000/docs

### Manual Setup
1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set up API keys**: Add your OpenAI and Anthropic API keys to `.env`
3. **Start the backend**: `python main.py`
4. **Start the frontend**: `python run_streamlit.py`

## 🔧 Troubleshooting

### Common Issues
- **API Key Errors**: Ensure your `.env` file contains valid API keys
- **Port Conflicts**: Make sure ports 8000 and 8501 are available
- **Model Loading**: Check that your selected models are available and accessible
- **Connection Issues**: Verify that all services are running and accessible

### Getting Help
- **Documentation**: Check the [README](../README.md) for quick start instructions
- **API Documentation**: Visit http://localhost:8000/docs for API details
- **Issues**: Report problems on the GitHub repository
- **Community**: Join discussions in the project's community channels

## 📚 Related Documentation

- **[Features Documentation](FEATURES.md)** - Detailed feature explanations and capabilities
- **[API Documentation](API.md)** - Complete API reference and examples
- **[Architecture Documentation](ARCHITECTURE.md)** - System architecture and design
- **[Development Guide](DEVELOPMENT.md)** - Development workflow and contribution guidelines
