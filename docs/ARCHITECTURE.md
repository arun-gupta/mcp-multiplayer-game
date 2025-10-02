# 🏗️ MCP Protocol Architecture

## Overview

This document describes the detailed architecture of the MCP Protocol Tic Tac Toe game, showing how CrewAI agents work together with MCP protocol as a standardized API layer.

**Key Innovation**: Each agent is simultaneously a **CrewAI Agent** (providing intelligence) and an **MCP Server** (providing standardized API), creating a hybrid architecture that combines agentic AI with protocol-based interfaces.

**Important**: MCP is used as an **API specification and external interface**, not as the internal transport protocol. Agents communicate internally via direct Python method calls for performance, while exposing MCP-compliant HTTP/JSON-RPC endpoints for external clients.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    External Clients (MCP Protocol)                              │
│          (curl, MCP Inspector, Monitoring Tools, Web Browsers)                  │
└────────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 │ HTTP/JSON-RPC (MCP Protocol)
                                 │ • GET /mcp/{id} - Discovery
                                 │ • POST /mcp/{id} - Tool calls
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Server (Port 8000)                             │
│                                                                                 │
│  MCP Endpoints (External Interface):                                           │
│  • GET  /mcp/scout      → Full MCP discovery (tools+resources+prompts)        │
│  • POST /mcp/scout      → JSON-RPC 2.0 calls (tools/call, resources/read)     │
│  • GET  /mcp/strategist → Full MCP discovery                                   │
│  • POST /mcp/strategist → JSON-RPC 2.0 calls                                   │
│  • GET  /mcp/executor   → Full MCP discovery                                   │
│  • POST /mcp/executor   → JSON-RPC 2.0 calls                                   │
│                                                                                 │
│  Game Endpoints:                                                                │
│  • GET  /state          → Game state                                           │
│  • POST /make-move      → Player move                                          │
│  • POST /ai-move        → Trigger AI move                                      │
│  • POST /reset-game     → Reset game                                           │
│                                                                                 │
│  Agent Endpoints:                                                               │
│  • GET  /agents/status            → All agent status                           │
│  • POST /agents/{id}/switch-model → Hot-swap LLM model                         │
│  • GET  /agents/{id}/metrics      → Real-time performance metrics              │
│  • GET  /mcp-logs                 → MCP protocol communication logs            │
└────────────────────────────────┬────────────────────────────────────────────────┘
                                 │
                                 │ Direct Python Calls (In-Process)
                                 │ • agent.tools_registry[name]['handler'](args)
                                 │ • agent.analyze_board(data)
                                 │ • agent.llm.call(prompt)
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    Agent Instances (Same Python Process)                        │
│                                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐           │
│  │   Scout Agent   │    │ Strategist Agent│    │ Executor Agent  │           │
│  │                 │    │                 │    │                 │           │
│  │ 🤖 CrewAI Agent │    │ 🤖 CrewAI Agent │    │ 🤖 CrewAI Agent │           │
│  │ + MCP Metadata  │    │ + MCP Metadata  │    │ + MCP Metadata  │           │
│  │                 │    │                 │    │                 │           │
│  │ • LLM (GPT-5)   │    │ • LLM (GPT-5)   │    │ • LLM (GPT-5)   │           │
│  │ • Tools (8)     │    │ • Tools (8)     │    │ • Tools (8)     │           │
│  │ • Resources(3)  │    │ • Resources(3)  │    │ • Resources(3)  │           │
│  │ • Prompts (4)   │    │ • Prompts (4)   │    │ • Prompts (4)   │           │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘           │
│                                                                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐   │
│  │              MCP Coordinator (Game Orchestration)                      │   │
│  │  • Game State Management                                               │   │
│  │  • Agent Pipeline (Scout → Strategist → Executor)                     │   │
│  │  • Optimization Logic (blocking/winning move detection)               │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTP API
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (Port 8501)                                 │
│  • Interactive Game Board                                                       │
│  • Real-time Agent Monitoring                                                   │
│  • Performance Metrics Dashboard                                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Key Architectural Patterns

### 1. Hybrid Agent Pattern (CrewAI + MCP Server)

Each agent inherits from both `Agent` (CrewAI) and exposes MCP Server capabilities:

```python
class BaseMCPAgent(Agent, ABC):
    """Combines CrewAI Agent capabilities with MCP Server communication"""

    def __init__(self, ...):
        # Initialize CrewAI Agent
        Agent.__init__(self, role, goal, backstory, memory=True, ...)

        # Add MCP Server
        self.__dict__['mcp_server'] = Server(f"{agent_id}-mcp-server")
        self.__dict__['tools_registry'] = {}
        self.__dict__['resources_registry'] = {}
        self.__dict__['prompts_registry'] = {}
```

**Benefits**:
- ✅ Leverages CrewAI's LLM integration (GPT-5, Claude, Llama)
- ✅ Standardized MCP API for external clients
- ✅ Registry-based discovery (tools, resources, prompts)
- ✅ Future-ready for distributed deployment

**Important**: The MCP Server object defines the API contract (tools, resources, prompts) but doesn't run as a separate HTTP server. Internal communication uses direct Python method calls for performance.

### 2. Registry-Based Discovery

Three separate registries enable dynamic capability discovery:

```python
tools_registry = {
    "analyze_board": {handler, description, inputSchema},
    "get_status": {handler, description, inputSchema},
    ...
}

resources_registry = {
    "agent://scout/metrics": {name, description, getter, mimeType},
    "agent://scout/status": {name, description, getter, mimeType},
    ...
}

prompts_registry = {
    "execute_task_prompt": {description, generator, arguments},
    ...
}
```

**Benefits**:
- ✅ Single GET request shows all capabilities
- ✅ Dynamic tool registration at runtime
- ✅ Separation of concerns (tools ≠ resources ≠ prompts)

### 3. MCP as External API (Not Internal Transport)

**External clients use MCP protocol:**
```
External Client → HTTP/JSON-RPC (MCP) → FastAPI → Agent metadata
```

**Internal communication bypasses MCP:**
```
Coordinator → Direct Python calls → Agent methods
FastAPI → Direct object access → Agent.tools_registry[name]['handler']
```

**Why this design:**
- ✅ **External**: Standard MCP API for discovery, tools, monitoring
- ✅ **Internal**: Fast direct calls, no network overhead
- ✅ **Pragmatic**: Protocol-first API, performance-first implementation
- ✅ **Flexible**: Can switch to real MCP transport when distributing agents

**Example:**
```python
# External client (uses MCP)
curl -X POST http://localhost:8000/mcp/scout \
  -d '{"method":"tools/call","params":{"name":"analyze_board"}}'

# Internal coordinator (bypasses MCP)
result = await scout_agent.analyze_board(data)  # Direct Python call
```

### 4. Full MCP Protocol Implementation

Implements all three MCP primitives:

**Tools** (8 per agent):
- Agent-specific: `analyze_board`, `detect_threats`, `create_strategy`, etc.
- Common: `execute_task`, `get_status`, `get_memory`, `get_metrics`

**Resources** (3 per agent):
- `agent://{id}/status` - Current status and configuration
- `agent://{id}/metrics` - Real-time performance metrics
- `agent://{id}/memory` - Agent memory and history

**Prompts** (4 per agent):
- `execute_task_prompt` - Task execution templates
- Agent-specific prompts for specialized operations

### 5. Per-Agent Metrics Tracking

Each agent independently tracks:

```python
Metrics = {
    "request_count": int,
    "avg_response_time": float,
    "min_response_time": float,
    "max_response_time": float,
    "total_tokens": int,
    "api_success_rate": float,
    "api_error_count": int,
    "timeout_count": int,
    "current_model": str,
    "memory_usage": float
}
```

**Benefits**:
- ✅ A/B testing different models per agent
- ✅ Fine-grained performance monitoring
- ✅ Resource attribution and cost tracking
- ✅ Real-time performance visualization

### 6. Hot-Swappable LLM Models

Change underlying models without restarting:

```bash
POST /agents/scout/switch-model
{
  "model": "gpt-4"
}
```

**Benefits**:
- ✅ Zero-downtime model changes
- ✅ Runtime experimentation
- ✅ Cost optimization (switch to cheaper models)
- ✅ Performance comparison across models

## Component Details

### Scout Agent
**Role**: Board analysis and threat detection

**CrewAI Capabilities**:
- Pattern recognition using LLM reasoning
- Memory of previous games and strategies
- Context-aware board analysis

**MCP Tools** (8 total):
- `analyze_board` - Comprehensive board state analysis
- `detect_threats` - Identify immediate opponent threats
- `identify_opportunities` - Find winning opportunities
- `get_pattern_analysis` - Analyze game patterns and trends
- `execute_task` - Execute CrewAI tasks
- `get_status` - Agent status
- `get_memory` - Agent memory
- `get_metrics` - Performance metrics

**MCP Resources**:
- `agent://scout/status` - Current status, model, configuration
- `agent://scout/metrics` - Real-time performance data
- `agent://scout/memory` - Conversation history

**MCP Endpoint**: `http://localhost:8000/mcp/scout`

---

### Strategist Agent
**Role**: Strategic planning and move recommendation

**CrewAI Capabilities**:
- Strategic thinking and long-term planning
- Position evaluation using LLM
- Move recommendation with reasoning

**MCP Tools** (8 total):
- `create_strategy` - Generate strategic plan from analysis
- `evaluate_position` - Evaluate position strength
- `recommend_move` - Recommend best move with reasoning
- `assess_win_probability` - Calculate win probability
- `execute_task` - Execute CrewAI tasks
- `get_status` - Agent status
- `get_memory` - Agent memory
- `get_metrics` - Performance metrics

**MCP Resources**:
- `agent://strategist/status` - Current status, model, configuration
- `agent://strategist/metrics` - Real-time performance data
- `agent://strategist/memory` - Conversation history

**MCP Endpoint**: `http://localhost:8000/mcp/strategist`

---

### Executor Agent
**Role**: Move execution and validation

**CrewAI Capabilities**:
- Precise move execution
- Validation logic and rule checking
- Game state management

**MCP Tools** (8 total):
- `execute_move` - Execute move on the board
- `validate_move` - Validate move legality
- `update_game_state` - Update game state after move
- `confirm_execution` - Confirm move execution with results
- `execute_task` - Execute CrewAI tasks
- `get_status` - Agent status
- `get_memory` - Agent memory
- `get_metrics` - Performance metrics

**MCP Resources**:
- `agent://executor/status` - Current status, model, configuration
- `agent://executor/metrics` - Real-time performance data
- `agent://executor/memory` - Conversation history

**MCP Endpoint**: `http://localhost:8000/mcp/executor`

---

### MCP Game Coordinator
**Role**: Orchestrates multi-agent communication and game flow

**Responsibilities**:
- Manages game state (board, current player, move history)
- Routes moves through agent pipeline
- Implements optimization logic:
  - Direct blocking of opponent winning moves
  - Direct execution of agent winning moves
  - Full pipeline for complex positions
- Tracks MCP protocol communication logs
- Coordinates agent responses with timeout handling

**Architecture**:
```python
class MCPGameCoordinator:
    def coordinate_ai_move(self):
        # 1. Check for immediate winning move
        # 2. Check for blocking opponent win
        # 3. If neither, use full agent pipeline:
        #    Scout → Strategist → Executor
```

---

### FastAPI Server (Port 8000)
**Role**: Main application server and MCP transport layer

**Key Features**:
- Unified MCP endpoint for all agents
- JSON-RPC 2.0 protocol implementation
- GET discovery endpoint (tools + resources + prompts)
- Game state management
- Agent status and metrics
- CORS support for web access

**MCP Implementation**:
```python
@app.get("/mcp/{agent_id}")  # Full discovery
@app.post("/mcp/{agent_id}") # JSON-RPC calls
```

---

### Streamlit UI (Port 8501)
**Role**: Interactive user interface and monitoring dashboard

**Features**:
- Interactive Tic-Tac-Toe game board
- Real-time agent status monitoring
- MCP protocol log visualization
- Performance metrics dashboard
- Model switching interface
- Move history tracking

## Communication Flow

### Player Move Flow
```
1. Player clicks cell in Streamlit UI
2. POST /make-move → FastAPI
3. Update game state
4. If game not over → Trigger AI move
5. Return updated state to UI
```

### AI Move Flow (Optimized)
```
1. POST /ai-move → FastAPI
2. MCPGameCoordinator.coordinate_ai_move()
3. Check for winning move:
   ├─ If found → Execute directly
   └─ If not → Check for blocking move:
      ├─ If found → Execute block
      └─ If not → Full agent pipeline (Direct Python Calls):

         Scout Analysis:
         • await scout_agent.analyze_board(data)  # Direct method call
         • scout_agent.llm.call(prompt)           # Direct LLM call
         • Returns: threats, opportunities, available moves

         ↓

         Strategist Planning:
         • await strategist_agent.create_strategy(data)  # Direct method call
         • strategist_agent.llm.call(prompt)             # Direct LLM call
         • Returns: recommended move with reasoning

         ↓

         Executor Validation:
         • await executor_agent.execute_move(data)  # Direct method call
         • executor_agent.llm.call(prompt)          # Direct LLM call
         • Returns: move execution result

4. Update game state with AI move
5. Track metrics on each agent
6. Return updated state to UI

Note: Internal coordination uses direct Python calls, NOT HTTP/JSON-RPC.
      MCP protocol is only used by external clients accessing /mcp endpoints.
```

### MCP Discovery Flow
```
1. GET /mcp/scout
2. FastAPI retrieves agent registries:
   • tools_registry
   • resources_registry
   • prompts_registry
3. Returns complete MCP server info:
   • serverInfo (name, version, transport)
   • capabilities (supported features + counts)
   • tools (array of all available tools)
   • resources (array of all resources)
   • prompts (array of all prompts)
```

## Data Flow Diagrams

### Agent Communication via MCP Protocol

**Internal communication bypasses MCP:**
```
┌──────────────┐
│ FastAPI      │
│ Receives     │
│ JSON-RPC     │
│ Request      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Parse JSON-RPC Request               │
│ {                                    │
│   "jsonrpc": "2.0",                 │
│   "id": 1,                          │
│   "method": "tools/call",           │
│   "params": {                       │
│     "name": "analyze_board",       │
│     "arguments": {...}             │
│   }                                  │
│ }                                    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Get Agent from Registry              │
│ agent = scout_agent                  │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Lookup Tool in Registry              │
│ tool = agent.tools_registry[name]    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Execute Tool Handler                 │
│ result = await handler(arguments)    │
│                                      │
│ • Tracks metrics (time, tokens)     │
│ • Uses CrewAI for LLM calls         │
│ • Returns structured result         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Return JSON-RPC Response             │
│ {                                    │
│   "jsonrpc": "2.0",                 │
│   "id": 1,                          │
│   "result": {...}                   │
│ }                                    │
└──────────────────────────────────────┘
```

## Configuration

### Model Configuration
The system uses a model factory pattern with environment-based fallbacks:

```python
Priority Order (all agents):
1. GPT-5 models (gpt-5, gpt-5-mini) - if OPENAI_API_KEY present
2. Llama 3.2 (llama3.2:3b) - if Ollama running
3. Other cloud models (GPT-4, Claude) - if API keys present
4. Other local models - if Ollama running
```

### Port Configuration
All ports are configurable via `config.json`:

```json
{
  "mcp": {
    "ports": {
      "scout": 3001,      // Logical port (not used)
      "strategist": 3002, // Logical port (not used)
      "executor": 3003    // Logical port (not used)
    }
  },
  "api": {
    "port": 8000          // Actual FastAPI port
  },
  "streamlit": {
    "port": 8501          // Streamlit UI port
  }
}
```

**Note**: MCP port numbers are logical identifiers only. All MCP communication happens through the unified FastAPI server at port 8000.

## Benefits

### Modularity
- Each agent is independently developed and tested
- Registry-based tool discovery enables dynamic capabilities
- Clear separation between CrewAI logic and MCP protocol
- Easy to add new agents or modify existing ones

### Observability
- Per-agent metrics for performance tracking
- MCP protocol logs for debugging
- Real-time monitoring via Streamlit dashboard
- Request tracing through the entire pipeline

### Flexibility
- Hot-swap LLM models without restart
- Runtime tool registration
- Multiple model support (OpenAI, Anthropic, Ollama)
- Environment-based configuration

### Standards Compliance
- Full MCP protocol implementation (Tools + Resources + Prompts)
- JSON-RPC 2.0 for method calls
- HTTP transport for universal access
- Compatible with MCP Inspector and other MCP tools

### Developer Experience
- Single GET request shows all capabilities
- No authentication required for exploration
- Works with curl, browsers, any HTTP client
- Comprehensive error messages and logging

## Performance Optimizations

### 1. Streamlined Coordination
- Direct execution for obvious moves (winning/blocking)
- Only invokes full pipeline when necessary
- Sub-second response times for simple positions

### 2. Metrics Tracking
- Microsecond-precision response time tracking
- Token usage monitoring per request
- Success rate and error tracking
- Memory usage monitoring

### 3. Async Architecture
- All MCP handlers are async
- Non-blocking agent communication
- Concurrent request handling

## Testing the Architecture

### Quick Test with curl

```bash
# 1. Discover Scout agent capabilities
curl http://localhost:8000/mcp/scout

# 2. Get Scout agent status
curl -X POST http://localhost:8000/mcp/scout \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_status","arguments":{}}}'

# 3. Read Scout metrics
curl -X POST http://localhost:8000/mcp/scout \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/read","params":{"uri":"agent://scout/metrics"}}'

# 4. Analyze a board position
curl -X POST http://localhost:8000/mcp/scout \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"analyze_board","arguments":{"board":[["X","O","X"],["","O",""],["","",""]]}}}'
```

### Test with Python

```python
import requests

# Discover all capabilities
response = requests.get("http://localhost:8000/mcp/scout")
capabilities = response.json()

print(f"Tools: {len(capabilities['result']['tools'])}")
print(f"Resources: {len(capabilities['result']['resources'])}")
print(f"Prompts: {len(capabilities['result']['prompts'])}")
```

### Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
# Configure:
# - Transport: HTTP
# - URL: http://localhost:8000/mcp/scout
# - Connection: Direct
```

## Future Enhancements

### Planned Features
- [ ] Distributed deployment across multiple machines
- [ ] Load balancing for agent requests
- [ ] Persistent game history and replay
- [ ] Tournament mode with multiple AI opponents
- [ ] WebSocket support for real-time updates
- [ ] Agent-to-agent direct communication (peer-to-peer)

### Potential Improvements
- [ ] Caching layer for repeated board positions
- [ ] Batch processing for multiple games
- [ ] Enhanced error recovery and retry logic
- [ ] Advanced metrics aggregation and analysis
- [ ] Model performance comparison dashboard

## References

- **MCP Protocol**: https://modelcontextprotocol.io/
- **CrewAI**: https://github.com/joaomdmoura/crewAI
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://streamlit.io/

---

**Last Updated**: October 2025
**Architecture Version**: 2.0.0
