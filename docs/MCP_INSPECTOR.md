# 🔍 MCP Inspector Integration Guide

This guide shows you how to use **MCP Inspector** to query and test the MCP servers running in this application.

## 🎯 Overview

The MCP Inspector is an interactive developer tool for testing and debugging MCP servers. Each of our three CrewAI agents (Scout, Strategist, Executor) runs as an MCP Server that can be inspected.

## 🚀 Quick Start

### **1. Ensure the Application is Running**

```bash
./quickstart.sh
```

This starts:
- **Scout MCP Server**: http://localhost:3001/mcp
- **Strategist MCP Server**: http://localhost:3002/mcp
- **Executor MCP Server**: http://localhost:3003/mcp
- **FastAPI Backend**: http://localhost:8000
- **Streamlit UI**: http://localhost:8501

### **2. Install MCP Inspector**

```bash
npm install -g @modelcontextprotocol/inspector
```

Or use without installing:
```bash
npx @modelcontextprotocol/inspector
```

### **3. Launch MCP Inspector**

```bash
npx @modelcontextprotocol/inspector
```

This opens a web interface in your browser (usually http://localhost:5173).

## 🔌 Connecting to MCP Servers

### **Option 1: Connect to Scout Agent**

1. In MCP Inspector, select **"SSE"** as the transport type
2. Enter Server URL: `http://localhost:3001/mcp`
3. Click **"Connect"**

### **Option 2: Connect to Strategist Agent**

1. In MCP Inspector, select **"SSE"** as the transport type
2. Enter Server URL: `http://localhost:3002/mcp`
3. Click **"Connect"**

### **Option 3: Connect to Executor Agent**

1. In MCP Inspector, select **"SSE"** as the transport type
2. Enter Server URL: `http://localhost:3003/mcp`
3. Click **"Connect"**

## 🛠️ Using MCP Inspector

### **1. List Tools**

Once connected, navigate to the **"Tools"** tab and click **"List Tools"**. You'll see all available tools with:

#### **Scout Agent Tools:**
- ✅ `analyze_board` - Analyze board state and provide insights
- ✅ `detect_threats` - Identify immediate threats
- ✅ `identify_opportunities` - Find winning opportunities
- ✅ `get_pattern_analysis` - Analyze game patterns
- ✅ `execute_task` - Execute CrewAI task
- ✅ `get_status` - Get agent status
- ✅ `get_memory` - Get agent memory
- ✅ `get_metrics` - Get performance metrics

#### **Strategist Agent Tools:**
- ✅ `create_strategy` - Generate strategic plan
- ✅ `evaluate_position` - Evaluate position strength
- ✅ `recommend_move` - Recommend best move
- ✅ `assess_win_probability` - Calculate win probability
- ✅ `execute_task` - Execute CrewAI task
- ✅ `get_status` - Get agent status
- ✅ `get_memory` - Get agent memory
- ✅ `get_metrics` - Get performance metrics

#### **Executor Agent Tools:**
- ✅ `execute_move` - Execute move on board
- ✅ `validate_move` - Validate move legality
- ✅ `update_game_state` - Update game state
- ✅ `confirm_execution` - Confirm move execution
- ✅ `execute_task` - Execute CrewAI task
- ✅ `get_status` - Get agent status
- ✅ `get_memory` - Get agent memory
- ✅ `get_metrics` - Get performance metrics

### **2. Test a Tool**

1. Click on any tool (e.g., `analyze_board`)
2. View the **Input Schema** (JSON Schema validation)
3. Enter test input:
   ```json
   {
     "board": [["X","",""],["","O",""],["","",""]],
     "current_player": "ai",
     "move_number": 3
   }
   ```
4. Click **"Execute"**
5. View the **Results** in real-time

### **3. View Tool Schemas**

Each tool shows its JSON Schema:

```json
{
  "name": "analyze_board",
  "description": "Analyze Tic-Tac-Toe board state and provide comprehensive insights",
  "inputSchema": {
    "type": "object",
    "properties": {
      "board": {
        "type": "array",
        "description": "3x3 game board"
      },
      "current_player": {
        "type": "string",
        "description": "Current player (player or ai)"
      },
      "move_number": {
        "type": "integer",
        "description": "Current move number"
      }
    },
    "required": ["board"]
  }
}
```

### **4. Debug MCP Communication**

The Inspector shows:
- ✅ **Protocol Messages** - Full JSON-RPC 2.0 communication
- ✅ **Tool Execution Logs** - Real-time execution traces
- ✅ **Error Messages** - Detailed error information
- ✅ **Response Timing** - Performance metrics

## 📊 Example Workflows

### **Workflow 1: Analyze a Game Position**

1. **Connect** to Scout Agent (`http://localhost:3001/mcp`)
2. **List Tools** to see available tools
3. **Select** `analyze_board` tool
4. **Input** current board state:
   ```json
   {
     "board": [["X","O","X"],["","O",""],["","",""]],
     "current_player": "ai"
   }
   ```
5. **Execute** and view the analysis
6. See **threats**, **opportunities**, and **available moves**

### **Workflow 2: Test Strategy Creation**

1. **Connect** to Strategist Agent (`http://localhost:3002/mcp`)
2. **Select** `create_strategy` tool
3. **Input** board analysis from Scout:
   ```json
   {
     "observation_data": {
       "board": [["X","O","X"],["","O",""],["","",""]],
       "threats": ["Opponent can win diagonally"],
       "opportunities": ["Can block center"]
     }
   }
   ```
4. **Execute** and view the strategic plan
5. See **recommended_move** and **reasoning**

### **Workflow 3: Check Agent Metrics**

1. **Connect** to any agent
2. **Select** `get_metrics` tool
3. **Execute** (no input needed)
4. View **real-time performance data**:
   - Request count
   - Response times
   - Token usage
   - Success rate

## 🧪 Advanced Testing

### **Multi-Agent Workflow Test**

1. **Open 3 Inspector windows** (one for each agent)
2. **Scout Window**: Execute `analyze_board`
3. **Copy Scout's output**
4. **Strategist Window**: Execute `create_strategy` with Scout's output
5. **Copy Strategist's output**
6. **Executor Window**: Execute `execute_move` with Strategist's move
7. **Observe** the complete multi-agent coordination flow!

### **Load Testing**

1. **Connect** to an agent
2. **Execute** the same tool multiple times
3. **Watch** `get_metrics` to see:
   - Increasing request count
   - Average response time
   - Token accumulation
   - Min/Max response times

## 🔧 Troubleshooting

### **Inspector Can't Connect**

**Problem:** Connection timeout or error

**Solutions:**
```bash
# 1. Check if MCP servers are running
lsof -i :3001
lsof -i :3002
lsof -i :3003

# 2. Check application logs
tail -f backend.log

# 3. Test HTTP endpoint directly
curl http://localhost:3001/health

# 4. Restart application
./quickstart.sh
```

### **Tools Not Appearing**

**Problem:** No tools shown in Inspector

**Solutions:**
1. Ensure you're connected to the correct URL (`/mcp` endpoint)
2. Check that the agent initialized successfully (check logs)
3. Verify tools were registered (look for "Registered tool" in logs)

### **Tool Execution Fails**

**Problem:** Tool returns error

**Solutions:**
1. Check the **Input Schema** - ensure your input matches
2. Review **Required Fields** - some tools need specific parameters
3. Check **Application Logs** - see detailed error messages
4. Test with minimal valid input first

## 📋 Available Inspector Features

### **Tools Tab**
- ✅ List all tools
- ✅ View tool descriptions
- ✅ See input/output schemas
- ✅ Execute tools with custom inputs
- ✅ View real-time results

### **Resources Tab** (Future)
- 🔄 Browse game state resources
- 🔄 View resource metadata
- 🔄 Subscribe to resource updates

### **Prompts Tab** (Future)
- 🔄 Explore prompt templates
- 🔄 Test prompt generation
- 🔄 Preview message outputs

### **Notifications Pane**
- ✅ Server logs and events
- ✅ Protocol-level debugging
- ✅ Error messages
- ✅ Performance metrics

## 🎯 Best Practices

### **1. Test Tools Individually**
- Start with simple tools like `get_status`
- Verify each tool works before chaining
- Use valid JSON Schema inputs

### **2. Use Health Check First**
```bash
# Test if server is accessible
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health
```

### **3. Monitor Logs**
```bash
# Watch application logs while testing
tail -f backend.log
```

### **4. Test Complete Workflows**
- Use Inspector to simulate full agent coordination
- Copy outputs between agents
- Verify end-to-end functionality

## 📚 Resources

- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **MCP Documentation**: https://modelcontextprotocol.io/docs/tools/inspector
- **Our MCP Protocol Guide**: [MCP_PROTOCOL.md](MCP_PROTOCOL.md)
- **API Documentation**: [API.md](API.md)

## 🎉 Quick Test

Try this to verify everything works:

```bash
# 1. Start application
./quickstart.sh

# 2. In another terminal, test Scout agent
curl http://localhost:3001/health

# 3. Open MCP Inspector
npx @modelcontextprotocol/inspector

# 4. Connect to Scout
# URL: http://localhost:3001/mcp
# Transport: SSE

# 5. List Tools and test analyze_board
```

You should see all 8 tools for the Scout agent and be able to execute them interactively! 🚀

