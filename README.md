# Multi-Agent Game Simulation

A turn-based strategy game simulation using CrewAI, FastAPI, and MCP-style architecture. The simulation features three independent agents working together to play a grid-based strategy game.

## 🎮 Game Overview

The game is a 5x5 grid-based strategy game where:
- **Player** (P) starts at position (0,0) with 100 HP
- **Enemy** (E) is located at position (4,4) with 50 HP  
- **Items** (I) are scattered around the map
- **Walls** (#) create obstacles and strategic positioning opportunities

## 🏗️ Architecture

### MCP-Style Multi-Agent System

The game uses a Multi-Context Protocol (MCP) style architecture with three specialized agents:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scout Agent   │    │ Strategist Agent│    │ Executor Agent  │
│   (Claude)      │───▶│   (Mistral)     │───▶│  (Llama2:7B)    │
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

#### 1. **Scout Agent** (Claude/GPT-4)
- **Model**: Claude (GPT-4) via OpenAI API
- **Role**: Environment observation and threat detection
- **Capabilities**:
  - Observes game environment with limited visibility (fog of war)
  - Detects enemies, items, and terrain features
  - Provides detailed analysis of current situation
  - Reports observations in structured format

#### 2. **Strategist Agent** (Mistral)
- **Model**: Mistral via Ollama
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
- OpenAI API key (for Claude/GPT-4)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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
   ollama pull mistral
   ollama pull llama2:7b
   ```

5. **Set environment variables**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
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

### Planned Features

1. **Multiple Players**: Support for multiple player entities
2. **Enhanced Fog of War**: Dynamic visibility based on terrain
3. **Turn History Replay**: Visual replay of game turns
4. **Advanced AI**: More sophisticated agent decision making
5. **Custom Maps**: User-defined map layouts
6. **Real-time Multiplayer**: WebSocket support for live games

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

This project is licensed under the MIT License - see the LICENSE file for details.

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