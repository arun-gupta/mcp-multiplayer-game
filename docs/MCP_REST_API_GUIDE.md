# 🌐 MCP Server REST HTTP API Guide

> **✅ RECOMMENDED APPROACH** - This is the most reliable way to interact with MCP agents. No GUI dependencies or connection issues.

## 🎯 **Direct HTTP Access to MCP Servers**

You can query MCP servers directly using REST HTTP requests without needing the MCP Inspector GUI!

## 📡 **Available Endpoints**

| Agent | Endpoint | Purpose |
|-------|----------|---------|
| **Scout** | `http://localhost:8000/mcp/scout` | Board analysis, threat detection |
| **Strategist** | `http://localhost:8000/mcp/strategist` | Strategy creation, move planning |
| **Executor** | `http://localhost:8000/mcp/executor` | Move execution, validation |

## 🔧 **HTTP Methods**

### **GET - Agent Information**
```bash
curl http://localhost:8000/mcp/scout
```
Returns: Agent info and available tools

### **POST - MCP Method Calls**
```bash
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"METHOD","params":{}}'
```

## 🛠️ **Available MCP Methods**

### **1. Tools**
```bash
# List all tools
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Call a tool
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_status","arguments":{}}}'
```

### **2. Resources**
```bash
# List resources
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/list","params":{}}'

# Read a resource
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/read","params":{"uri":"agent://scout/metrics"}}'
```

### **3. Prompts**
```bash
# List prompts
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"prompts/list","params":{}}'

# Get a prompt
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"prompts/get","params":{"name":"execute_task_prompt","arguments":{"task_description":"Analyze board"}}}'
```

## 🎮 **Game-Specific Tool Examples**

### **Scout Agent - Board Analysis**
```bash
# Analyze Tic-Tac-Toe board
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"analyze_board","arguments":{"board":["X","O","X","-","O","X","-","O","X"]}}}'

# Detect threats
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"detect_threats","arguments":{"board":["X","O","X","-","O","X","-","O","X"]}}}'

# Identify opportunities
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"identify_opportunities","arguments":{"board":["X","O","X","-","O","X","-","O","X"]}}}'
```

### **Strategist Agent - Strategy Creation**
```bash
# Create strategy
curl -X POST http://localhost:8000/mcp/strategist \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"create_strategy","arguments":{"observation_data":"Board analysis results"}}}'

# Evaluate position
curl -X POST http://localhost:8000/mcp/strategist \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"evaluate_position","arguments":{"board_state":["X","O","X","-","O","X","-","O","X"],"player":"X"}}}'
```

### **Executor Agent - Move Execution**
```bash
# Execute move
curl -X POST http://localhost:8000/mcp/executor \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"execute_move","arguments":{"strategy_data":"Strategic plan"}}}'

# Validate move
curl -X POST http://localhost:8000/mcp/executor \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"validate_move","arguments":{"move":4,"board_state":["X","O","X","-","O","X","-","O","X"]}}}'
```

## 🐍 **Python Examples**

### **Simple Python Client**
```python
import requests
import json

def call_mcp_method(agent, method, params={}):
    """Call MCP method via HTTP"""
    response = requests.post(
        f"http://localhost:8000/mcp/{agent}",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
    )
    return response.json()

# Examples
tools = call_mcp_method("scout", "tools/list")
status = call_mcp_method("scout", "tools/call", {
    "name": "get_status",
    "arguments": {}
})
resources = call_mcp_method("scout", "resources/list")
```

### **Interactive Python Tool**
```python
import requests
import json

class MCPClient:
    def __init__(self, agent):
        self.agent = agent
        self.base_url = f"http://localhost:8000/mcp/{agent}"
    
    def call(self, method, params={}):
        response = requests.post(
            self.base_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
        )
        return response.json()
    
    def list_tools(self):
        return self.call("tools/list")
    
    def call_tool(self, name, arguments={}):
        return self.call("tools/call", {"name": name, "arguments": arguments})
    
    def list_resources(self):
        return self.call("resources/list")
    
    def read_resource(self, uri):
        return self.call("resources/read", {"uri": uri})

# Usage
scout = MCPClient("scout")
tools = scout.list_tools()
status = scout.call_tool("get_status")
```

## 📊 **Response Format**

All responses follow JSON-RPC 2.0 format:

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        // Method-specific result
    }
}
```

## 🚀 **Quick Start Examples**

### **1. Get Agent Status**
```bash
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_status","arguments":{}}}'
```

### **2. Get Agent Metrics**
```bash
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"resources/read","params":{"uri":"agent://scout/metrics"}}'
```

### **3. Analyze Board**
```bash
curl -X POST http://localhost:8000/mcp/scout \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"analyze_board","arguments":{"board":["X","O","X","-","O","X","-","O","X"]}}}'
```

## ✅ **Benefits of REST HTTP**

- ✅ **No GUI required** - Direct API access
- ✅ **Easy integration** - Standard HTTP requests
- ✅ **Scriptable** - Perfect for automation
- ✅ **Language agnostic** - Works with any HTTP client
- ✅ **Real-time** - Direct access to MCP agents
- ✅ **No authentication** - Simple and direct

---

**Happy MCP REST API Exploring! 🚀**
