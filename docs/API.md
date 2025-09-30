# 📡 API Documentation

This document provides comprehensive information about the API architecture and endpoints for Agentic Tic-Tac-Toe with CrewAI and MCP.

## 📡 API Architecture

The system has **two types of endpoints**:

### 🌐 **FastAPI Server Endpoints** (Port 8000)
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

### 🤖 **MCP Agent Server Tools** (Ports 3001-3003)
*Individual agent MCP servers exposing tools for direct communication*

> **📝 MCP Tools**: These are **tools** (actions/operations) that agents can perform, representing capabilities like "analyze", "create", "execute".

#### **Scout Agent** (Port 3001)
| Tool | Description |
|------|-------------|
| `analyze_board` | Analyze board state and provide insights |
| `detect_threats` | Detect immediate threats on the board |
| `identify_opportunities` | Identify winning opportunities |
| `get_pattern_analysis` | Analyze game patterns and trends |

#### **Strategist Agent** (Port 3002)
| Tool | Description |
|------|-------------|
| `create_strategy` | Create strategic plan based on analysis |
| `evaluate_position` | Evaluate position strength and options |
| `recommend_move` | Recommend best move with reasoning |
| `assess_win_probability` | Assess win probability for current position |

#### **Executor Agent** (Port 3003)
| Tool | Description |
|------|-------------|
| `execute_move` | Execute strategic move on the board |
| `validate_move` | Validate move legality and constraints |
| `update_game_state` | Update game state after move |
| `confirm_execution` | Confirm move execution and results |

## 🔧 **Example Usage**

### **FastAPI Server (Main Application)**
```bash
# Get game state
curl http://localhost:8000/state

# Make a player move (AI responds automatically)
curl -X POST http://localhost:8000/make-move \
  -H "Content-Type: application/json" \
  -d '{"row": 0, "col": 0}'

# Trigger AI move manually (auto-called by frontend)
curl -X POST http://localhost:8000/ai-move

# Get agent status
curl http://localhost:8000/agents/status

# Get real-time metrics for Scout agent
curl http://localhost:8000/agents/scout/metrics

# Switch Scout agent model
curl -X POST http://localhost:8000/agents/scout/switch-model \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4"}'

# Get MCP logs
curl http://localhost:8000/mcp-logs
```

### **MCP Agent Servers (Direct Tool Access)**
```bash
# Connect to Scout Agent via MCP Inspector to access tools
npx @modelcontextprotocol/inspector node agents/scout.py

# Connect to Strategist Agent via MCP Inspector to access tools
npx @modelcontextprotocol/inspector node agents/strategist.py

# Connect to Executor Agent via MCP Inspector to access tools
npx @modelcontextprotocol/inspector node agents/executor.py
```

## 🤖 MCP Protocol Architecture

The project uses **MCP (Multi-Context Protocol)** for distributed communication between CrewAI agents:

### **🤖 MCP Agents**
- **Scout Agent** - Board analysis with MCP endpoints (Port 3001)
- **Strategist Agent** - Strategy creation with MCP endpoints (Port 3002)  
- **Executor Agent** - Move execution with MCP endpoints (Port 3003)
- **MCP Game Coordinator** - Orchestrates agent communication via MCP protocol

### **🔗 MCP Communication Flow**
```
Player Move → MCP Coordinator → Scout Agent (MCP) → Strategist Agent (MCP) → Executor Agent (MCP) → Game State Update
```

### **🔧 MCP Inspector Integration**

Connect to each agent's MCP server for debugging:

```bash
# Connect to Scout Agent
npx @modelcontextprotocol/inspector node agents/scout.py

# Connect to Strategist Agent  
npx @modelcontextprotocol/inspector node agents/strategist.py

# Connect to Executor Agent
npx @modelcontextprotocol/inspector node agents/executor.py
```

### **🎯 Architecture Benefits**

#### **Modularity**
- Each agent can be developed and deployed independently
- Agents communicate via standardized MCP protocol
- Easy to add new agents or modify existing ones

#### **Scalability**
- Agents can run on different machines
- Load balancing across multiple agent instances
- Horizontal scaling of agent capabilities

#### **Flexibility**
- Hot-swap agents or models without restarting the entire system
- Runtime configuration changes via MCP endpoints
- Language-agnostic agent development

#### **Monitoring**
- Rich metrics and monitoring via MCP endpoints
- Real-time agent performance tracking
- Comprehensive logging of agent communications

## 📚 Related Documentation

- **[Architecture Documentation](ARCHITECTURE.md)** - Complete architecture diagrams, communication flows, and component details
- **[Development Guide](DEVELOPMENT.md)** - Development workflow, debugging, and contribution guidelines
- **[Base MCP Agent](../agents/base_mcp_agent.py)** - Base MCP Agent implementation
- **[MCP Game Coordinator](../game/mcp_coordinator.py)** - MCP protocol coordination
- **[Scout Agent](../agents/scout.py)** - Scout MCP Agent implementation
- **[Strategist Agent](../agents/strategist.py)** - Strategist MCP Agent implementation
- **[Executor Agent](../agents/executor.py)** - Executor MCP Agent implementation
