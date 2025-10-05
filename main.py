"""
Main FastAPI Application with MCP Protocol
Multi-Agent Game Simulation using CrewAI + MCP
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette import EventSourceResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
import uvicorn
import os
import json
from datetime import datetime
import asyncio
import time
import psutil
import random

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[INFO] Environment variables loaded from .env file")
except ImportError:
    # python-dotenv not installed, that's okay
    print("[INFO] python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"[WARNING] Failed to load .env file: {e}")

# Check for API keys and provide helpful messages
import os
missing_keys = []
if not os.getenv("OPENAI_API_KEY"):
    missing_keys.append("OPENAI_API_KEY")
if not os.getenv("ANTHROPIC_API_KEY"):
    missing_keys.append("ANTHROPIC_API_KEY")

if missing_keys:
    print(f"[WARNING] Missing API keys: {', '.join(missing_keys)}")
    print("[INFO] Cloud models (OpenAI/Anthropic) will not be available")
    print("[INFO] To enable cloud models, create .env file with your API keys:")
    print("[INFO]   cp .env.example .env")
    print("[INFO]   # Edit .env and add your API keys")
else:
    print("[INFO] API keys found - cloud models will be available")

# Import MCP modules
from game.mcp_coordinator import MCPGameCoordinator
from agents.scout_local import ScoutMCPAgent
from agents.strategist_local import StrategistMCPAgent
from agents.executor_local import ExecutorMCPAgent
from agents.scout_langchain import ScoutLangChain
from agents.strategist_langchain import StrategistLangChain
from agents.executor_langchain import ExecutorLangChain
from models.registry import model_registry
from models.factory import ModelFactory
from models.shared_llm import SharedLLMConnection

# Initialize FastAPI app
app = FastAPI(
    title="MCP Protocol Tic Tac Toe",
    description="Multi-Agent Game Simulation using CrewAI + MCP Protocol",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global coordinator and agents
# Will be initialized in startup_event based on mode
coordinator = None
scout_agent = None
strategist_agent = None
executor_agent = None
distributed_mode = False

# Metrics are now handled by individual MCP agents via their tools

# Pydantic models for API requests/responses
class MoveRequest(BaseModel):
    """Request model for making a move"""
    row: int
    col: int

class ModelSwitchRequest(BaseModel):
    """Request model for switching agent model"""
    model: str

class AgentStatusResponse(BaseModel):
    """Response model for agent status"""
    agents: Dict[str, Any]
    coordinator: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Start agents and coordinator based on framework mode"""
    global scout_agent, strategist_agent, executor_agent, coordinator, distributed_mode
    
    print("🚀 Startup event triggered - initializing agents...")

    # Load configuration
    from utils.config import config
    agent_framework = config.get("agent_framework", "mode", default="langchain")
    
    print(f"🚀 Starting {agent_framework.upper()} system...")

    # Check for distributed mode
    import sys
    if "--distributed" in sys.argv:
        distributed_mode = True
        print("🌐 DISTRIBUTED MODE: Agents will run as separate processes")
    else:
        print("🏠 LOCAL MODE: Agents will run in the same process")

    # Initialize coordinator with appropriate mode
    coordinator = MCPGameCoordinator(distributed=distributed_mode)
    print(f"✅ Coordinator initialized (distributed={distributed_mode})")

    # In distributed mode, skip local agent creation
    if distributed_mode:
        print("⏩ Skipping local agent creation in distributed mode")
        print("📡 Agents should be started separately:")
        print("   python agents/scout_server.py")
        print("   python agents/strategist_server.py")
        print("   python agents/executor_server.py")
        return

    # LOCAL MODE: Create agents
    print("🏠 Creating local agents...")

    # Determine best available model
    available_models = ModelFactory.get_default_models()
    print(f"🔍 Available models: {available_models}")
    
    # Try to get the best available model
    default_model = "gpt-5-mini"  # Default fallback
    
    # Check if gpt-5-mini is available, otherwise use first available
    if available_models.get("scout"):
        default_model = available_models["scout"]
        print(f"✅ Using {default_model} as default model")
    else:
        # Try to find any available model
        for model_name in ["gpt-5-mini", "gpt-4", "claude-3-sonnet", "llama3.2:3b"]:
            if ModelFactory.create_llm(model_name) is not None:
                default_model = model_name
                print(f"✅ Fallback to {default_model}")
                break
        else:
            print("⚠️ No models available - agents will be created but may not function")
    
    # Initialize agents based on framework mode
    if agent_framework == "langchain":
        print("🔗 Using LangChain agents (faster and more reliable)")
        print("📦 Creating shared LLM connection for all agents")

        # Create single shared LLM connection
        try:
            shared_llm = SharedLLMConnection(default_model)
            print(f"✅ Shared LLM connection created: {shared_llm.model_name}")
        except Exception as e:
            print(f"❌ Error creating shared LLM connection: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            shared_llm = None

        # Create agents with shared LLM connection
        try:
            scout_agent = ScoutLangChain(shared_llm=shared_llm)
            print(f"✅ Scout LangChain Agent created")
        except Exception as e:
            print(f"❌ Error creating Scout LangChain Agent: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            scout_agent = None

        try:
            strategist_agent = StrategistLangChain(shared_llm=shared_llm)
            print(f"✅ Strategist LangChain Agent created")
        except Exception as e:
            print(f"❌ Error creating Strategist LangChain Agent: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            strategist_agent = None

        try:
            executor_agent = ExecutorLangChain(shared_llm=shared_llm)
            print(f"✅ Executor LangChain Agent created")
        except Exception as e:
            print(f"❌ Error creating Executor LangChain Agent: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            executor_agent = None
            
    elif agent_framework == "crewai":
        print("🤖 Using CrewAI agents (with MCP protocol)")
        try:
            scout_agent = ScoutMCPAgent({"model": default_model})
            print(f"✅ Scout CrewAI Agent created with {default_model}")
        except Exception as e:
            print(f"❌ Error creating Scout CrewAI Agent: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            scout_agent = None
        
        try:
            strategist_agent = StrategistMCPAgent({"model": default_model})
            print(f"✅ Strategist CrewAI Agent created with {default_model}")
        except Exception as e:
            print(f"❌ Error creating Strategist CrewAI Agent: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            strategist_agent = None
        
        try:
            executor_agent = ExecutorMCPAgent({"model": default_model})
            print(f"✅ Executor CrewAI Agent created with {default_model}")
        except Exception as e:
            print(f"❌ Error creating Executor CrewAI Agent: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            executor_agent = None
    else:
        print(f"❌ Unknown agent framework: {agent_framework}")
        print("Available options: 'crewai', 'langchain'")
        return

    print(f"🔍 Agent status: scout={scout_agent is not None}, strategist={strategist_agent is not None}, executor={executor_agent is not None}")

    # Start MCP servers (only for CrewAI agents)
    if agent_framework == "crewai":
        if scout_agent:
            try:
                await scout_agent.start_mcp_server()
                print("✅ Scout MCP Server started")
            except Exception as e:
                print(f"❌ Error starting Scout MCP Server: {e}")
        if strategist_agent:
            try:
                await strategist_agent.start_mcp_server()
                print("✅ Strategist MCP Server started")
            except Exception as e:
                print(f"❌ Error starting Strategist MCP Server: {e}")
        if executor_agent:
            try:
                await executor_agent.start_mcp_server()
                print("✅ Executor MCP Server started")
            except Exception as e:
                print(f"❌ Error starting Executor MCP Server: {e}")
    else:
        # LangChain agents don't need MCP servers
        if scout_agent:
            print("✅ Scout LangChain Agent ready (no MCP server needed)")
        if strategist_agent:
            print("✅ Strategist LangChain Agent ready (no MCP server needed)")
        if executor_agent:
            print("✅ Executor LangChain Agent ready (no MCP server needed)")
    
    # Set agents in coordinator (local mode only)
    if not distributed_mode:
        coordinator.set_agents(scout_agent, strategist_agent, executor_agent)
        print("✅ Agents registered with coordinator")

    # Initialize coordinator connections
    try:
        await coordinator.initialize_agents()
        print("✅ Coordinator initialized")
    except Exception as e:
        print(f"❌ Error initializing coordinator: {e}")

    # Light pre-warming for faster startup
    if not distributed_mode and scout_agent:
        try:
            print("🔥 Light model pre-warming for faster startup...")
            
            # Quick model warmup only
            print("   📝 Basic model initialization...")
            warmup_prompt = "Hello, this is a quick warmup call."
            await asyncio.to_thread(scout_agent.llm.call, warmup_prompt)
            
            print("✅ Light pre-warming completed - game is ready!")
            
        except Exception as e:
            print(f"⚠️ Model pre-warming failed (non-critical): {e}")
            print("   💡 Game will still work but first move may be slower")

    # Show model availability summary (local mode only)
    if not distributed_mode:
        print("\n" + "="*50)
        print("MODEL AVAILABILITY SUMMARY")
        print("="*50)
        if scout_agent is not None:
            print(f"✅ All agents using: {default_model}")
        else:
            print("❌ No working models available - AI features will be limited")
            print("💡 To enable AI features:")
            print("   1. Add API keys to .env file, OR")
            print("   2. Install Ollama and pull models")
        print("="*50 + "\n")

    print("🎉 MCP CrewAI system initialized!")

@app.get("/")
async def root():
    return {"message": "MCP CrewAI Tic Tac Toe Game", "version": "2.0.0"}

@app.get("/mcp/{agent_id}")
async def mcp_info_endpoint(agent_id: str):
    """Full MCP discovery endpoint - returns tools, resources, and prompts"""
    try:
        # Get the agent
        agent = None
        if agent_id == "scout":
            agent = scout_agent
        elif agent_id == "strategist":
            agent = strategist_agent
        elif agent_id == "executor":
            agent = executor_agent
        else:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        if agent is None:
            raise HTTPException(status_code=503, detail=f"Agent '{agent_id}' not initialized")

        # Get tools registry from agent
        tools_registry = agent.__dict__.get('tools_registry', {})
        tools = []
        for tool_name, tool_info in tools_registry.items():
            tools.append({
                "name": tool_name,
                "description": tool_info.get('description', ''),
                "inputSchema": tool_info.get('inputSchema', {})
            })

        # Get resources registry from agent
        resources_registry = agent.__dict__.get('resources_registry', {})
        resources = []
        for resource_uri, resource_info in resources_registry.items():
            resources.append({
                "uri": resource_uri,
                "name": resource_info.get('name', ''),
                "description": resource_info.get('description', ''),
                "mimeType": resource_info.get('mimeType', 'text/plain')
            })

        # Get prompts registry from agent
        prompts_registry = agent.__dict__.get('prompts_registry', {})
        prompts = []
        for prompt_name, prompt_info in prompts_registry.items():
            prompts.append({
                "name": prompt_name,
                "description": prompt_info.get('description', ''),
                "arguments": prompt_info.get('arguments', [])
            })

        return {
            "jsonrpc": "2.0",
            "result": {
                "serverInfo": {
                    "name": f"{agent_id}_agent",
                    "version": "1.0.0",
                    "transport": "http"
                },
                "capabilities": {
                    "tools": {"supported": True, "count": len(tools)},
                    "resources": {"supported": True, "count": len(resources)},
                    "prompts": {"supported": True, "count": len(prompts)}
                },
                "tools": tools,
                "resources": resources,
                "prompts": prompts
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/{agent_id}")
async def mcp_tool_call(agent_id: str, request: dict):
    """MCP Inspector endpoint - call a tool on a specific agent"""
    try:
        # Get the agent
        agent = None
        if agent_id == "scout":
            agent = scout_agent
        elif agent_id == "strategist":
            agent = strategist_agent
        elif agent_id == "executor":
            agent = executor_agent
        else:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        
        if agent is None:
            raise HTTPException(status_code=503, detail=f"Agent '{agent_id}' not initialized")
        
        # Extract tool name and arguments from MCP request
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/list":
            # Return list of tools
            tools_registry = agent.__dict__.get('tools_registry', {})
            tools = []
            for tool_name, tool_info in tools_registry.items():
                tools.append({
                    "name": tool_name,
                    "description": tool_info.get('description', ''),
                    "inputSchema": tool_info.get('inputSchema', {})
                })
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"tools": tools}
            }
        
        elif method == "resources/list":
            # List resources
            resources_registry = agent.__dict__.get('resources_registry', {})
            resources = []
            for resource_uri, resource_info in resources_registry.items():
                resources.append({
                    "uri": resource_uri,
                    "name": resource_info.get('name', ''),
                    "description": resource_info.get('description', ''),
                    "mimeType": resource_info.get('mimeType', 'text/plain')
                })
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"resources": resources}
            }
        
        elif method == "resources/read":
            # Read a specific resource
            uri = params.get("uri")
            resources_registry = agent.__dict__.get('resources_registry', {})
            
            if uri not in resources_registry:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32602,
                        "message": f"Resource '{uri}' not found"
                    }
                }
            
            getter = resources_registry[uri]['getter']
            content = await getter()
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": resources_registry[uri]['mimeType'],
                            "text": json.dumps(content, default=str)
                        }
                    ]
                }
            }
        
        elif method == "prompts/list":
            # List prompts
            prompts_registry = agent.__dict__.get('prompts_registry', {})
            prompts = []
            for prompt_name, prompt_info in prompts_registry.items():
                prompts.append({
                    "name": prompt_name,
                    "description": prompt_info.get('description', ''),
                    "arguments": prompt_info.get('arguments', [])
                })
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"prompts": prompts}
            }
        
        elif method == "prompts/get":
            # Get a specific prompt
            prompt_name = params.get("name")
            prompt_args = params.get("arguments", {})
            prompts_registry = agent.__dict__.get('prompts_registry', {})
            
            if prompt_name not in prompts_registry:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32602,
                        "message": f"Prompt '{prompt_name}' not found"
                    }
                }
            
            generator = prompts_registry[prompt_name]['generator']
            messages = await generator(prompt_args)
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "messages": [
                        {
                            "role": messages.role,
                            "content": messages.content
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            # Call a specific tool
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            tools_registry = agent.__dict__.get('tools_registry', {})
            if tool_name not in tools_registry:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found"
                    }
                }
            
            # Execute the tool
            handler = tools_registry[tool_name]['handler']
            # Call handler with arguments if it accepts them, otherwise call without
            import inspect
            sig = inspect.signature(handler)
            if len(sig.parameters) > 0:
                result = await handler(arguments)
            else:
                result = await handler()
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result)
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not supported"
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }

@app.get("/state")
async def get_game_state():
    """Get current game state"""
    try:
        return {
            "board": coordinator.game_state.board,
            "current_player": coordinator.game_state.current_player,
            "move_number": coordinator.game_state.move_number,
            "game_over": coordinator.game_state.game_over,
            "winner": coordinator.game_state.winner,
            "game_history": [move.model_dump() for move in coordinator.game_state.game_history]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting game state: {str(e)}")

@app.post("/make-move")
async def make_move(move_data: MoveRequest):
    """Make a player move and get AI response via MCP"""
    try:
        # Pass real agents to coordinator for actual timing (local mode only)
        if not distributed_mode:
            print(f"[DEBUG] Setting agents: scout={scout_agent is not None}, strategist={strategist_agent is not None}, executor={executor_agent is not None}")
            coordinator.set_agents(scout_agent, strategist_agent, executor_agent)
            print(f"[DEBUG] Agents set in coordinator: {list(coordinator.agents.keys())}")

        result = await coordinator.process_player_move(move_data.row, move_data.col)

        return result
    except Exception as e:
        print(f"[DEBUG] Error in make_move: {e}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error making move: {str(e)}")

@app.post("/ai-move")
async def ai_move():
    """Trigger AI move when it's the AI's turn"""
    try:
        # Check if it's the AI's turn
        if coordinator.game_state.current_player != "ai":
            return {"success": False, "error": "Not AI's turn"}
        
        if coordinator.game_state.game_over:
            return {"success": False, "error": "Game is over"}
        
        # Pass real agents to coordinator for metrics tracking
        coordinator.set_agents(scout_agent, strategist_agent, executor_agent)
        
        # Get AI move via MCP coordination
        ai_result = await coordinator.get_ai_move()
        
        # Safety check for None result
        if ai_result is None:
            print("[DEBUG] AI result is None, using emergency fallback")
            return {"success": False, "error": "AI move failed - no result returned"}
        
        if ai_result.get("success"):
            return {
                "success": True,
                "move": ai_result.get("move"),
                "reasoning": ai_result.get("reasoning", "AI strategic move")
            }
        else:
            return {"success": False, "error": ai_result.get("error", "AI move failed")}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/reset-game")
async def reset_game():
    """Reset the game to initial state"""
    try:
        coordinator.reset_game()
        return {"message": "Game reset successfully", "board": coordinator.game_state.board}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting game: {str(e)}")

@app.get("/agents/status")
async def get_agent_status():
    """Get status of all agents"""
    try:
        # Handle different agent types
        async def get_agent_info(agent, agent_name):
            if agent is None:
                return None
            
            # Check if it's a LangChain agent (no get_agent_status method)
            if not hasattr(agent, 'get_agent_status'):
                return {
                    "agent_id": agent_name,
                    "status": "active",
                    "framework": "langchain",
                    "model": getattr(agent, 'model_name', 'unknown'),
                    "type": str(type(agent).__name__)
                }
            
            # CrewAI agent with get_agent_status method
            try:
                return await agent.get_agent_status()
            except Exception as e:
                return {
                    "agent_id": agent_name,
                    "status": "error",
                    "error": str(e),
                    "framework": "crewai",
                    "type": str(type(agent).__name__)
                }
        
        status = {
            "scout": await get_agent_info(scout_agent, "scout"),
            "strategist": await get_agent_info(strategist_agent, "strategist"),
            "executor": await get_agent_info(executor_agent, "executor"),
            "coordinator": coordinator.get_agent_status() if coordinator else None
        }
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")

@app.post("/agents/{agent_id}/switch-model")
async def switch_agent_model(agent_id: str, model_config: ModelSwitchRequest):
    """Switch an agent's model via MCP"""
    try:
        # Validate agent exists
        agents = {
            "scout": scout_agent,
            "strategist": strategist_agent,
            "executor": executor_agent
        }
        
        if agent_id not in agents or agents[agent_id] is None:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Validate model exists in registry
        from models.registry import model_registry
        model_config_obj = model_registry.get_model(model_config.model)
        if not model_config_obj:
            available_models = [m.name for m in model_registry.get_available_models()]
            raise HTTPException(
                status_code=422, 
                detail=f"Model '{model_config.model}' not found. Available models: {', '.join(available_models)}"
            )
        
        # Check if model is available
        if not model_config_obj.is_available:
            raise HTTPException(
                status_code=422,
                detail=f"Model '{model_config.model}' is not available. Reason: {model_config_obj._get_unavailable_reason(model_config_obj, False)}"
            )
        
        result = await agents[agent_id].switch_llm_model({"model": model_config.model})
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching model: {str(e)}")

@app.get("/models")
async def get_available_models():
    """Get available models for switching"""
    try:
        from models.registry import model_registry
        return {"models": model_registry.get_model_info()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")

@app.get("/framework")
async def get_framework_info():
    """Get current agent framework information"""
    try:
        from utils.config import config
        agent_framework = config.get("agent_framework", "mode", default="langchain")
        return {
            "current_framework": agent_framework,
            "available_frameworks": ["crewai", "langchain"],
            "description": {
                "crewai": "CrewAI agents with MCP protocol (more complex, full agent coordination)",
                "langchain": "Direct LangChain agents (faster, simpler, more reliable)"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting framework info: {str(e)}")

class FrameworkSwitchRequest(BaseModel):
    """Request model for switching agent framework"""
    framework: str

@app.post("/framework/switch")
async def switch_framework(request: FrameworkSwitchRequest):
    """Switch between CrewAI and LangChain frameworks (requires restart)"""
    try:
        if request.framework not in ["crewai", "langchain"]:
            raise HTTPException(status_code=400, detail="Framework must be 'crewai' or 'langchain'")
        
        # Update config file
        import json
        with open('config.json', 'r') as f:
            config_data = json.load(f)
        if "agent_framework" not in config_data:
            config_data["agent_framework"] = {}
        config_data["agent_framework"]["mode"] = request.framework
        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return {
            "success": True,
            "message": f"Framework switched to {request.framework}. Please restart the application to apply changes.",
            "current_framework": request.framework
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching framework: {str(e)}")

@app.get("/mcp-logs")
async def get_mcp_logs():
    """Get MCP protocol logs"""
    try:
        return {"mcp_logs": coordinator.get_mcp_logs()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting MCP logs: {str(e)}")

@app.get("/debug/agents")
async def debug_agents():
    """Debug endpoint to check agent creation status"""
    return {
        "scout_agent": scout_agent is not None,
        "strategist_agent": strategist_agent is not None, 
        "executor_agent": executor_agent is not None,
        "scout_type": str(type(scout_agent)) if scout_agent else None,
        "strategist_type": str(type(strategist_agent)) if strategist_agent else None,
        "executor_type": str(type(executor_agent)) if executor_agent else None
    }

@app.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str):
    """Get performance metrics for a specific agent"""
    try:
        if agent_id not in ["scout", "strategist", "executor"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get the appropriate agent
        agent = None
        if agent_id == "scout":
            agent = scout_agent
        elif agent_id == "strategist":
            agent = strategist_agent
        elif agent_id == "executor":
            agent = executor_agent
        
        if agent is None:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Handle different agent types
        if not hasattr(agent, 'get_performance_metrics'):
            # LangChain agent - return basic metrics
            return {
                "agent_id": agent_id,
                "status": "active",
                "framework": "langchain",
                "model": getattr(agent, 'model_name', 'unknown'),
                "request_count": 0,
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
                "total_tokens": 0,
                "api_success_rate": 100.0,
                "api_error_count": 0,
                "current_model": getattr(agent, 'model_name', 'unknown'),
                "mcp_connected": False
            }
        
        # CrewAI agent with metrics method
        try:
            return await agent.get_performance_metrics()
        except Exception as e:
            return {
                "agent_id": agent_id,
                "status": "error",
                "framework": "crewai",
                "error": str(e),
                "request_count": 0,
                "avg_response_time": 0.0,
                "api_success_rate": 0.0
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent metrics: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "version": "2.0.0",
        "architecture": "MCP + CrewAI Protocol",
        "agents": {
            "scout": scout_agent is not None,
            "strategist": strategist_agent is not None,
            "executor": executor_agent is not None
        },
        "coordinator": coordinator is not None
    }

if __name__ == "__main__":
    from utils.config import config
    
    # Get API config from config file
    api_config = config.get_api_config()
    
    # Manually call startup to ensure agents are initialized
    import asyncio
    print("🚀 Manually initializing agents...")
    asyncio.run(startup_event())
    
    uvicorn.run(
        "main:app",
        host=api_config.get('host', '0.0.0.0'),
        port=api_config.get('port', 8000),
        reload=True,
        log_level="info"
    ) 
