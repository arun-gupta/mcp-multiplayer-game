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
from game.state import TicTacToeGameState
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
game_state = TicTacToeGameState()

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
    move_number: Optional[int] = None


class GameStateResponse(BaseModel):
    """Response model for game state"""
    board: List[List[str]]
    current_player: str
    move_number: int
    game_over: bool
    winner: Optional[str]
    game_history: List[Dict[str, Any]]
    available_moves: List[Dict[str, Any]]
    statistics: Dict[str, Any]


class TurnSimulationResponse(BaseModel):
    """Response model for turn simulation"""
    move_number: int
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
        <title>Tic Tac Toe Multi-Agent Game</title>
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
            .board-container {{
                display: flex;
                justify-content: center;
                margin: 20px 0;
            }}
            .tic-tac-toe-board {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 5px;
                background: #333;
                padding: 10px;
                border-radius: 15px;
                border: 2px solid #00ff00;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
            }}
            .board-row {{
                display: contents;
            }}
            .board-cell {{
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #222, #1a1a1a);
                border: 2px solid #00ff00;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                font-weight: bold;
                color: #00ff00;
                cursor: pointer;
                transition: all 0.3s ease;
                text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            }}
            .board-cell:hover {{
                background: linear-gradient(135deg, #333, #2a2a2a);
                transform: scale(1.05);
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
            }}
            .board-cell:active {{
                transform: scale(0.95);
            }}
            .main-game-area {{
                margin-bottom: 30px;
            }}
            .game-layout {{
                display: grid;
                grid-template-columns: 1fr 300px;
                gap: 30px;
                align-items: start;
            }}
            .board-section {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .sidebar {{
                display: flex;
                flex-direction: column;
                gap: 20px;
            }}
            .game-status-card, .ai-agents-card {{
                background: linear-gradient(135deg, #333, #222);
                padding: 20px;
                border-radius: 15px;
                border: 1px solid #00ff00;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }}
            .status-item, .agent-item {{
                margin: 10px 0;
                padding: 8px 0;
                border-bottom: 1px solid rgba(0, 255, 0, 0.2);
            }}
            .status-item:last-child, .agent-item:last-child {{
                border-bottom: none;
            }}
            .status-item.winner {{
                color: #00ff00;
                font-weight: bold;
                text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
            }}
            .compact-section {{
                margin-top: 20px;
            }}
            .compact-layout {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .move-history-compact, .mcp-section-compact {{
                background: linear-gradient(135deg, #333, #222);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #00ff00;
            }}
            .move-list {{
                max-height: 120px;
                overflow-y: auto;
            }}
            .move-entry-compact {{
                padding: 5px 0;
                border-bottom: 1px solid rgba(0, 255, 0, 0.2);
                font-size: 12px;
            }}
            .move-entry-compact:last-child {{
                border-bottom: none;
            }}
            .mcp-controls {{
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }}
            .btn.small {{
                padding: 8px 12px;
                font-size: 12px;
            }}
            .compact-content {{
                max-height: 100px;
                overflow-y: auto;
                font-size: 11px;
                background: rgba(0, 0, 0, 0.3);
                padding: 8px;
                border-radius: 5px;
            }}
            .board-controls {{
                text-align: center;
                margin: 20px 0;
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
                <h1>🎮 <span class="emoji">⭕</span> Tic Tac Toe <span class="emoji">❌</span> Multi-Agent Battle <span class="emoji">🎯</span></h1>
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
            
            <div class="game-section main-game-area">
                <div class="game-layout">
                    <div class="board-section">
                        <h2>🎮 Tic Tac Toe Board</h2>
                        <div class="board-container">
                            <div class="tic-tac-toe-board">
                                {chr(10).join([f'<div class="board-row">' + chr(10).join([f'<div class="board-cell" data-row="{row}" data-col="{col}" onclick="makeMove({row}, {col})">{current_state.get("board", [["", "", ""], ["", "", ""], ["", "", ""]])[row][col]}</div>' for col in range(3)]) + '</div>' for row in range(3)])}
                            </div>
                        </div>
                        <div class="board-controls">
                            <button class="btn" onclick="simulateTurn()" {'disabled' if current_state.get('game_over', False) or current_state.get('current_player', 'player') == 'player' else ''}>
                                <span class="emoji">🤖</span> AI MOVE
                            </button>
                            <button class="btn" onclick="resetGame()">
                                <span class="emoji">🔄</span> NEW GAME
                            </button>
                        </div>
                    </div>
                    
                    <div class="sidebar">
                        <div class="game-status-card">
                            <h3><span class="emoji">📊</span> Game Status</h3>
                            <div class="status-item">
                                <span class="emoji">🎯</span> Move: <strong>{current_state.get('move_number', 0)}</strong>
                            </div>
                            <div class="status-item">
                                <span class="emoji">👤</span> Turn: <strong>{current_state.get('current_player', 'player').upper()}</strong>
                            </div>
                            <div class="status-item">
                                <span class="emoji">🏆</span> Status: <strong>{'GAME OVER' if current_state.get('game_over', False) else 'IN PROGRESS'}</strong>
                            </div>
                            {f'<div class="status-item winner"><span class="emoji">🎉</span> Winner: <strong>{current_state.get("winner", "").upper()}</strong></div>' if current_state.get('game_over', False) and current_state.get('winner') else ''}
                        </div>
                        
                        <div class="ai-agents-card">
                            <h3><span class="emoji">🤖</span> AI Agents</h3>
                            <div class="agent-item">
                                <span class="emoji">🔍</span> Scout: <strong>GPT-4</strong>
                            </div>
                            <div class="agent-item">
                                <span class="emoji">🧠</span> Strategist: <strong>Claude 3</strong>
                            </div>
                            <div class="agent-item">
                                <span class="emoji">⚡</span> Executor: <strong>Llama2:7B</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="game-section compact-section">
                <div class="compact-layout">
                    <div class="move-history-compact">
                        <h3><span class="emoji">📜</span> Recent Moves</h3>
                        <div class="move-list">
                            {chr(10).join([f'<div class="move-entry-compact">Move {move.get("move_number", "N/A")}: <span class="emoji">{"👤" if move.get("player") == "player" else "🤖"}</span> {move.get("position", {}).get("value", "?")} at ({move.get("position", {}).get("row", "?"), move.get("position", {}).get("col", "?")})</div>' for move in current_state.get('game_history', [])[-3:]])}
                        </div>
                    </div>
                    
                    <div class="mcp-section-compact">
                        <h3><span class="emoji">📡</span> MCP Protocol</h3>
                        <div class="mcp-controls">
                            <button class="btn small" onclick="loadAgents()">
                                <span class="emoji">🤖</span> Agents
                            </button>
                            <button class="btn small" onclick="loadMCPLogs()">
                                <span class="emoji">📋</span> Logs
                            </button>
                        </div>
                        <div id="agents-content" class="compact-content">
                            <p>Click "Agents" to view AI information</p>
                        </div>
                        <div id="mcp-logs-content" class="compact-content" style="display: none;">
                            <p>Click "Logs" to view MCP protocol messages</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function makeMove(row, col) {{
                const cell = document.querySelector(`[data-row="${{row}}"][data-col="${{col}}"]`);
                if (cell.textContent !== '') {{
                    showNotification('❌ Cell already occupied!', 'error');
                    return;
                }}
                
                try {{
                    // Make player move
                    const response = await fetch('/make-move', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ row: row, col: col }})
                    }});
                    
                    if (response.ok) {{
                        location.reload();
                    }} else {{
                        showNotification('❌ Invalid move!', 'error');
                    }}
                }} catch (error) {{
                    showNotification('❌ Error: ' + error.message, 'error');
                }}
            }}
            
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
                    showNotification('🤖 AI move completed!', 'success');
                    
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
                    btn.innerHTML = '<span class="emoji">🤖</span> AI MOVE';
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
                    const logsContent = document.getElementById('mcp-logs-content');
                    
                    // Hide logs, show agents
                    logsContent.style.display = 'none';
                    agentsContent.style.display = 'block';
                    
                    let html = '';
                    for (const [agentName, agentInfo] of Object.entries(data.agents)) {{
                        html += `
                            <div style="margin-bottom: 8px; padding: 6px; background: rgba(0, 255, 0, 0.1); border-radius: 4px; border-left: 2px solid #00ff00;">
                                <div style="font-weight: bold; color: #00ff00; font-size: 10px;">${{agentInfo.name || agentName.toUpperCase()}}</div>
                                <div style="font-size: 9px; margin: 2px 0;"><strong>Role:</strong> ${{agentInfo.role || 'N/A'}}</div>
                                <div style="font-size: 9px; margin: 2px 0;"><strong>Model:</strong> ${{agentInfo.model || 'N/A'}}</div>
                            </div>
                        `;
                    }}
                    
                    agentsContent.innerHTML = html;
                }} catch (error) {{
                    document.getElementById('agents-content').innerHTML = '<p style="color: #ff4444; font-size: 9px;">Error loading agent information</p>';
                }}
            }}
            
            async function loadMCPLogs() {{
                try {{
                    const response = await fetch('/mcp-logs');
                    const data = await response.json();
                    const logsContent = document.getElementById('mcp-logs-content');
                    const agentsContent = document.getElementById('agents-content');
                    
                    // Hide agents, show logs
                    agentsContent.style.display = 'none';
                    logsContent.style.display = 'block';
                    
                    if (data.mcp_logs && data.mcp_logs.length > 0) {{
                        let html = '';
                        const recentLogs = data.mcp_logs.slice(-5); // Show last 5 logs for compact view
                        
                        recentLogs.forEach(log => {{
                            const timestamp = new Date(log.timestamp).toLocaleTimeString();
                            const agentEmoji = {{
                                'Scout': '🔍',
                                'Strategist': '🧠', 
                                'Executor': '⚡',
                                'GameEngine': '🎮'
                            }}[log.agent] || '🤖';
                            
                            html += `
                                <div style="margin-bottom: 6px; padding: 4px; background: rgba(0, 255, 0, 0.05); border-radius: 3px; border-left: 1px solid #00ff00; font-size: 9px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                                        <span style="color: #00ff00; font-weight: bold;">${{agentEmoji}} ${{log.agent}}</span>
                                        <span style="color: #888;">${{timestamp}}</span>
                                    </div>
                                    <div style="color: #ccc; font-size: 8px;"><strong>Type:</strong> ${{log.message_type}}</div>
                                </div>
                            `;
                        }});
                        
                        logsContent.innerHTML = html;
                    }} else {{
                        logsContent.innerHTML = '<p style="color: #888; font-size: 9px;">No MCP logs yet. Play to see protocol in action!</p>';
                    }}
                }} catch (error) {{
                    document.getElementById('mcp-logs-content').innerHTML = '<p style="color: #ff4444; font-size: 9px;">Error loading MCP logs</p>';
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


@app.post("/make-move")
async def make_move(request: dict):
    """Make a player move on the board"""
    try:
        row = request.get("row")
        col = request.get("col")
        
        if row is None or col is None:
            return {"error": "Row and column are required"}
        
        # Check if it's player's turn
        if game_state.current_player != "player":
            return {"error": "Not player's turn"}
        
        # Check if game is over
        if game_state.game_over:
            return {"error": "Game is over"}
        
        # Make the move
        success = game_state.make_move(row, col, "player")
        
        if not success:
            return {"error": "Invalid move"}
        
        # Log the move
        log_mcp_message("GameEngine", "PlayerMove", {
            "row": row,
            "col": col,
            "symbol": game_state.player_symbol
        })
        
        return {"success": True, "message": "Move made successfully"}
        
    except Exception as e:
        print(f"Error in make_move: {e}")
        return {"error": "Internal server error"}

@app.post("/simulate-turn", response_model=TurnSimulationResponse)
async def simulate_turn(request: SimulateTurnRequest = SimulateTurnRequest()):
    """
    Simulate AI's turn using the three-agent system:
    1. Scout Agent observes the environment
    2. Strategist Agent creates a plan
    3. Executor Agent executes the plan
    """
    try:
        # Check if it's AI's turn
        if game_state.current_player != "ai":
            raise HTTPException(status_code=400, detail="Not AI's turn")
        
        # Check if game is over
        if game_state.game_over:
            raise HTTPException(status_code=400, detail="Game is already over. Start a new game.")
        
        # Step 1: Scout Agent observes the environment
        print("\n" + "="*50)
        print("AI TURN SIMULATION STARTED")
        print("="*50)
        
        observation = scout_agent.observe_environment()
        log_mcp_message("Scout", "Observation", observation.dict())
        
        # Step 2: Strategist Agent creates a plan
        plan = strategist_agent.create_plan(observation)
        log_mcp_message("Strategist", "Plan", plan.dict())
        
        # Step 3: Executor Agent executes the plan
        action_result = executor_agent.execute_plan(plan)
        log_mcp_message("Executor", "ExecutionResult", action_result.dict())
        
        print("="*50)
        print("AI TURN SIMULATION COMPLETED")
        print("="*50)
        
        return TurnSimulationResponse(
            move_number=observation.move_number + 1,
            observation=observation.dict(),
            plan=plan.dict(),
            execution_result=action_result.dict(),
            game_state_update=action_result.dict(),
            mcp_logs=mcp_logs[-10:]  # Last 10 MCP messages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating AI move: {str(e)}")


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