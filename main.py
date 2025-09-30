"""
Main FastAPI Application with MCP Protocol
Multi-Agent Game Simulation using CrewAI + MCP
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
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
from agents.scout import ScoutMCPAgent
from agents.strategist import StrategistMCPAgent  
from agents.executor import ExecutorMCPAgent
from models.registry import model_registry
from models.factory import ModelFactory

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
coordinator = MCPGameCoordinator()
scout_agent = None
strategist_agent = None
executor_agent = None

# Metrics are now handled by individual MCP agents via their tools

# Pydantic models for API requests/responses
class MoveRequest(BaseModel):
    """Request model for making a move"""
    row: int
    col: int

class ModelSwitchRequest(BaseModel):
    """Request model for switching agent model"""
    agent: str
    model: str

class AgentStatusResponse(BaseModel):
    """Response model for agent status"""
    agents: Dict[str, Any]
    coordinator: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Start MCP agents and coordinator"""
    global scout_agent, strategist_agent, executor_agent
    
    print("🚀 Starting MCP CrewAI system...")
    
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
    
    # Initialize agents with MCP servers
    try:
        scout_agent = ScoutMCPAgent({"model": default_model})
        print(f"✅ Scout MCP Agent created with {default_model}")
    except Exception as e:
        print(f"❌ Error creating Scout MCP Agent: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        scout_agent = None
    
    try:
        strategist_agent = StrategistMCPAgent({"model": default_model})
        print(f"✅ Strategist MCP Agent created with {default_model}")
    except Exception as e:
        print(f"❌ Error creating Strategist MCP Agent: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        strategist_agent = None
    
    try:
        executor_agent = ExecutorMCPAgent({"model": default_model})
        print(f"✅ Executor MCP Agent created with {default_model}")
    except Exception as e:
        print(f"❌ Error creating Executor MCP Agent: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        executor_agent = None

    print(f"🔍 Agent status: scout={scout_agent is not None}, strategist={strategist_agent is not None}, executor={executor_agent is not None}")

    # Start MCP servers
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
    
    # Initialize coordinator connections
    try:
        await coordinator.initialize_agents()
        print("✅ Coordinator initialized")
    except Exception as e:
        print(f"❌ Error initializing coordinator: {e}")
    
    # Show model availability summary
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

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/state")
async def get_game_state():
    """Get current game state"""
    try:
        return {
            "board": coordinator.game_state.board,
            "current_player": coordinator.game_state.current_player,
            "move_number": coordinator.game_state.move_number,
            "game_over": coordinator.game_state.game_over,
            "winner": coordinator.game_state.winner
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting game state: {str(e)}")

@app.post("/make-move")
async def make_move(move_data: MoveRequest):
    """Make a player move and get AI response via MCP"""
    try:
        # Pass real agents to coordinator for actual timing
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
    """Get status of all MCP agents"""
    try:
        status = {
            "scout": await scout_agent.get_agent_status() if scout_agent else None,
            "strategist": await strategist_agent.get_agent_status() if strategist_agent else None,
            "executor": await executor_agent.get_agent_status() if executor_agent else None,
            "coordinator": coordinator.get_agent_status()
        }
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")

@app.post("/agents/{agent_id}/switch-model")
async def switch_agent_model(agent_id: str, model_config: ModelSwitchRequest):
    """Switch an agent's model via MCP"""
    try:
        agents = {
            "scout": scout_agent,
            "strategist": strategist_agent,
            "executor": executor_agent
        }
        
        if agent_id not in agents or agents[agent_id] is None:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        result = await agents[agent_id].switch_llm_model({"model": model_config.model})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching model: {str(e)}")

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
    """Get performance metrics for a specific agent via MCP"""
    try:
        agents = {
            "scout": scout_agent,
            "strategist": strategist_agent,
            "executor": executor_agent
        }
        
        if agent_id not in agents or agents[agent_id] is None:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get metrics from the agent's MCP tool
        metrics = await agents[agent_id].get_performance_metrics()
        return metrics
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 
