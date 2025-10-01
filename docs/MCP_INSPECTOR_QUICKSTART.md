# 🔍 MCP Inspector Quick Start

## 🚀 3-Step Setup

### **Step 1: Start the Application**
```bash
./quickstart.sh
```

### **Step 2: Install & Launch MCP Inspector**
```bash
npx @modelcontextprotocol/inspector
```

### **Step 3: Connect to an Agent**

In the MCP Inspector web UI:
- **Method**: Use HTTP/JSON-RPC (custom transport)
- **Base URL**: `http://localhost:8000`
- **Agent Endpoint**: `/mcp/{agent_id}`
  - Scout: `/mcp/scout`
  - Strategist: `/mcp/strategist`
  - Executor: `/mcp/executor`

**Or use curl to test:**
```bash
# List Scout tools
curl http://localhost:8000/mcp/scout

# Call a tool
curl -X POST http://localhost:8000/mcp/scout \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_status","arguments":{}}}'
```

## 🎯 Quick Test

1. Click **"Tools"** tab
2. Click **"List Tools"** - You should see 8 tools
3. Select **"get_status"** tool
4. Click **"Execute"** - See agent status
5. Try **"analyze_board"** with:
   ```json
   {
     "board": [["X","",""],["","O",""],["","",""]],
     "current_player": "ai"
   }
   ```

## 📊 What You Can Do

- ✅ **Discover Tools** - See all 8 tools per agent
- ✅ **View Schemas** - JSON Schema for each tool
- ✅ **Test Tools** - Execute tools with custom inputs
- ✅ **Debug Protocol** - See full MCP communication
- ✅ **Monitor Performance** - Real-time metrics

## 🔗 MCP Tool Endpoints

| Agent | MCP Endpoint | Tools |
|-------|--------------|-------|
| **Scout** | http://localhost:8000/mcp/scout | Board analysis, threat detection, 8 tools total |
| **Strategist** | http://localhost:8000/mcp/strategist | Strategy creation, move recommendation, 8 tools total |
| **Executor** | http://localhost:8000/mcp/executor | Move execution, validation, 8 tools total |

**Protocol**: JSON-RPC 2.0 (MCP-compliant)  
**Methods**: `tools/list`, `tools/call`, `initialize`  
**Format**: Standard MCP tool discovery and execution

## 📚 Full Documentation

See [docs/MCP_INSPECTOR.md](docs/MCP_INSPECTOR.md) for complete guide.

---

**🎉 You now have full MCP protocol inspection capability!**

