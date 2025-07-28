# Multi-Agent Game Simulation

A **Multi-Context Protocol (MCP) demonstration** featuring a turn-based strategy game where **three different LLMs work together** in isolated contexts. This project showcases how multiple AI models can collaborate through structured communication protocols - each agent runs on a different LLM (OpenAI GPT-4, Claude 3 Sonnet, and local Llama2:7B) and communicates only through standardized JSON schemas, demonstrating true MCP principles of model isolation and structured data flow.

## 🎮 Game Overview

The game is a 5x5 grid-based strategy game where:
- **Player** (P) starts at position (0,0) with 100 HP
- **Enemy** (E) is located at position (4,4) with 50 HP  
- **Items** (I) are scattered around the map
- **Walls** (#) create obstacles and strategic positioning opportunities

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
│ • Limited View  │    │ • Prioritizes   │    │ • Validates     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Game State Manager                           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Game Map    │  │ Game Engine │  │ Turn History│            │
│  │ (5x5 Grid)  │  │ (Mechanics) │  │ (Logging)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

#### 1. **Scout Agent** (OpenAI GPT-4)
- **Model**: OpenAI GPT-4 via OpenAI API
- **Role**: Environment observation and threat detection
- **Capabilities**:
  - Observes game environment with limited visibility (fog of war)
  - Detects enemies, items, and terrain features
  - Provides detailed analysis of current situation
  - Reports observations in structured format

#### 2. **Strategist Agent** (Claude 3 Sonnet)
- **Model**: Claude 3 Sonnet via Anthropic API
- **Role**: Strategic planning and decision making
- **Capabilities**:
  - Analyzes scout observations
  - Creates prioritized action plans
  - Assesses risks and opportunities
  - Provides alternative strategies

#### 3. **Executor Agent** (Llama2:7B)
- **Model**: Llama2:7B via Ollama (local)
- **Role**: Plan execution and game state updates
- **Capabilities**:
  - Validates plans before execution
  - Executes actions in priority order
  - Updates game state
  - Provides execution feedback

## 🔄 Protocol Flow

### Turn Execution Process

```
1. SCOUT OBSERVATION
   ┌─────────────────────────────────────┐
   │ Scout Agent observes environment    │
   │ • Limited visibility (3-tile range) │
   │ • Detects enemies, items, terrain   │
   │ • Creates detailed observation      │
   └─────────────────────────────────────┘
                    │
                    ▼
2. STRATEGIC PLANNING
   ┌─────────────────────────────────────┐
   │ Strategist Agent analyzes           │
   │ • Threat assessment                 │
   │ • Opportunity identification        │
   │ • Action prioritization             │
   │ • Risk evaluation                   │
   └─────────────────────────────────────┘
                    │
                    ▼
3. PLAN EXECUTION
   ┌─────────────────────────────────────┐
   │ Executor Agent executes plan        │
   │ • Validates actions                 │
   │ • Executes in priority order        │
   │ • Updates game state                │
   │ • Reports results                   │
   └─────────────────────────────────────┘
                    │
                    ▼
4. STATE UPDATE
   ┌─────────────────────────────────────┐
   │ Game State Manager updates          │
   │ • Advances turn counter             │
   │ • Checks win/lose conditions        │
   │ • Logs turn history                 │
   │ • Prepares for next turn            │
   └─────────────────────────────────────┘
```

### MCP Message Flow

```
Turn N:
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

### Actions Available

1. **Move** - Move in 8 directions (N, S, E, W, NE, NW, SE, SW)
2. **Attack** - Attack enemies within 1 tile range
3. **Pickup** - Collect items at current position
4. **Retreat** - Move away from enemies
5. **Wait** - Skip turn

### Combat System

- **Attack Range**: 1 tile (adjacent only)
- **Damage**: Base damage ± 20% variance
- **Health**: Enemies die at 0 HP
- **Victory**: Defeat all enemies
- **Defeat**: Player health reaches 0

### Map Features

- **5x5 Grid**: Bounded world
- **Walls**: Impassable obstacles
- **Fog of War**: Limited visibility (3-tile range)
- **Items**: Collectible resources
- **Enemies**: Hostile entities

## 🔍 Monitoring and Debugging

### MCP Protocol Logs

All agent communications are logged in JSON format:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "agent": "Scout",
  "message_type": "Observation",
  "data": {
    "scout_position": [0, 0],
    "enemies_in_range": [...],
    "items_in_range": [...],
    ...
  }
}
```

### Turn History

Each turn is logged with:
- Turn number
- Actions executed
- Success/failure rates
- Damage dealt/taken
- Items collected
- Enemies defeated

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
    ├── map.py          # Game map and entities
    ├── state.py        # Game state management
    └── engine.py       # Game mechanics and execution
```

### Adding New Features

1. **New Actions**: Add to `schemas/plan.py` ActionType enum
2. **New Agents**: Create new agent class in `agents/` directory
3. **New Game Mechanics**: Extend `game/engine.py`
4. **New Map Features**: Modify `game/map.py`

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

1. **Multiple Players**: Support for multiple player entities
2. **Enhanced Fog of War**: Dynamic visibility based on terrain
3. **Turn History Replay**: Visual replay of game turns
4. **Advanced AI**: More sophisticated agent decision making
5. **Custom Maps**: User-defined map layouts
6. **Real-time Multiplayer**: WebSocket support for live games

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
   - Enhanced threat detection
   - Pathfinding capabilities
   - Resource tracking

2. **Strategist Agent**:
   - Long-term planning
   - Risk assessment algorithms
   - Adaptive strategies

3. **Executor Agent**:
   - Action optimization
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