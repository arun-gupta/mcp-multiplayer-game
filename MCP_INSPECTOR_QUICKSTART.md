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
- **Transport**: Select "HTTP"
- **Server URL**: Enter one of:
  - Scout: `http://localhost:8000/mcp/scout`
  - Strategist: `http://localhost:8000/mcp/strategist`
  - Executor: `http://localhost:8000/mcp/executor`
- Click **"Connect"**

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

## 🔗 MCP Server URLs

| Agent | MCP Inspector URL | Tools |
|-------|-------------------|-------|
| **Scout** | http://localhost:8000/mcp/scout | Board analysis, threat detection |
| **Strategist** | http://localhost:8000/mcp/strategist | Strategy creation, move recommendation |
| **Executor** | http://localhost:8000/mcp/executor | Move execution, validation |

## 📚 Full Documentation

See [docs/MCP_INSPECTOR.md](docs/MCP_INSPECTOR.md) for complete guide.

---

**🎉 You now have full MCP protocol inspection capability!**

