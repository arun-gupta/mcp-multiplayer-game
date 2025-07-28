# Multi-Agent Game Simulation

A **Multi-Context Protocol (MCP) demonstration** featuring a turn-based strategy game where **three different LLMs work together** in isolated contexts. This project showcases how multiple AI models can collaborate through structured communication protocols - each agent runs on a different LLM (OpenAI GPT-4, Claude 3 Sonnet, and local Llama2:7B) and communicates only through standardized JSON schemas, demonstrating true MCP principles of model isolation and structured data flow.

## 🎮 Game Overview

The game is an **interactive Tic Tac Toe** where you play against three AI agents working together:

- **Game Format**: Classic 3x3 Tic Tac Toe
- **Player**: You play as X against the AI team
- **AI Team**: Three specialized AI agents working together
  - **Scout Agent** (OpenAI GPT-4): Analyzes board state and threats
  - **Strategist Agent** (Claude 3 Sonnet): Creates strategic plans
  - **Executor Agent** (Llama2:7B): Executes the chosen move
- **Objective**: Get three X's in a row (horizontally, vertically, or diagonally)

### 🎯 How It Works

1. **You click** any empty cell to place your X
2. **Scout Agent** observes the current board state and identifies threats/opportunities
3. **Strategist Agent** analyzes the board and creates a strategic plan
4. **Executor Agent** executes the AI's move (places O)
5. **Game continues** until someone wins or it's a draw

### 🏆 Victory Conditions

- **Player Win**: Three X's in a row (horizontally, vertically, or diagonally)
- **AI Win**: Three O's in a row (horizontally, vertically, or diagonally)
- **Draw**: All 9 cells filled with no winner

## 🚀 QuickStart

**Get the Multi-Agent Game Simulation running in 5 minutes!**

👉 **[📖 Quick Start Guide](QUICKSTART.md)** - Complete setup and usage instructions

The QuickStart guide includes:
- ✅ **Prerequisites** and dependencies
- ✅ **Step-by-step setup** commands
- ✅ **How to play** the game
- ✅ **API testing** examples
- ✅ **Troubleshooting** common issues

For detailed setup instructions and troubleshooting, see the [Full Setup Guide](#-setup-instructions) below.

## 🏗️ Architecture

### MCP-Style Multi-Agent System

The game uses a Multi-Context Protocol (MCP) style architecture with three specialized agents:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scout Agent   │    │ Strategist Agent│    │ Executor Agent  │
│  (OpenAI GPT-4) │───▶│  (Claude 3)     │───▶│  (Llama2:7B)    │
│                 │    │                 │    │                 │
│ • Observes      │    │ • Analyzes      │    │ • Executes      │
│ • Reports       │    │ • Plans         │    │ • Updates       │
│ • Pattern Rec.  │    │ • Prioritizes   │    │ • Validates     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Game State Manager                           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Game State  │  │ Game Engine │  │ Move History│            │
│  │ (RPS Logic) │  │ (RPS Rules) │  │ (Logging)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

#### 1. **Scout Agent** (OpenAI GPT-4)
- **Model**: OpenAI GPT-4 via OpenAI API
- **Role**: Game state observation and pattern analysis
- **Capabilities**:
  - Observes current game state and score
  - Analyzes opponent's move history and patterns
  - Tracks win/loss streaks and game progress
  - Reports observations in structured format

#### 2. **Strategist Agent** (Claude 3 Sonnet)
- **Model**: Claude 3 Sonnet via Anthropic API
- **Role**: Strategic planning and move selection
- **Capabilities**:
  - Analyzes opponent patterns from scout observations
  - Creates strategic plans for next move (Rock/Paper/Scissors)
  - Assesses confidence levels and risks
  - Provides alternative strategies as backups

#### 3. **Executor Agent** (Llama2:7B)
- **Model**: Llama2:7B via Ollama (local)
- **Role**: Move execution and result processing
- **Capabilities**:
  - Executes the chosen move (Rock/Paper/Scissors)
  - Generates opponent's move
  - Determines round winner
  - Updates game state and score

## 🔄 Protocol Flow

### Round Execution Process

```
1. SCOUT OBSERVATION
   ┌─────────────────────────────────────┐
   │ Scout Agent observes game state     │
   │ • Current score and round number    │
   │ • Opponent's move history           │
   │ • Win/loss streaks and patterns     │
   └─────────────────────────────────────┘
                    │
                    ▼
2. STRATEGIC PLANNING
   ┌─────────────────────────────────────┐
   │ Strategist Agent analyzes           │
   │ • Opponent pattern analysis         │
   │ • Move selection strategy           │
   │ • Confidence assessment             │
   │ • Alternative strategies            │
   └─────────────────────────────────────┘
                    │
                    ▼
3. MOVE EXECUTION
   ┌─────────────────────────────────────┐
   │ Executor Agent executes move        │
   │ • Chooses Rock/Paper/Scissors       │
   │ • Generates opponent's move         │
   │ • Determines round winner           │
   │ • Updates score                     │
   └─────────────────────────────────────┘
                    │
                    ▼
4. STATE UPDATE
   ┌─────────────────────────────────────┐
   │ Game State Manager updates          │
   │ • Advances round counter            │
   │ • Checks tournament end             │
   │ • Logs move history                 │
   │ • Prepares for next round           │
   └─────────────────────────────────────┘
```

### MCP Message Flow

```
Round N:
├── Scout → Observation (JSON)
├── Strategist → Plan (JSON)
├── Executor → ExecutionResult (JSON)
└── GameEngine → StateUpdate (JSON)

Each message is logged with timestamp and agent identifier
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- Ollama (for local models)
- OpenAI API key (for Scout Agent)
- Anthropic API key (for Strategist Agent)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/arun-gupta/mcp-multiplayer-game.git
   cd mcp-multiplayer-game
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama models**
   ```bash
   ollama pull llama2:7b
   ```

5. **Set environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit the .env file and add your API keys
   # Replace the placeholder values with your actual API keys:
   # OPENAI_API_KEY=your-actual-openai-api-key-here
   # ANTHROPIC_API_KEY=your-actual-anthropic-api-key-here
   ```

6. **Test the installation**
   ```bash
   python test_installation.py
   ```

### Running the Application

1. **Start the server**
   ```bash
   python main.py
   ```

2. **Access the application**
   - Web Dashboard: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📡 API Endpoints

### Core Endpoints

- `GET /` - Game dashboard with visualization
- `GET /state` - Current game state
- `POST /simulate-turn` - Simulate a complete game turn
- `GET /agents` - Information about all agents
- `GET /mcp-logs` - MCP protocol message logs
- `POST /reset-game` - Reset game to initial state

### Example API Usage

```bash
# Get current game state
curl http://localhost:8000/state

# Simulate a turn
curl -X POST http://localhost:8000/simulate-turn

# Get agent information
curl http://localhost:8000/agents

# Reset the game
curl -X POST http://localhost:8000/reset-game
```

## 🎯 Game Mechanics

### Board Layout

- **3x3 Grid**: Classic Tic Tac Toe board
- **Player Symbol**: X (green color)
- **AI Symbol**: O (red color)
- **Empty Cells**: Available for moves

### Game Rules

- **Player Goes First**: You always start with X
- **Alternating Turns**: Player (X) → AI (O) → Player (X) → etc.
- **Win Condition**: Three of your symbols in a row (horizontal, vertical, or diagonal)
- **Draw Condition**: All 9 cells filled with no winner

### AI Strategy Features

- **Threat Detection**: AI identifies immediate win opportunities
- **Blocking Moves**: AI blocks your potential winning moves
- **Strategic Planning**: AI creates multiple move strategies with confidence levels
- **Board Analysis**: Real-time analysis of board state and game phase
- **Adaptive Play**: AI adjusts strategy based on game progression

## 🔍 Monitoring and Debugging

### MCP Protocol Logs

All agent communications are logged in JSON format:

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
    "blocking_moves": [...],
    ...
  }
}
```

### Move History

Each move is logged with:
- Move number
- Player (X) or AI (O) move
- Board position (row, col)
- Board state after move
- Game phase (opening, midgame, endgame)

### Agent Performance

Monitor agent performance through:
- `/agents` endpoint for agent capabilities
- `/mcp-logs` for communication flow
- Turn history for execution success rates

## 🛠️ Development

### Project Structure

```
mcp-multiplayer-game/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── schemas/               # MCP-style communication schemas
│   ├── __init__.py
│   ├── observation.py     # Scout observations
│   ├── plan.py           # Strategist plans
│   └── action_result.py  # Executor results
├── agents/               # CrewAI agent implementations
│   ├── __init__.py
│   ├── scout.py         # Scout agent (Claude)
│   ├── strategist.py    # Strategist agent (Mistral)
│   └── executor.py      # Executor agent (Llama2:7B)
└── game/                # Game logic and state
    ├── __init__.py
    └── state.py        # Tic Tac Toe game state management
```

### Adding New Features

1. **New Board Sizes**: Modify `game/state.py` board dimensions
2. **New Agents**: Create new agent class in `agents/` directory
3. **New Game Mechanics**: Extend `game/state.py` game logic
4. **New Game Modes**: Add different game variations to `game/state.py`

### Testing

```bash
# Run the application
python main.py

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/state
curl -X POST http://localhost:8000/simulate-turn
```

## 🔮 Future Enhancements

### 🎮 Game Features & Improvements

1. **Multiple Opponents**: Support for different AI opponent personalities
2. **Tournament Modes**: Best of 3, 5, 7, or custom round counts
3. **Move History Replay**: Visual replay of game rounds
4. **Advanced AI**: More sophisticated pattern recognition and strategy
5. **Custom Rules**: User-defined Rock-Paper-Scissors variants
6. **Real-time Multiplayer**: WebSocket support for live tournaments

### 🔄 MCP Protocol Features

7. **Hot-Swappable LLMs**: Dynamic LLM replacement between games
   - **Runtime Model Switching**: Swap out any agent's LLM without restarting the game
   - **Model Registry**: Centralized registry of available LLMs (OpenAI, Anthropic, Ollama, local models)
   - **Performance Comparison**: A/B test different models for each agent role
   - **Configuration API**: REST endpoints to change agent models on-the-fly
   - **Model Validation**: Automatic compatibility checking for new models
   - **Preset Configurations**: Save and load different LLM combinations

8. **Protocol Versioning & Schema Evolution**: MCP protocol enhancements
   - **Version Headers**: Protocol version tracking in all messages
   - **Schema Registry**: Centralized schema management with versioning
   - **Backward Compatibility**: Support for multiple schema versions simultaneously
   - **Migration Tools**: Automatic schema migration between versions
   - **Deprecation Warnings**: Notify when using deprecated schemas

9. **Enhanced Observability & Monitoring**: Comprehensive system visibility
   - **MCP Metrics Dashboard**: Real-time protocol performance monitoring
   - **Message Latency Tracking**: Monitor communication delays between agents
   - **Schema Validation Metrics**: Track validation success/failure rates
   - **Agent Performance Analytics**: Response times and error rates per agent
   - **Throughput Monitoring**: Messages per second and system capacity
   - **Error Rate Tracking**: Monitor and alert on communication failures
   - **Distributed Tracing**: Track message flow across the entire system

10. **Multi-Protocol Support**: Flexible communication options
    - **WebSocket Integration**: Real-time bidirectional communication
    - **gRPC Endpoints**: High-performance RPC communication
    - **GraphQL API**: Flexible querying of game state and agent data
    - **Event Streaming**: Kafka/RabbitMQ for event-driven architecture
    - **Protocol Adapters**: Seamless switching between communication protocols
    - **Load Balancing**: Distribute load across multiple protocol endpoints

### Agent Improvements

1. **Scout Agent**: 
   - Enhanced pattern recognition
   - Opponent behavior analysis
   - Statistical trend detection

2. **Strategist Agent**:
   - Advanced strategy algorithms
   - Machine learning pattern recognition
   - Adaptive confidence scoring

3. **Executor Agent**:
   - Move optimization
   - Error recovery
   - Performance monitoring

## 📄 License

This project is licensed under the Apache License, Version 2.0 - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the MCP logs for debugging

---

**Happy Gaming! 🎮** 