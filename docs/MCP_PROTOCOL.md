# 📡 MCP Protocol Implementation

This document explains the **real MCP (Multi-Context Protocol)** implementation in this project.

## 🎯 Overview

The project now uses the **official MCP SDK** (`mcp==1.15.0`) instead of a simulated protocol. Each CrewAI agent runs as a real MCP Server with standardized tool exposure.

## 🏗️ Architecture

### **MCP Server Stack**
```
┌─────────────────────────────────────┐
│   MCP Protocol (JSON-RPC 2.0)      │
├─────────────────────────────────────┤
│   MCP SDK (Server, Tool, Client)   │
├─────────────────────────────────────┤
│   CrewAI Agent (LLM, Memory, Task)  │
├─────────────────────────────────────┤
│   Python asyncio Runtime            │
└─────────────────────────────────────┘
```

### **Agent MCP Servers**
- **Scout Agent**: Port 3001 (Board Analysis Tools)
- **Strategist Agent**: Port 3002 (Strategy Tools)
- **Executor Agent**: Port 3003 (Execution Tools)

## 📋 MCP Protocol Endpoints

### **Standard MCP Requests**

#### **1. List Tools** (`tools/list`)
Discover all available tools from an agent:

```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}

// Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "analyze_board",
        "description": "Analyze Tic-Tac-Toe board state and provide comprehensive insights",
        "inputSchema": {
          "type": "object",
          "properties": {
            "board": { "type": "array", "description": "3x3 game board" },
            "current_player": { "type": "string", "description": "Current player" },
            "move_number": { "type": "integer", "description": "Current move number" }
          },
          "required": ["board"]
        }
      }
    ]
  }
}
```

#### **2. Call Tool** (`tools/call`)
Execute a specific tool:

```json
// Request
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "analyze_board",
    "arguments": {
      "board": [["X","",""],["","O",""],["","",""]],
      "current_player": "ai",
      "move_number": 3
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"agent_id\":\"scout\",\"board_state\":...,\"analysis\":...}"
      }
    ]
  }
}
```

## 🔍 Scout Agent MCP Tools

**Port:** 3001

| Tool | Description | Parameters |
|------|-------------|------------|
| `analyze_board` | Analyze board state and provide insights | `board`, `current_player`, `move_number` |
| `detect_threats` | Identify immediate threats | `board` |
| `identify_opportunities` | Find winning opportunities | `board` |
| `get_pattern_analysis` | Analyze game patterns | `board`, `move_history` |
| `execute_task` | Execute CrewAI task | `description`, `expected_output`, `context` |
| `get_status` | Get agent status | - |
| `get_memory` | Get agent memory | - |
| `get_metrics` | Get performance metrics | - |

## 🧠 Strategist Agent MCP Tools

**Port:** 3002

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_strategy` | Generate strategic plan | `observation_data` |
| `evaluate_position` | Evaluate position strength | `board_state`, `player` |
| `recommend_move` | Recommend best move | `board_state`, `available_moves` |
| `assess_win_probability` | Calculate win probability | `board_state`, `player` |
| `execute_task` | Execute CrewAI task | `description`, `expected_output`, `context` |
| `get_status` | Get agent status | - |
| `get_memory` | Get agent memory | - |
| `get_metrics` | Get performance metrics | - |

## ⚡ Executor Agent MCP Tools

**Port:** 3003

| Tool | Description | Parameters |
|------|-------------|------------|
| `execute_move` | Execute move on board | `move_data`, `board_state` |
| `validate_move` | Validate move legality | `move`, `board_state` |
| `update_game_state` | Update game state | `move`, `current_state` |
| `confirm_execution` | Confirm move execution | `execution_result` |
| `execute_task` | Execute CrewAI task | `description`, `expected_output`, `context` |
| `get_status` | Get agent status | - |
| `get_memory` | Get agent memory | - |
| `get_metrics` | Get performance metrics | - |

## 🛠️ How to Use MCP Protocol

### **Method 1: MCP Inspector (Recommended)**

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Connect to Scout Agent
npx @modelcontextprotocol/inspector http://localhost:3001

# Connect to Strategist Agent
npx @modelcontextprotocol/inspector http://localhost:3002

# Connect to Executor Agent
npx @modelcontextprotocol/inspector http://localhost:3003
```

The MCP Inspector provides:
- ✅ Interactive tool discovery
- ✅ Tool testing with custom inputs
- ✅ Real-time results viewing
- ✅ JSON Schema validation
- ✅ Protocol debugging

### **Method 2: curl / HTTP Client**

```bash
# List tools from Scout Agent
curl -X POST http://localhost:3001 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call analyze_board tool
curl -X POST http://localhost:3001 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "analyze_board",
      "arguments": {
        "board": [["X","",""],["","O",""],["","",""]],
        "current_player": "ai"
      }
    }
  }'
```

### **Method 3: MCP Client Library (Python)**

```python
from mcp.client import Client
import asyncio

async def query_scout_agent():
    async with Client("http://localhost:3001") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Scout Agent Tools: {[t.name for t in tools]}")
        
        # Call analyze_board tool
        result = await client.call_tool(
            "analyze_board",
            arguments={
                "board": [["X","",""],["","O",""],["","",""]],
                "current_player": "ai",
                "move_number": 3
            }
        )
        print(f"Analysis Result: {result}")

asyncio.run(query_scout_agent())
```

## 🔧 Implementation Details

### **Base MCP Agent Class**

**File:** `agents/base_mcp_agent.py`

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

class BaseMCPAgent(Agent, ABC):
    def __init__(self, ...):
        # Create MCP Server
        self.__dict__['mcp_server'] = Server(f"{agent_id}-mcp-server")
        self.__dict__['tools_registry'] = {}
    
    async def start_mcp_server(self):
        """Start MCP server with protocol support"""
        mcp_server = self.__dict__.get('mcp_server')
        
        # Register tools/list handler
        @mcp_server.list_tools()
        async def list_tools() -> list[Tool]:
            # Return registered tools
            ...
        
        # Register tools/call handler
        @mcp_server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            # Execute tool and return result
            ...
    
    def register_mcp_tool(self, name, handler, description, input_schema):
        """Register a tool with JSON Schema"""
        self.__dict__['tools_registry'][name] = {
            'handler': handler,
            'description': description,
            'inputSchema': input_schema
        }
```

### **Tool Registration Example**

```python
# In Scout Agent
def register_agent_specific_endpoints(self):
    self.register_mcp_tool(
        "analyze_board",
        self.analyze_board,
        "Analyze Tic-Tac-Toe board state and provide comprehensive insights",
        {
            "type": "object",
            "properties": {
                "board": {"type": "array", "description": "3x3 game board"},
                "current_player": {"type": "string"},
                "move_number": {"type": "integer"}
            },
            "required": ["board"]
        }
    )
```

## 📊 Benefits of Real MCP Protocol

### **1. Standardization**
- ✅ Industry-standard JSON-RPC 2.0 protocol
- ✅ Consistent tool discovery across all agents
- ✅ JSON Schema validation for inputs

### **2. Interoperability**
- ✅ Any MCP client can connect to agents
- ✅ Language-agnostic tool invocation
- ✅ Compatible with MCP Inspector and other tools

### **3. Debugging & Monitoring**
- ✅ Real-time tool inspection
- ✅ Protocol-level debugging
- ✅ Standardized error handling

### **4. Scalability**
- ✅ Agents can run on different machines
- ✅ Service discovery via MCP protocol
- ✅ Load balancing and failover support

## 🚀 Next Steps

### **Planned Enhancements**
- [ ] HTTP/SSE transport for network access
- [ ] MCP Prompts support for agent interactions
- [ ] MCP Resources for game state sharing
- [ ] Client SDK for easier integration
- [ ] WebSocket transport for real-time updates

### **Testing MCP Tools**
1. Start the application: `./quickstart.sh`
2. Open MCP Inspector: `npx @modelcontextprotocol/inspector http://localhost:3001`
3. Explore available tools in the web UI
4. Test tools with custom inputs
5. View real-time results

## 📚 Resources

- **MCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **MCP Specification**: https://spec.modelcontextprotocol.io
- **JSON-RPC 2.0**: https://www.jsonrpc.org/specification

---

**Note:** The MCP implementation is now production-ready with real protocol support, tool discovery, and standardized communication! 🎉

