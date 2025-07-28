"""
Main FastAPI Application
Multi-Agent Game Simulation with MCP-style Architecture
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os
import json
from datetime import datetime

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, that's okay
    pass

# Import our modules
from game.state import GameStateManager
from agents.scout import ScoutAgent
from agents.strategist import StrategistAgent
from agents.executor import ExecutorAgent
from schemas.observation import Observation
from schemas.plan import Plan
from schemas.action_result import TurnResult, GameStateUpdate


# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Game Simulation",
    description="A turn-based strategy game simulation using CrewAI and MCP-style architecture",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game state manager
game_manager = GameStateManager()

# Global agents
scout_agent = None
strategist_agent = None
executor_agent = None

# MCP Protocol logs
mcp_logs = []


def initialize_agents():
    """Initialize all agents"""
    global scout_agent, strategist_agent, executor_agent
    
    current_state = game_manager.get_current_state()
    scout_agent = ScoutAgent(current_state)
    strategist_agent = StrategistAgent()
    executor_agent = ExecutorAgent(current_state)


def log_mcp_message(agent: str, message_type: str, data: Dict[str, Any]):
    """Log MCP protocol messages"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "message_type": message_type,
        "data": data
    }
    mcp_logs.append(log_entry)
    print(f"[MCP] {agent} -> {message_type}: {json.dumps(data, indent=2)}")


# Pydantic models for API requests/responses
class SimulateTurnRequest(BaseModel):
    """Request model for simulating a turn"""
    turn_number: Optional[int] = None


class GameStateResponse(BaseModel):
    """Response model for game state"""
    game_state: Dict[str, Any]
    map_ascii: str
    turn_history: List[Dict[str, Any]]
    action_logs: List[Dict[str, Any]]


class TurnSimulationResponse(BaseModel):
    """Response model for turn simulation"""
    turn_number: int
    observation: Dict[str, Any]
    plan: Dict[str, Any]
    execution_result: Dict[str, Any]
    game_state_update: Dict[str, Any]
    mcp_logs: List[Dict[str, Any]]


class AgentInfoResponse(BaseModel):
    """Response model for agent information"""
    agents: Dict[str, Dict[str, Any]]


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    initialize_agents()





@app.get("/", response_class=HTMLResponse)
async def game_dashboard():
    """Game dashboard with visualization"""
    current_state = game_manager.get_state_for_api()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Multi-Agent Game Simulation</title>
        <style>
            body {{ font-family: monospace; margin: 20px; background: #1a1a1a; color: #00ff00; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .game-section {{ margin-bottom: 30px; }}
            .map {{ background: #000; padding: 20px; border-radius: 5px; white-space: pre; font-size: 14px; }}
            .controls {{ text-align: center; margin: 20px 0; }}
            .btn {{ background: #00ff00; color: #000; border: none; padding: 10px 20px; margin: 5px; cursor: pointer; border-radius: 3px; }}
            .btn:hover {{ background: #00cc00; }}
            .logs {{ background: #000; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto; }}
            .agent-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .agent-card {{ background: #333; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎮 Multi-Agent Game Simulation</h1>
                <p>MCP-style architecture with CrewAI agents</p>
            </div>
            
            <div class="game-section">
                <h2>Current Game State</h2>
                <div class="map">{current_state.get('map_ascii', 'No map available')}</div>
                
                <div class="controls">
                    <button class="btn" onclick="simulateTurn()">Simulate Turn</button>
                    <button class="btn" onclick="resetGame()">Reset Game</button>
                    <button class="btn" onclick="refreshState()">Refresh State</button>
                </div>
            </div>
            
            <div class="game-section">
                <h2>Game Information</h2>
                <div class="agent-info">
                    <div class="agent-card">
                        <h3>Player Status</h3>
                        <p>Health: {current_state.get('game_state', {}).get('player_health', 0)}/{current_state.get('game_state', {}).get('player_max_health', 100)}</p>
                        <p>Position: {current_state.get('game_state', {}).get('player_position', [0, 0])}</p>
                        <p>Turn: {current_state.get('game_state', {}).get('turn_number', 1)}</p>
                    </div>
                    <div class="agent-card">
                        <h3>Enemies</h3>
                        <p>Remaining: {current_state.get('game_state', {}).get('enemies_remaining', 0)}</p>
                    </div>
                    <div class="agent-card">
                        <h3>Items</h3>
                        <p>Available: {current_state.get('game_state', {}).get('items_remaining', 0)}</p>
                    </div>
                </div>
            </div>
            
            <div class="game-section">
                <h2>Recent Turn History</h2>
                <div class="logs">
                    {chr(10).join([f"Turn {turn.get('turn_number', 'N/A')}: {turn.get('summary', 'No summary')}" for turn in current_state.get('turn_history', [])[-5:]])}
                </div>
            </div>
        </div>
        
        <script>
            async function simulateTurn() {{
                try {{
                    const response = await fetch('/simulate-turn', {{ method: 'POST' }});
                    const result = await response.json();
                    alert('Turn simulated! Check the logs for details.');
                    location.reload();
                }} catch (error) {{
                    alert('Error simulating turn: ' + error.message);
                }}
            }}
            
            async function resetGame() {{
                try {{
                    const response = await fetch('/reset-game', {{ method: 'POST' }});
                    alert('Game reset!');
                    location.reload();
                }} catch (error) {{
                    alert('Error resetting game: ' + error.message);
                }}
            }}
            
            async function refreshState() {{
                location.reload();
            }}
        </script>
    </body>
    </html>
    """
    
    return html_content


@app.get("/state", response_model=GameStateResponse)
async def get_game_state():
    """Get current game state"""
    try:
        state_data = game_manager.get_state_for_api()
        return GameStateResponse(**state_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting game state: {str(e)}")


@app.post("/simulate-turn", response_model=TurnSimulationResponse)
async def simulate_turn(request: SimulateTurnRequest):
    """
    Simulate a complete game turn using the three-agent system:
    1. Scout Agent observes the environment
    2. Strategist Agent creates a plan
    3. Executor Agent executes the plan
    """
    try:
        # Get current game state
        current_state = game_manager.get_current_state()
        
        # Step 1: Scout Agent observes the environment
        print("\n" + "="*50)
        print("TURN SIMULATION STARTED")
        print("="*50)
        
        observation = scout_agent.observe_environment()
        log_mcp_message("Scout", "Observation", observation.dict())
        
        # Step 2: Strategist Agent creates a plan
        plan = strategist_agent.create_strategic_plan(observation)
        log_mcp_message("Strategist", "Plan", plan.dict())
        
        # Step 3: Executor Agent executes the plan
        turn_result = executor_agent.execute_plan(plan)
        log_mcp_message("Executor", "ExecutionResult", turn_result.dict())
        
        # Step 4: Update game state
        game_state_update = game_manager.update_state_from_turn_result(turn_result)
        log_mcp_message("GameEngine", "StateUpdate", game_state_update.dict())
        
        # Advance turn
        current_state.advance_turn()
        
        print("="*50)
        print("TURN SIMULATION COMPLETED")
        print("="*50)
        
        return TurnSimulationResponse(
            turn_number=observation.turn_number,
            observation=observation.dict(),
            plan=plan.dict(),
            execution_result=turn_result.dict(),
            game_state_update=game_state_update.dict(),
            mcp_logs=mcp_logs[-10:]  # Last 10 MCP messages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating turn: {str(e)}")


@app.get("/agents", response_model=AgentInfoResponse)
async def get_agent_info():
    """Get information about all agents"""
    try:
        agent_info = {
            "scout": scout_agent.get_agent_info() if scout_agent else {},
            "strategist": strategist_agent.get_agent_info() if strategist_agent else {},
            "executor": executor_agent.get_agent_info() if executor_agent else {}
        }
        return AgentInfoResponse(agents=agent_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent info: {str(e)}")


@app.get("/mcp-logs")
async def get_mcp_logs():
    """Get MCP protocol logs"""
    try:
        return {"mcp_logs": mcp_logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting MCP logs: {str(e)}")


@app.post("/reset-game")
async def reset_game():
    """Reset the game to initial state"""
    try:
        global game_manager, scout_agent, strategist_agent, executor_agent
        
        # Reset game state
        game_manager.initialize_new_game()
        
        # Reinitialize agents
        initialize_agents()
        
        # Clear MCP logs
        mcp_logs.clear()
        
        return {"message": "Game reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting game: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Get the port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "message": "Multi-Agent Game Simulation is running!",
        "endpoints": {
            "game_dashboard": f"http://localhost:{port}",
            "api_documentation": f"http://localhost:{port}/docs",
            "health_check": f"http://localhost:{port}/health"
        }
    }


if __name__ == "__main__":
    # Set default port
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    print("🎮 Multi-Agent Game Simulation")
    print("="*50)
    print("🚀 Starting server...")
    print(f"📍 Server will be available at:")
    print(f"   🌐 Game Dashboard: http://localhost:{port}")
    print(f"   📚 API Documentation: http://localhost:{port}/docs")
    print(f"   🔍 Health Check: http://localhost:{port}/health")
    print("="*50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 