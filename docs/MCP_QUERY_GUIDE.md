# 🔍 MCP Server Query Guide

This guide shows you how to query MCP servers using different methods.

## 🎯 **Available MCP Servers**

| Agent | URL | Port | Purpose |
|-------|-----|------|---------|
| Scout | `http://localhost:8000/mcp/scout` | 3001 | Board analysis, threat detection |
| Strategist | `http://localhost:8000/mcp/strategist` | 3002 | Strategy creation, move planning |
| Executor | `http://localhost:8000/mcp/executor` | 3003 | Move execution, validation |

## 🛠️ **Method 1: MCP Inspector (Recommended)**

The easiest way to explore MCP servers with a GUI:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Connect to Scout Agent
npx @modelcontextprotocol/inspector --transport sse --server-url http://localhost:8000/mcp/scout

# Connect to Strategist Agent  
npx @modelcontextprotocol/inspector --transport sse --server-url http://localhost:8000/mcp/strategist

# Connect to Executor Agent
npx @modelcontextprotocol/inspector --transport sse --server-url http://localhost:8000/mcp/executor

# CLI Mode (for scripting)
npx @modelcontextprotocol/inspector --transport sse --server-url http://localhost:8000/mcp/scout --cli
```

## 📡 **Method 2: Direct HTTP/JSON-RPC Calls**

### **List All Tools**
```bash
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### **Call a Tool**
```bash
# Get agent status
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_status","arguments":{}}}'

# Analyze board (Scout)
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"analyze_board","arguments":{"board":"XOX-OX-OX"}}}'

# Create strategy (Strategist)
curl -X POST http://localhost:8000/mcp/strategist \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"create_strategy","arguments":{"observation_data":"Board analysis results"}}}'

# Execute move (Executor)
curl -X POST http://localhost:8000/mcp/executor \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"execute_move","arguments":{"strategy_data":"Strategic plan"}}}'
```

### **List Resources**
```bash
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/list","params":{}}'
```

### **Read a Resource**
```bash
# Get agent metrics
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/read","params":{"uri":"agent://scout/metrics"}}'

# Get agent status
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/read","params":{"uri":"agent://scout/status"}}'

# Get agent memory
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/read","params":{"uri":"agent://scout/memory"}}'
```

### **List Prompts**
```bash
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"prompts/list","params":{}}'
```

### **Get a Prompt**
```bash
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"prompts/get","params":{"name":"execute_task_prompt","arguments":{"task_description":"Analyze the board"}}}'
```

## 🐍 **Method 3: Python Script**

Use our existing test script:

```bash
# Run comprehensive MCP discovery
python test_mcp_tools.py
```

Or create your own script:

```python
import requests
import json

def query_mcp_server(agent_id, method, params={}):
    """Query MCP server with JSON-RPC"""
    response = requests.post(
        f"http://localhost:8000/mcp/{agent_id}",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
    )
    return response.json()

# Examples
tools = query_mcp_server("scout", "tools/list")
resources = query_mcp_server("scout", "resources/list")
prompts = query_mcp_server("scout", "prompts/list")

# Call a tool
result = query_mcp_server("scout", "tools/call", {
    "name": "get_status",
    "arguments": {}
})
```

## 📊 **Available MCP Methods**

| Method | Purpose | Example |
|--------|---------|---------|
| `tools/list` | List all available tools | `{"method":"tools/list","params":{}}` |
| `tools/call` | Execute a tool | `{"method":"tools/call","params":{"name":"get_status","arguments":{}}}` |
| `resources/list` | List all resources | `{"method":"resources/list","params":{}}` |
| `resources/read` | Read a resource | `{"method":"resources/read","params":{"uri":"agent://scout/metrics"}}` |
| `prompts/list` | List all prompts | `{"method":"prompts/list","params":{}}` |
| `prompts/get` | Get a prompt template | `{"method":"prompts/get","params":{"name":"execute_task_prompt","arguments":{"task_description":"..."}}}` |

## 🎮 **Game-Specific Tool Examples**

### **Scout Agent Tools**
```bash
# Analyze board state
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"analyze_board","arguments":{"board":"XOX-OX-OX"}}}'

# Detect threats
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"detect_threats","arguments":{"board":"XOX-OX-OX"}}}'

# Identify opportunities
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"identify_opportunities","arguments":{"board":"XOX-OX-OX"}}}'
```

### **Strategist Agent Tools**
```bash
# Create strategy
curl -X POST http://localhost:8000/mcp/strategist \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"create_strategy","arguments":{"observation_data":"Board analysis"}}}'

# Evaluate position
curl -X POST http://localhost:8000/mcp/strategist \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"evaluate_position","arguments":{"board_state":"XOX-OX-OX","player":"X"}}}'

# Recommend move
curl -X POST http://localhost:8000/mcp/strategist \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"recommend_move","arguments":{"board_state":"XOX-OX-OX","available_moves":[0,1,2,3,4,5,6,7,8]}}}'
```

### **Executor Agent Tools**
```bash
# Execute move
curl -X POST http://localhost:8000/mcp/executor \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"execute_move","arguments":{"strategy_data":"Strategic plan"}}}'

# Validate move
curl -X POST http://localhost:8000/mcp/executor \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"validate_move","arguments":{"move":4,"board_state":"XOX-OX-OX"}}}'

# Update game state
curl -X POST http://localhost:8000/mcp/executor \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"update_game_state","arguments":{"move":4,"current_state":"XOX-OX-OX"}}}'
```

## 🔧 **Troubleshooting**

### **Server Not Running**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend
cd /path/to/project
source venv/bin/activate
python main.py
```

### **Connection Refused**
```bash
# Check if port is in use
lsof -i :8000

# Kill existing processes
pkill -f "python main.py"
```

### **JSON-RPC Errors**
- Ensure `Content-Type: application/json` header
- Use proper JSON-RPC 2.0 format
- Include `id` field for request tracking

## 📚 **Additional Resources**

- [MCP Protocol Specification](https://modelcontextprotocol.io/docs)
- [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

---

**Happy Querying! 🚀**
