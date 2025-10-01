# 🔍 MCP Inspector Connection Guide

> **⚠️ WORK IN PROGRESS** - The MCP Inspector GUI has connection issues. Use the [REST API Guide](MCP_REST_API_GUIDE.md) for direct HTTP access instead.

## 🎯 **Correct Settings for MCP Inspector**

When the MCP Inspector opens in your browser, use these **exact settings**:

### **📋 Required Settings:**
1. **Transport Type**: `Streamable HTTP` ✅
2. **URL**: `http://localhost:8000/mcp/scout` ✅
3. **Connection Type**: `Direct` ✅ (NOT "Via Proxy")
4. **Authentication**: Leave empty (disabled)
5. **Configuration**: Leave as default

### **❌ Common Mistakes:**
- ❌ **Don't use "Via Proxy"** - This requires proxy tokens
- ❌ **Don't use SSE transport** - It's deprecated
- ❌ **Don't add authentication tokens** - We disabled auth

## 🚀 **Launch Methods:**

### **Method 1: Automatic Launcher**
```bash
./scripts/mcp/launch_inspector.sh scout
```
- Automatically handles port cleanup
- Opens browser with correct settings
- Shows helpful instructions

### **Method 2: Direct Connection**
```bash
./scripts/mcp/launch_direct_mcp.sh
```
- Launches with direct connection
- Shows step-by-step instructions
- No proxy configuration needed

### **Method 3: Manual Launch**
```bash
DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector --transport http --server-url "http://localhost:8000/mcp/scout"
```

## 🎮 **Available Agents:**

| Agent | URL | Purpose |
|-------|-----|---------|
| **Scout** | `http://localhost:8000/mcp/scout` | Board analysis, threat detection |
| **Strategist** | `http://localhost:8000/mcp/strategist` | Strategy creation, move planning |
| **Executor** | `http://localhost:8000/mcp/executor` | Move execution, validation |

## 🔧 **Troubleshooting:**

### **Connection Error: "Did you add the proxy session token?"**
**Solution**: Change Connection Type from "Via Proxy" to "Direct"

### **Connection Error: "Check if your MCP server is running"**
**Solution**: 
1. Ensure backend is running: `curl http://localhost:8000/health`
2. Start backend: `python main.py`

### **Port Conflicts**
**Solution**: Run `./scripts/cleanup_ports.sh` or restart with `./scripts/mcp/launch_inspector.sh scout`

## 📊 **What You Can Do in MCP Inspector:**

### **🔧 Tools (8 per agent):**
- `execute_task` - Execute CrewAI tasks
- `get_status` - Get agent status
- `get_memory` - Get agent memory
- `get_metrics` - Get performance metrics
- `analyze_board` - Analyze Tic-Tac-Toe board
- `detect_threats` - Identify threats
- `identify_opportunities` - Find opportunities
- `get_pattern_analysis` - Analyze patterns

### **📦 Resources (3 per agent):**
- `agent://scout/status` - Agent status and config
- `agent://scout/metrics` - Performance metrics
- `agent://scout/memory` - Agent memory

### **💬 Prompts (1 per agent):**
- `execute_task_prompt` - Task execution template

## 🎯 **Quick Start:**

1. **Start Backend**: `python main.py`
2. **Launch Inspector**: `./scripts/mcp/launch_inspector.sh scout`
3. **Configure GUI**: Use settings above
4. **Click Connect**: Should work without errors
5. **Explore**: Browse tools, resources, and prompts

## ✅ **Success Indicators:**

- ✅ No "Connection Error" messages
- ✅ Tools list loads in the GUI
- ✅ Can call tools and see responses
- ✅ Resources and prompts accessible
- ✅ Real-time interaction with MCP agents

---

**Happy MCP Exploring! 🚀**
