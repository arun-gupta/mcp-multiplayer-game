"""
Main FastAPI Application
Multi-Agent Game Simulation with MCP-style Architecture
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

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, that's okay
    pass

# Import our modules
from game.state import RPSGameState
from agents.scout import ScoutAgent
from agents.strategist import StrategistAgent
from agents.executor import ExecutorAgent
from schemas.observation import Observation
from schemas.plan import Plan
from schemas.action_result import ActionResult


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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global game state
game_state = RPSGameState()

# Global agents
scout_agent = None
strategist_agent = None
executor_agent = None

# MCP Protocol logs
mcp_logs = []


def initialize_agents():
    """Initialize all agents"""
    global scout_agent, strategist_agent, executor_agent
    
    scout_agent = ScoutAgent(game_state)
    strategist_agent = StrategistAgent()
    executor_agent = ExecutorAgent(game_state)


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
    game_history: List[Dict[str, Any]]
    recent_moves: List[Dict[str, Any]]
    statistics: Dict[str, Any]


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





@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon"""
    return FileResponse("static/favicon.ico")

@app.get("/", response_class=HTMLResponse)
async def game_dashboard():
    """Game dashboard with visualization"""
    current_state = game_state.get_state_for_api()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rock-Paper-Scissors Multi-Agent Game</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <style>
            body {{ 
                font-family: 'Courier New', monospace; 
                margin: 0; 
                background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%); 
                color: #00ff00; 
                overflow-x: hidden;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ 
                text-align: center; 
                margin-bottom: 30px; 
                animation: glow 2s ease-in-out infinite alternate;
            }}
            @keyframes glow {{
                from {{ text-shadow: 0 0 5px #00ff00, 0 0 10px #00ff00, 0 0 15px #00ff00; }}
                to {{ text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00, 0 0 30px #00ff00; }}
            }}
            .game-section {{ 
                margin-bottom: 30px; 
                animation: slideIn 0.5s ease-out;
            }}
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .score-board {{ 
                background: linear-gradient(45deg, #000, #1a1a1a); 
                padding: 30px; 
                border-radius: 15px; 
                text-align: center; 
                font-size: 24px; 
                border: 2px solid #00ff00;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
                position: relative;
                overflow: hidden;
            }}
            .score-board::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, transparent, rgba(0, 255, 0, 0.1), transparent);
                animation: shimmer 3s infinite;
            }}
            @keyframes shimmer {{
                0% {{ transform: translateX(-100%) translateY(-100%) rotate(45deg); }}
                100% {{ transform: translateX(100%) translateY(100%) rotate(45deg); }}
            }}
            .score-display {{
                display: flex;
                justify-content: space-around;
                align-items: center;
                margin: 20px 0;
            }}
            .player-score, .opponent-score {{
                padding: 15px 30px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 28px;
                transition: all 0.3s ease;
            }}
            .player-score {{
                background: linear-gradient(45deg, #00ff00, #00cc00);
                color: #000;
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
            }}
            .opponent-score {{
                background: linear-gradient(45deg, #ff4444, #cc0000);
                color: #fff;
                box-shadow: 0 0 15px rgba(255, 68, 68, 0.5);
            }}
            .controls {{ 
                text-align: center; 
                margin: 30px 0; 
            }}
            .btn {{ 
                background: linear-gradient(45deg, #00ff00, #00cc00); 
                color: #000; 
                border: none; 
                padding: 15px 30px; 
                margin: 10px; 
                cursor: pointer; 
                border-radius: 25px; 
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0, 255, 0, 0.3);
                position: relative;
                overflow: hidden;
            }}
            .btn:hover {{ 
                background: linear-gradient(45deg, #00cc00, #009900); 
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0, 255, 0, 0.5);
            }}
            .btn:active {{ 
                transform: translateY(0);
            }}
            .btn:disabled {{
                background: #666;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }}
            .btn::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.5s;
            }}
            .btn:hover::before {{
                left: 100%;
            }}
            .agent-info {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
            }}
            .agent-card {{ 
                background: linear-gradient(135deg, #333, #222); 
                padding: 20px; 
                border-radius: 15px; 
                border: 1px solid #00ff00;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            .agent-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 255, 0, 0.2);
            }}
            .agent-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #00ff00, #00cc00, #00ff00);
                animation: loading 2s infinite;
            }}
            @keyframes loading {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
            .move-history {{ 
                background: linear-gradient(135deg, #000, #1a1a1a); 
                padding: 20px; 
                border-radius: 15px; 
                border: 1px solid #00ff00;
                max-height: 400px;
                overflow-y: auto;
            }}
            .move-entry {{ 
                margin: 10px 0; 
                padding: 15px; 
                border-left: 4px solid #00ff00; 
                background: rgba(0, 255, 0, 0.1);
                border-radius: 5px;
                transition: all 0.3s ease;
                animation: fadeIn 0.5s ease-out;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateX(-20px); }}
                to {{ opacity: 1; transform: translateX(0); }}
            }}
            .move-entry:hover {{
                background: rgba(0, 255, 0, 0.2);
                transform: translateX(5px);
            }}
            .move-result {{
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 15px;
                margin-left: 10px;
            }}
            .result-win {{ background: #00ff00; color: #000; }}
            .result-lose {{ background: #ff4444; color: #fff; }}
            .result-draw {{ background: #ffff00; color: #000; }}
            .game-over {{
                background: linear-gradient(45deg, #ff4444, #cc0000);
                color: #fff;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                animation: pulse 1s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
            .progress-bar {{
                width: 100%;
                height: 20px;
                background: #333;
                border-radius: 10px;
                overflow: hidden;
                margin: 10px 0;
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #00ff00, #00cc00);
                transition: width 0.5s ease;
                border-radius: 10px;
            }}
            .thinking {{
                display: inline-block;
                animation: thinking 1.5s infinite;
            }}
            @keyframes thinking {{
                0%, 20% {{ content: "🤔"; }}
                40% {{ content: "💭"; }}
                60% {{ content: "🧠"; }}
                80%, 100% {{ content: "💡"; }}
            }}
            .emoji {{
                font-size: 24px;
                margin: 0 10px;
            }}
            .loading {{
                display: none;
                text-align: center;
                padding: 20px;
            }}
            .spinner {{
                border: 4px solid #333;
                border-top: 4px solid #00ff00;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎮 <span class="emoji">✂️</span> Rock-Paper-Scissors <span class="emoji">🪨</span> Multi-Agent Battle <span class="emoji">📄</span></h1>
                <p>Watch three AI agents work together using MCP protocol!</p>
            </div>
            
            <div class="game-section">
                <h2>🏆 Live Battle Arena</h2>
                <div class="score-board">
                    <div class="score-display">
                        <div class="player-score">
                            <div class="emoji">👤</div>
                            <div>PLAYER</div>
                            <div>{current_state.get('game_state', {}).get('player_score', 0)}</div>
                        </div>
                        <div class="emoji">⚔️</div>
                        <div class="opponent-score">
                            <div class="emoji">🤖</div>
                            <div>OPPONENT</div>
                            <div>{current_state.get('game_state', {}).get('opponent_score', 0)}</div>
                        </div>
                    </div>
                    
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(current_state.get('game_state', {}).get('current_round', 1) / current_state.get('game_state', {}).get('max_rounds', 10)) * 100}%"></div>
                    </div>
                    
                    <p>Round: <strong>{current_state.get('game_state', {}).get('current_round', 1)}</strong> / {current_state.get('game_state', {}).get('max_rounds', 10)}</p>
                    <p>Rounds Remaining: <strong>{current_state.get('game_state', {}).get('rounds_remaining', 10)}</strong></p>
                    
                    {f'<div class="game-over"><span class="emoji">🏁</span> GAME OVER! Winner: {current_state.get("game_state", {}).get("winner", "Unknown").title()} <span class="emoji">🏆</span></div>' if current_state.get('game_state', {}).get('game_over', False) else ""}
                </div>
                
                <div class="controls">
                    <button class="btn" onclick="simulateTurn()" {"disabled" if current_state.get('game_state', {}).get('game_over', False) else ""}>
                        <span class="emoji">🎯</span> PLAY ROUND
                    </button>
                    <button class="btn" onclick="resetGame()">
                        <span class="emoji">🔄</span> NEW GAME
                    </button>
                    <button class="btn" onclick="refreshState()">
                        <span class="emoji">🔄</span> REFRESH
                    </button>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>🤖 Agents are thinking...</p>
                </div>
            </div>
            
            <div class="game-section">
                <h2>📊 Battle Statistics</h2>
                <div class="agent-info">
                    <div class="agent-card">
                        <h3><span class="emoji">👤</span> Player Stats</h3>
                        <p><span class="emoji">✅</span> Wins: <strong>{current_state.get('statistics', {}).get('player_wins', 0)}</strong></p>
                        <p><span class="emoji">❌</span> Losses: <strong>{current_state.get('statistics', {}).get('opponent_wins', 0)}</strong></p>
                        <p><span class="emoji">🤝</span> Draws: <strong>{current_state.get('statistics', {}).get('draws', 0)}</strong></p>
                    </div>
                    <div class="agent-card">
                        <h3><span class="emoji">📈</span> Game Progress</h3>
                        <p><span class="emoji">🎯</span> Total Rounds: <strong>{current_state.get('statistics', {}).get('total_rounds', 0)}</strong></p>
                        <p><span class="emoji">🏆</span> Win Rate: <strong>{(current_state.get('statistics', {}).get('player_wins', 0) / max(1, current_state.get('statistics', {}).get('total_rounds', 1)) * 100):.1f}%</strong></p>
                    </div>
                    <div class="agent-card">
                        <h3><span class="emoji">🤖</span> AI Agents</h3>
                        <p><span class="emoji">🔍</span> Scout: <strong>OpenAI GPT-4</strong></p>
                        <p><span class="emoji">🧠</span> Strategist: <strong>Claude 3 Sonnet</strong></p>
                        <p><span class="emoji">⚡</span> Executor: <strong>Llama2:7B</strong></p>
                    </div>
                </div>
            </div>
            
            <div class="game-section">
                <h2>📜 Battle History</h2>
                <div class="move-history">
                    {chr(10).join([f'<div class="move-entry">Round {move.get("round_number", "N/A")}: <span class="emoji">{"🪨" if move.get("player_move") == "rock" else "📄" if move.get("player_move") == "paper" else "✂️"}</span> Player {move.get("player_move", "?").upper()} <span class="emoji">⚔️</span> <span class="emoji">{"🪨" if move.get("opponent_move") == "rock" else "📄" if move.get("opponent_move") == "paper" else "✂️"}</span> Opponent {move.get("opponent_move", "?").upper()} <span class="move-result result-{move.get("result", "?").lower()}">{move.get("result", "?").upper()}</span></div>' for move in current_state.get('recent_moves', [])[-5:]])}
                </div>
            </div>
            
            <div class="game-section">
                <h2>🤖 AI Agents & MCP Protocol</h2>
                <div class="agent-info">
                    <div class="agent-card" id="agents-card">
                        <h3><span class="emoji">🤖</span> Agent Information</h3>
                        <div id="agents-content">
                            <p>Loading agent information...</p>
                        </div>
                        <button class="btn" onclick="loadAgents()" style="margin-top: 10px; padding: 8px 16px; font-size: 12px;">
                            <span class="emoji">🔄</span> Refresh Agents
                        </button>
                    </div>
                    <div class="agent-card" id="mcp-logs-card">
                        <h3><span class="emoji">📡</span> MCP Protocol Logs</h3>
                        <div id="mcp-logs-content">
                            <p>Loading MCP logs...</p>
                        </div>
                        <button class="btn" onclick="loadMCPLogs()" style="margin-top: 10px; padding: 8px 16px; font-size: 12px;">
                            <span class="emoji">🔄</span> Refresh Logs
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function simulateTurn() {{
                const loading = document.getElementById('loading');
                const btn = event.target;
                
                try {{
                    // Show loading animation
                    loading.style.display = 'block';
                    btn.disabled = true;
                    btn.innerHTML = '<span class="emoji">🤔</span> THINKING...';
                    
                    const response = await fetch('/simulate-turn', {{ method: 'POST' }});
                    const result = await response.json();
                    
                    // Show success message
                    showNotification('🎯 Round completed! Check the battle history below.', 'success');
                    
                    // Reload after a short delay to show the animation
                    setTimeout(() => {{
                        location.reload();
                    }}, 1000);
                    
                }} catch (error) {{
                    showNotification('❌ Error: ' + error.message, 'error');
                }} finally {{
                    // Hide loading animation
                    loading.style.display = 'none';
                    btn.disabled = false;
                    btn.innerHTML = '<span class="emoji">🎯</span> PLAY ROUND';
                }}
            }}
            
            async function resetGame() {{
                const btn = event.target;
                
                try {{
                    btn.disabled = true;
                    btn.innerHTML = '<span class="emoji">🔄</span> RESETTING...';
                    
                    const response = await fetch('/reset-game', {{ method: 'POST' }});
                    showNotification('🔄 New game started! Ready for battle!', 'success');
                    
                    setTimeout(() => {{
                        location.reload();
                    }}, 1000);
                    
                }} catch (error) {{
                    showNotification('❌ Error: ' + error.message, 'error');
                }} finally {{
                    btn.disabled = false;
                    btn.innerHTML = '<span class="emoji">🔄</span> NEW GAME';
                }}
            }}
            
            async function refreshState() {{
                const btn = event.target;
                btn.innerHTML = '<span class="emoji">🔄</span> REFRESHING...';
                location.reload();
            }}
            
            function showNotification(message, type) {{
                // Create notification element
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 20px;
                    border-radius: 10px;
                    color: white;
                    font-weight: bold;
                    z-index: 1000;
                    animation: slideInRight 0.5s ease-out;
                    background: ${{type === 'success' ? 'linear-gradient(45deg, #00ff00, #00cc00)' : 'linear-gradient(45deg, #ff4444, #cc0000)'}};
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                `;
                notification.textContent = message;
                
                // Add to page
                document.body.appendChild(notification);
                
                // Remove after 3 seconds
                setTimeout(() => {{
                    notification.style.animation = 'slideOutRight 0.5s ease-in';
                    setTimeout(() => {{
                        document.body.removeChild(notification);
                    }}, 500);
                }}, 3000);
            }}
            
            // Add CSS animations for notifications
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideInRight {{
                    from {{ transform: translateX(100%); opacity: 0; }}
                    to {{ transform: translateX(0); opacity: 1; }}
                }}
                @keyframes slideOutRight {{
                    from {{ transform: translateX(0); opacity: 1; }}
                    to {{ transform: translateX(100%); opacity: 0; }}
                }}
            `;
            document.head.appendChild(style);
            
            // Add some interactive effects
            document.addEventListener('DOMContentLoaded', function() {{
                // Add hover effects to move entries
                const moveEntries = document.querySelectorAll('.move-entry');
                moveEntries.forEach(entry => {{
                    entry.addEventListener('mouseenter', function() {{
                        this.style.transform = 'translateX(10px) scale(1.02)';
                    }});
                    entry.addEventListener('mouseleave', function() {{
                        this.style.transform = 'translateX(0) scale(1)';
                    }});
                }});
                
                // Add click effects to buttons
                const buttons = document.querySelectorAll('.btn');
                buttons.forEach(btn => {{
                    btn.addEventListener('click', function() {{
                        this.style.transform = 'scale(0.95)';
                        setTimeout(() => {{
                            this.style.transform = '';
                        }}, 150);
                    }});
                }});
                
                // Load initial data
                loadAgents();
                loadMCPLogs();
            }});
            
            async function loadAgents() {{
                try {{
                    const response = await fetch('/agents');
                    const data = await response.json();
                    const agentsContent = document.getElementById('agents-content');
                    
                    let html = '';
                    for (const [agentName, agentInfo] of Object.entries(data.agents)) {{
                        html += `
                            <div style="margin-bottom: 15px; padding: 10px; background: rgba(0, 255, 0, 0.1); border-radius: 8px; border-left: 3px solid #00ff00;">
                                <h4 style="margin: 0 0 8px 0; color: #00ff00;">${{agentInfo.name || agentName.toUpperCase()}}</h4>
                                <p style="margin: 2px 0; font-size: 12px;"><strong>Role:</strong> ${{agentInfo.role || 'N/A'}}</p>
                                <p style="margin: 2px 0; font-size: 12px;"><strong>Model:</strong> ${{agentInfo.model || 'N/A'}}</p>
                                <p style="margin: 2px 0; font-size: 12px;"><strong>Description:</strong> ${{agentInfo.description || 'N/A'}}</p>
                                <p style="margin: 2px 0; font-size: 12px;"><strong>Capabilities:</strong> ${{agentInfo.capabilities ? agentInfo.capabilities.join(', ') : 'N/A'}}</p>
                            </div>
                        `;
                    }}
                    
                    agentsContent.innerHTML = html;
                }} catch (error) {{
                    document.getElementById('agents-content').innerHTML = '<p style="color: #ff4444;">Error loading agent information</p>';
                }}
            }}
            
            async function loadMCPLogs() {{
                try {{
                    const response = await fetch('/mcp-logs');
                    const data = await response.json();
                    const logsContent = document.getElementById('mcp-logs-content');
                    
                    if (data.mcp_logs && data.mcp_logs.length > 0) {{
                        let html = '';
                        const recentLogs = data.mcp_logs.slice(-10); // Show last 10 logs
                        
                        recentLogs.forEach(log => {{
                            const timestamp = new Date(log.timestamp).toLocaleTimeString();
                            const agentEmoji = {{
                                'Scout': '🔍',
                                'Strategist': '🧠', 
                                'Executor': '⚡',
                                'GameEngine': '🎮'
                            }}[log.agent] || '🤖';
                            
                            html += `
                                <div style="margin-bottom: 10px; padding: 8px; background: rgba(0, 255, 0, 0.05); border-radius: 5px; border-left: 2px solid #00ff00; font-size: 11px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                        <span style="color: #00ff00; font-weight: bold;">${{agentEmoji}} ${{log.agent}}</span>
                                        <span style="color: #888;">${{timestamp}}</span>
                                    </div>
                                    <div style="color: #ccc; margin-bottom: 3px;"><strong>Type:</strong> ${{log.message_type}}</div>
                                    <div style="color: #aaa; font-size: 10px; max-height: 60px; overflow-y: auto;">
                                        <pre style="margin: 0; white-space: pre-wrap;">${{JSON.stringify(log.data, null, 2)}}</pre>
                                    </div>
                                </div>
                            `;
                        }});
                        
                        logsContent.innerHTML = html;
                    }} else {{
                        logsContent.innerHTML = '<p style="color: #888;">No MCP logs available yet. Play a round to see the protocol in action!</p>';
                    }}
                }} catch (error) {{
                    document.getElementById('mcp-logs-content').innerHTML = '<p style="color: #ff4444;">Error loading MCP logs</p>';
                }}
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
        state_data = game_state.get_state_for_api()
        return GameStateResponse(**state_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting game state: {str(e)}")


@app.post("/simulate-turn", response_model=TurnSimulationResponse)
async def simulate_turn(request: SimulateTurnRequest = SimulateTurnRequest()):
    """
    Simulate a complete game round using the three-agent system:
    1. Scout Agent observes the environment
    2. Strategist Agent creates a plan
    3. Executor Agent executes the plan
    """
    try:
        # Check if game is over
        if game_state.game_over:
            raise HTTPException(status_code=400, detail="Game is already over. Start a new game.")
        
        # Step 1: Scout Agent observes the environment
        print("\n" + "="*50)
        print("ROUND SIMULATION STARTED")
        print("="*50)
        
        observation = scout_agent.observe_environment()
        log_mcp_message("Scout", "Observation", observation.dict())
        
        # Step 2: Strategist Agent creates a plan
        plan = strategist_agent.create_strategic_plan(observation)
        log_mcp_message("Strategist", "Plan", plan.dict())
        
        # Step 3: Executor Agent executes the plan
        action_result = executor_agent.execute_plan(plan)
        log_mcp_message("Executor", "ExecutionResult", action_result.dict())
        
        # Step 4: Update game state
        game_state_update = game_state.update_from_result(action_result)
        log_mcp_message("GameEngine", "StateUpdate", game_state_update)
        
        print("="*50)
        print("ROUND SIMULATION COMPLETED")
        print("="*50)
        
        return TurnSimulationResponse(
            turn_number=observation.current_round,
            observation=observation.dict(),
            plan=plan.dict(),
            execution_result=action_result.dict(),
            game_state_update=game_state_update,
            mcp_logs=mcp_logs[-10:]  # Last 10 MCP messages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating round: {str(e)}")


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
        global game_state, scout_agent, strategist_agent, executor_agent
        
        # Reset game state
        game_state.initialize_new_game()
        
        # Reinitialize agents
        initialize_agents()
        
        # Clear MCP logs
        mcp_logs.clear()
        
        return {"message": "New game started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting new game: {str(e)}")


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