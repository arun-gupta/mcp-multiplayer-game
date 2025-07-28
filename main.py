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
from models.registry import model_registry
from models.factory import ModelFactory
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
                position: relative;
            }}
            .github-corner {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }}
            .github-corner a {{
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px 15px;
                background: linear-gradient(135deg, rgba(0, 255, 0, 0.1), rgba(0, 0, 0, 0.3));
                border: 1px solid rgba(0, 255, 0, 0.3);
                border-radius: 8px;
                color: #00ff00;
                text-decoration: none;
                font-size: 12px;
                font-weight: bold;
                transition: all 0.3s ease;
                backdrop-filter: blur(5px);
            }}
            .github-corner a:hover {{
                background: linear-gradient(135deg, rgba(0, 255, 0, 0.2), rgba(0, 0, 0, 0.4));
                border-color: #00ff00;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 255, 0, 0.4);
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
                margin-bottom: 20px; 
                animation: slideIn 0.5s ease-out;
            }}
            @keyframes slideIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .game-header {{
                text-align: center;
                margin-bottom: 20px;
                padding: 15px;
                background: linear-gradient(135deg, rgba(0, 255, 0, 0.1), rgba(0, 0, 0, 0.3));
                border-radius: 10px;
                border: 1px solid rgba(0, 255, 0, 0.3);
            }}
            .game-header h2 {{
                margin: 0 0 5px 0;
                font-size: 20px;
                color: #00ff00;
            }}
            .game-header p {{
                margin: 0;
                font-size: 12px;
                color: #aaa;
            }}

            .github-icon {{
                width: 20px;
                height: 20px;
                color: #00ff00;
                transition: all 0.3s ease;
            }}
            .github-corner a:hover .github-icon {{
                color: #fff;
                transform: scale(1.1);
            }}
            .link-text {{
                font-size: 11px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-bottom: 15px;
            }}
            .metric-card {{
                background: rgba(0, 255, 0, 0.05);
                border: 1px solid rgba(0, 255, 0, 0.2);
                border-radius: 6px;
                padding: 8px;
                text-align: center;
            }}
            .metric-title {{
                font-size: 11px;
                color: #00ff00;
                font-weight: bold;
                margin-bottom: 6px;
            }}
            .metric-value {{
                font-size: 14px;
                font-weight: bold;
                color: #fff;
                margin-bottom: 4px;
            }}
            .metric-desc {{
                font-size: 9px;
                color: #888;
            }}
            .metrics-breakdown {{
                margin-top: 10px;
            }}
            .metrics-breakdown h4 {{
                font-size: 12px;
                color: #00ff00;
                margin: 0 0 10px 0;
                font-weight: bold;
            }}
            .llm-costs {{
                display: flex;
                flex-direction: column;
                gap: 6px;
            }}
            .llm-cost-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 6px 8px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
                font-size: 10px;
            }}
            .llm-name {{
                color: #ccc;
            }}
            .llm-cost {{
                color: #00ff00;
                font-weight: bold;
            }}
            
            .agent-response-times {{
                display: flex;
                flex-direction: column;
                gap: 6px;
            }}
            
            .response-time-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 6px 8px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
                font-size: 10px;
            }}
            
            .agent-name {{
                color: #ccc;
            }}
            
            .response-time {{
                color: #00ff00;
                font-weight: bold;
            }}
            
            /* Model Selection Styles */
            .model-selection {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            
            .agent-model-card {{
                background: linear-gradient(135deg, #333, #222);
                border: 1px solid #00ff00;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }}
            
            .agent-model-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            
            .agent-model-title {{
                color: #00ff00;
                font-weight: bold;
                font-size: 14px;
            }}
            
            .current-model {{
                color: #ccc;
                font-size: 12px;
                background: rgba(0, 255, 0, 0.1);
                padding: 4px 8px;
                border-radius: 4px;
            }}
            
            .model-selector {{
                display: flex;
                gap: 8px;
                flex-wrap: wrap;
            }}
            
            .model-option {{
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
                cursor: pointer;
                transition: all 0.2s ease;
                color: #ccc;
            }}
            
            .model-option:hover {{
                border-color: #00ff00;
                background: rgba(0, 255, 0, 0.1);
            }}
            
            .model-option.active {{
                border-color: #00ff00;
                background: rgba(0, 255, 0, 0.2);
                color: #00ff00;
            }}
            
            .model-option.unavailable {{
                opacity: 0.5;
                cursor: not-allowed;
                border-color: #666;
            }}
            
            .model-info {{
                font-size: 10px;
                color: #888;
                margin-top: 4px;
            }}
            
            .model-cost {{
                color: #00ff00;
                font-weight: bold;
            }}
            
            .model-switch-btn {{
                background: linear-gradient(45deg, #00ff00, #00cc00);
                color: #000;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            
            .model-switch-btn:hover {{
                background: linear-gradient(45deg, #00cc00, #009900);
                transform: translateY(-1px);
            }}
            
            .model-switch-btn:disabled {{
                background: #666;
                cursor: not-allowed;
                transform: none;
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
            .game-container {{
                display: grid;
                grid-template-columns: 1fr 350px;
                gap: 20px;
                margin: 20px 0;
            }}
            .game-board-section {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .board-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                margin-bottom: 15px;
            }}
            .board-header h2 {{
                margin: 0;
                font-size: 18px;
            }}
            .game-status-mini {{
                display: flex;
                gap: 10px;
            }}
            .status-badge {{
                background: rgba(0, 255, 0, 0.2);
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 11px;
                border: 1px solid rgba(0, 255, 0, 0.3);
            }}
            .status-badge.winner {{
                background: rgba(0, 255, 0, 0.3);
                color: #00ff00;
                font-weight: bold;
            }}
            .game-controls {{
                margin-top: 15px;
                text-align: center;
            }}
            .game-status-bar {{
                display: flex;
                justify-content: center;
                gap: 15px;
                margin-bottom: 10px;
            }}
            .status-item {{
                background: rgba(0, 255, 0, 0.1);
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 11px;
                border: 1px solid rgba(0, 255, 0, 0.3);
                color: #00ff00;
            }}
            .status-item.winner {{
                background: rgba(0, 255, 0, 0.2);
                color: #fff;
                font-weight: bold;
            }}
            .turn-indicator-mini {{
                background: rgba(0, 255, 0, 0.1);
                padding: 8px 12px;
                border-radius: 6px;
                margin-bottom: 10px;
                font-size: 12px;
                border: 1px solid rgba(0, 255, 0, 0.3);
            }}
            .info-section {{
                background: linear-gradient(135deg, #333, #222);
                border-radius: 10px;
                border: 1px solid #00ff00;
                overflow: hidden;
                min-height: 600px;
            }}
            .tab-container {{
                height: 100%;
                display: flex;
                flex-direction: column;
            }}
            .tab-buttons {{
                display: flex;
                background: rgba(0, 0, 0, 0.3);
                border-bottom: 1px solid #00ff00;
            }}
            .tab-btn {{
                flex: 1;
                background: none;
                border: none;
                color: #aaa;
                padding: 12px 8px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .tab-btn:hover {{
                background: rgba(0, 255, 0, 0.1);
                color: #00ff00;
            }}
            .tab-btn.active {{
                background: rgba(0, 255, 0, 0.2);
                color: #00ff00;
                border-bottom: 2px solid #00ff00;
            }}
            .tab-content {{
                flex: 1;
                padding: 20px;
                max-height: 550px;
                overflow-y: auto;
            }}
            .tab-panel {{
                display: none;
            }}
            .tab-panel.active {{
                display: block;
            }}
            .tab-panel h3 {{
                margin: 0 0 15px 0;
                font-size: 16px;
                color: #00ff00;
                font-weight: bold;
            }}
            .moves-list {{
                max-height: 500px;
                overflow-y: auto;
                padding-right: 5px;
                word-wrap: break-word;
                overflow-x: hidden;
            }}
            .move-item {{
                padding: 8px 10px;
                margin: 3px 0;
                border-radius: 4px;
                font-size: 12px;
                border-left: 3px solid;
                transition: all 0.3s ease;
                line-height: 1.3;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            .move-item.player-move {{
                background: rgba(0, 255, 0, 0.1);
                border-left-color: #00ff00;
                color: #00ff00;
            }}
            .move-item.ai-move {{
                background: rgba(255, 68, 68, 0.1);
                border-left-color: #ff4444;
                color: #ff4444;
            }}
            .move-item:hover {{
                transform: translateX(2px);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }}
            .move-item:last-child {{
                border-bottom: none;
            }}
            .move-item.no-moves {{
                background: rgba(255, 255, 255, 0.1);
                border-left-color: #888;
                color: #888;
                text-align: center;
                font-style: italic;
                font-size: 13px;
                padding: 12px 15px;
                margin: 8px 0;
            }}
            .board-controls {{
                text-align: center;
                margin: 20px 0;
            }}
            .turn-indicator {{
                margin-bottom: 15px;
                padding: 10px;
                background: rgba(0, 255, 0, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(0, 255, 0, 0.3);
            }}
            .turn-indicator p {{
                margin: 5px 0;
                font-size: 14px;
                color: #00ff00;
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
        <div class="github-corner">
            <a href="https://github.com/arungupta/mcp-multiplayer-game" target="_blank" title="View on GitHub">
                <svg class="github-icon" viewBox="0 0 24 24" width="20" height="20">
                    <path fill="currentColor" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                <span class="link-text">GitHub</span>
            </a>
        </div>
        
        <div class="container">
            <div class="header">
                <h1>🎮 <span class="emoji">⭕</span> Tic Tac Toe <span class="emoji">❌</span> Multi-Agent Battle <span class="emoji">🎯</span></h1>
                <p>Watch three AI agents work together using MCP protocol!</p>
            </div>
            
            <div class="game-section">
                <div class="game-header">
                    <h2>🎮 Tic Tac Toe Multi-Agent Game</h2>
                    <p>Experience MCP protocol with three different AI agents</p>
                </div>
            </div>
            
            <div class="game-container">
                <!-- Game Board Section -->
                <div class="game-board-section">
                    <div class="board-header">
                        <h2>🎮 Tic Tac Toe</h2>
                    </div>
                    
                    <div class="board-container">
                        <div class="tic-tac-toe-board">
                            {chr(10).join([f'<div class="board-row">' + chr(10).join([f'<div class="board-cell" data-row="{row}" data-col="{col}" onclick="makeMove({row}, {col})">{current_state.get("board", [["", "", ""], ["", "", ""], ["", "", ""]])[row][col]}</div>' for col in range(3)]) + '</div>' for row in range(3)])}
                        </div>
                    </div>
                    
                    <div class="game-controls">
                        <div class="game-status-bar">
                            <span class="status-item">Move: {current_state.get('move_number', 0)}</span>
                            <span class="status-item">Turn: {current_state.get('current_player', 'player').upper()}</span>
                            {f'<span class="status-item winner">Winner: {current_state.get("winner", "").upper()}</span>' if current_state.get('game_over', False) and current_state.get('winner') else ''}
                        </div>
                        <div class="turn-indicator-mini">
                            {f'<span class="emoji">🎉</span> Game Over! {current_state.get("winner", "").upper()} wins!' if current_state.get('game_over', False) and current_state.get('winner') else f'<span class="emoji">🤝</span> Game Over! It is a draw!' if current_state.get('game_over', False) else f'<span class="emoji">{"👤" if current_state.get("current_player", "player") == "player" else "🤖"}</span> {"Your turn! Click any cell" if current_state.get("current_player", "player") == "player" else "AI is thinking..."}'}
                        </div>
                        <button class="btn" onclick="resetGame()">
                            <span class="emoji">🔄</span> NEW GAME
                        </button>
                    </div>
                </div>
                
                <!-- Tabbed Info Section -->
                <div class="info-section">
                    <div class="tab-container">
                        <div class="tab-buttons">
                            <button class="tab-btn active" onclick="showTab('moves')">
                                <span class="emoji">📜</span> Moves
                            </button>
                            <button class="tab-btn" onclick="showTab('agents')">
                                <span class="emoji">🤖</span> Agents
                            </button>
                            <button class="tab-btn" onclick="showTab('logs')">
                                <span class="emoji">📡</span> MCP Logs
                            </button>
                            <button class="tab-btn" onclick="showTab('metrics')">
                                <span class="emoji">📊</span> Metrics
                            </button>
                            <button class="tab-btn" onclick="showTab('models')">
                                <span class="emoji">🤖</span> Models
                            </button>
                        </div>
                        
                        <div class="tab-content">
                            <div id="moves-tab" class="tab-panel active">
                                <h3>All Moves</h3>
                                <div class="moves-list">
                                    {chr(10).join([f'<div class="move-item {"player-move" if move.get("player") == "player" else "ai-move"}">Move {move.get("move_number", "N/A")}: <span class="emoji">{"👤" if move.get("player") == "player" else "🤖"}</span> <strong>{move.get("position", {}).get("value", "?")}</strong> at ({move.get("position", {}).get("row", "?")},{move.get("position", {}).get("col", "?")})</div>' for move in current_state.get('game_history', [])]) if current_state.get('game_history', []) else '<div class="move-item no-moves"><span class="emoji">🎮</span> No moves yet. Start the game by clicking any cell!</div>'}
                                </div>
                            </div>
                            
                            <div id="agents-tab" class="tab-panel">
                                <h3>AI Agents</h3>
                                <div id="agents-content">
                                    <p style="color: #888; font-size: 12px; text-align: center; padding: 15px;">Loading agent information...</p>
                                </div>
                            </div>
                            
                            <div id="logs-tab" class="tab-panel">
                                <h3>MCP Protocol Logs</h3>
                                <div id="mcp-logs-content">
                                    <p style="color: #888; font-size: 12px; text-align: center; padding: 15px;">Loading MCP logs...</p>
                                </div>
                            </div>
                            
                            <div id="metrics-tab" class="tab-panel">
                                <h3>Game Metrics Dashboard</h3>
                                <div id="metrics-content">
                                    <div class="metrics-grid">
                                        <div class="metric-card">
                                            <div class="metric-title">📡 MCP Messages</div>
                                            <div class="metric-value" id="mcp-count">0</div>
                                            <div class="metric-desc">Total exchanges</div>
                                        </div>
                                        <div class="metric-card">
                                            <div class="metric-title">💰 Total Cost</div>
                                            <div class="metric-value" id="total-cost">$0.000000</div>
                                            <div class="metric-desc">Across all LLMs</div>
                                        </div>
                                        <div class="metric-card">
                                            <div class="metric-title">🎮 Game Duration</div>
                                            <div class="metric-value" id="game-duration">0s</div>
                                            <div class="metric-desc">Time played</div>
                                        </div>
                                        <div class="metric-card">
                                            <div class="metric-title">⚡ Avg Response Time</div>
                                            <div class="metric-value" id="avg-response">0ms</div>
                                            <div class="metric-desc">Per agent</div>
                                        </div>
                                    </div>
                                    <div class="metrics-breakdown">
                                        <h4>LLM Cost Breakdown</h4>
                                        <div class="llm-costs">
                                            <div class="llm-cost-item">
                                                <span class="llm-name">🤖 GPT-4 (Scout)</span>
                                                <span class="llm-cost" id="gpt4-cost">$0.000000</span>
                                            </div>
                                            <div class="llm-cost-item">
                                                <span class="llm-name">🧠 Claude (Strategist)</span>
                                                <span class="llm-cost" id="claude-cost">$0.000000</span>
                                            </div>
                                            <div class="llm-cost-item">
                                                <span class="llm-name">⚡ Llama2 (Executor)</span>
                                                <span class="llm-cost" id="llama-cost">$0.000000</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="metrics-breakdown">
                                        <h4>Agent Response Times</h4>
                                        <div class="agent-response-times">
                                            <div class="response-time-item">
                                                <span class="agent-name">🔍 Scout (GPT-4)</span>
                                                <span class="response-time" id="scout-response">0ms</span>
                                            </div>
                                            <div class="response-time-item">
                                                <span class="agent-name">🧠 Strategist (Claude)</span>
                                                <span class="response-time" id="strategist-response">0ms</span>
                                            </div>
                                            <div class="response-time-item">
                                                <span class="agent-name">⚡ Executor (Llama2)</span>
                                                <span class="response-time" id="executor-response">0ms</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div id="models-tab" class="tab-panel">
                                <h3>Hot-Swappable LLM Models</h3>
                                <div id="models-content">
                                    <p style="color: #888; font-size: 12px; text-align: center; padding: 15px;">Loading available models...</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function makeMove(row, col) {{
                const cell = document.querySelector('[data-row="' + row + '"][data-col="' + col + '"]');
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
                        // Update the board immediately with player's move
                        cell.textContent = 'X';
                        cell.style.color = '#00ff00';
                        
                        // Show player move notification
                        showNotification('✅ Your move made! AI is thinking...', 'success');
                        
                        // Update game status to show AI's turn
                        updateTurnIndicator('ai');
                        
                        // Update moves list immediately to show player's move
                        setTimeout(() => {{
                            loadMoves();
                        }}, 100);
                        
                        // Wait a moment, then trigger AI move
                        setTimeout(async () => {{
                            try {{
                                const aiResponse = await fetch('/simulate-turn', {{ method: 'POST' }});
                                if (aiResponse.ok) {{
                                    const aiResult = await aiResponse.json();
                                    
                                    // Update board with AI's move
                                    if (aiResult.execution_result && aiResult.execution_result.move_executed) {{
                                        const aiMove = aiResult.execution_result.move_executed.position;
                                        const aiCell = document.querySelector('[data-row="' + aiMove.row + '"][data-col="' + aiMove.col + '"]');
                                        if (aiCell) {{
                                            aiCell.textContent = 'O';
                                            aiCell.style.color = '#ff4444';
                                        }}
                                    }}
                                    
                                    // Update turn indicator
                                    updateTurnIndicator('player');
                                    
                                    // Show AI move notification
                                    showNotification('🤖 AI has made its move!', 'success');
                                    
                                    // Update moves list immediately to show AI's move
                                    setTimeout(() => {{
                                        loadMoves();
                                    }}, 100);
                                    
                                    // Refresh other data
                                    setTimeout(() => {{
                                        refreshGameData();
                                    }}, 500);
                                    
                                }} else {{
                                    showNotification('❌ AI move failed!', 'error');
                                    location.reload();
                                }}
                            }} catch (error) {{
                                showNotification('❌ AI move error: ' + error.message, 'error');
                                location.reload();
                            }}
                        }}, 1500);
                        
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
            
            function updateTurnIndicator(player) {{
                const turnIndicator = document.querySelector('.turn-indicator-mini');
                if (turnIndicator) {{
                    if (player === 'ai') {{
                        turnIndicator.innerHTML = '<span class="emoji">🤖</span> AI is thinking...';
                    }} else {{
                        turnIndicator.innerHTML = '<span class="emoji">👤</span> Your turn! Click any cell';
                    }}
                }}
            }}
            
            async function refreshGameData() {{
                try {{
                    // Refresh agents info
                    if (document.getElementById('agents-tab').classList.contains('active')) {{
                        await loadAgents();
                    }}
                    
                    // Refresh MCP logs
                    if (document.getElementById('logs-tab').classList.contains('active')) {{
                        await loadMCPLogs();
                    }}
                    
                    // Refresh metrics
                    if (document.getElementById('metrics-tab').classList.contains('active')) {{
                        await loadMetrics();
                    }}
                }} catch (error) {{
                    console.error('Error refreshing game data:', error);
                }}
            }}
            

            

            
            function showNotification(message, type) {{
                // Create notification element
                const notification = document.createElement('div');
                const background = type === 'success' ? 'linear-gradient(45deg, #00ff00, #00cc00)' : 'linear-gradient(45deg, #ff4444, #cc0000)';
                notification.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 15px 20px; border-radius: 10px; color: white; font-weight: bold; z-index: 1000; animation: slideInRight 0.5s ease-out; background: ' + background + '; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);';
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
            style.textContent = '@keyframes slideInRight {{ from {{ transform: translateX(100%); opacity: 0; }} to {{ transform: translateX(0); opacity: 1; }} }} @keyframes slideOutRight {{ from {{ transform: translateX(0); opacity: 1; }} to {{ transform: translateX(100%); opacity: 0; }} }}';
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
                loadMoves();
                loadAgents();
                loadMCPLogs();
            }});
            
            async function loadMoves() {{
                try {{
                    const response = await fetch('/state');
                    const data = await response.json();
                    const movesList = document.querySelector('.moves-list');
                    
                    if (data.game_history && data.game_history.length > 0) {{
                        let html = '';
                        data.game_history.forEach(move => {{
                            const playerClass = move.player === 'player' ? 'player-move' : 'ai-move';
                            const emoji = move.player === 'player' ? '👤' : '🤖';
                            const position = move.position;
                            
                            const moveDiv = '<div class="move-item ' + playerClass + '">Move ' + move.move_number + ': <span class="emoji">' + emoji + '</span> <strong>' + position.value + '</strong> at (' + position.row + ',' + position.col + ')</div>';
                            html += moveDiv;
                        }});
                        
                        movesList.innerHTML = html;
                    }} else {{
                        movesList.innerHTML = '<div class="move-item no-moves"><span class="emoji">🎮</span> No moves yet. Start the game by clicking any cell!</div>';
                    }}
                }} catch (error) {{
                    console.error('Error loading moves:', error);
                }}
            }}
            
            async function loadAgents() {{
                try {{
                    const response = await fetch('/agents');
                    const data = await response.json();
                    const agentsContent = document.getElementById('agents-content');
                    
                    let html = '';
                    for (const [agentName, agentInfo] of Object.entries(data.agents)) {{
                        const agentDiv = '<div style="margin-bottom: 8px; padding: 6px; background: rgba(0, 255, 0, 0.1); border-radius: 4px; border-left: 2px solid #00ff00;">';
                        const nameDiv = '<div style="font-weight: bold; color: #00ff00; font-size: 10px;">' + (agentInfo.name || agentName.toUpperCase()) + '</div>';
                        const roleDiv = '<div style="font-size: 9px; margin: 2px 0;"><strong>Role:</strong> ' + (agentInfo.role || 'N/A') + '</div>';
                        const modelDiv = '<div style="font-size: 9px; margin: 2px 0;"><strong>Model:</strong> ' + (agentInfo.model || 'N/A') + '</div>';
                        const agentEnd = '</div>';
                        html += agentDiv + nameDiv + roleDiv + modelDiv + agentEnd;
                    }}
                    
                    agentsContent.innerHTML = html;
                }} catch (error) {{
                    document.getElementById('agents-content').innerHTML = '<p style="color: #ff4444; font-size: 12px; text-align: center; padding: 15px;">Error loading agent information</p>';
                }}
            }}
            
            function showTab(tabName) {{
                // Hide all tab panels
                const tabPanels = document.querySelectorAll('.tab-panel');
                tabPanels.forEach(panel => panel.classList.remove('active'));
                
                // Remove active class from all tab buttons
                const tabButtons = document.querySelectorAll('.tab-btn');
                tabButtons.forEach(btn => btn.classList.remove('active'));
                
                // Show selected tab panel
                document.getElementById(tabName + '-tab').classList.add('active');
                
                // Add active class to clicked button
                event.target.classList.add('active');
                
                // Load content based on tab
                if (tabName === 'agents') {{
                    loadAgents();
                }} else if (tabName === 'logs') {{
                    loadMCPLogs();
                }} else if (tabName === 'metrics') {{
                    loadMetrics();
                }} else if (tabName === 'models') {{
                    loadModels();
                }}
            }}
            
            async function loadMCPLogs() {{
                try {{
                    const response = await fetch('/mcp-logs');
                    const data = await response.json();
                    const logsContent = document.getElementById('mcp-logs-content');
                    
                    if (data.mcp_logs && data.mcp_logs.length > 0) {{
                        let html = '';
                        const recentLogs = data.mcp_logs.slice(-8); // Show last 8 logs
                        
                        recentLogs.forEach(log => {{
                            const timestamp = new Date(log.timestamp).toLocaleTimeString();
                            const agentEmoji = {{
                                'Scout': '🔍',
                                'Strategist': '🧠', 
                                'Executor': '⚡',
                                'GameEngine': '🎮'
                            }}[log.agent] || '🤖';
                            
                            // Format JSON data for display
                            const jsonData = JSON.stringify(log.data, null, 2);
                            const shortData = jsonData.length > 200 ? jsonData.substring(0, 200) + '...' : jsonData;
                            
                            const logDiv = '<div style="margin-bottom: 8px; padding: 8px; background: rgba(0, 255, 0, 0.05); border-radius: 4px; border-left: 3px solid #00ff00; font-size: 11px;">';
                            const headerDiv = '<div style="display: flex; justify-content: space-between; margin-bottom: 4px;">';
                            const agentSpan = '<span style="color: #00ff00; font-weight: bold;">' + agentEmoji + ' ' + log.agent + '</span>';
                            const timeSpan = '<span style="color: #888;">' + timestamp + '</span>';
                            const messageDiv = '<div style="color: #00ff00; font-size: 10px; margin-bottom: 4px; font-weight: bold;">' + log.message_type + '</div>';
                            const detailsDiv = '<details style="margin-top: 4px;">';
                            const summaryDiv = '<summary style="color: #888; font-size: 9px; cursor: pointer;">📄 View JSON Data</summary>';
                            const preStyle = 'background: rgba(0, 0, 0, 0.3); padding: 6px; border-radius: 3px; font-size: 8px; color: #ccc; margin: 4px 0; max-height: 200px; overflow-y: auto; overflow-x: auto; white-space: pre-wrap;';
                            const preDiv = '<pre style="' + preStyle + '">' + jsonData + '</pre>';
                            
                            const headerEnd = '</div>';
                            const detailsEnd = '</details></div>';
                            const logHtml = logDiv + headerDiv + agentSpan + timeSpan + headerEnd + messageDiv + detailsDiv + summaryDiv + preDiv + detailsEnd;
                            html += logHtml;
                        }});
                        
                        logsContent.innerHTML = html;
                    }} else {{
                        logsContent.innerHTML = '<p style="color: #888; font-size: 12px; text-align: center; padding: 15px;">No MCP logs yet. Play to see protocol in action!</p>';
                    }}
                }} catch (error) {{
                    document.getElementById('mcp-logs-content').innerHTML = '<p style="color: #ff4444; font-size: 12px; text-align: center; padding: 15px;">Error loading MCP logs</p>';
                }}
            }}
            
            async function loadMetrics() {{
                try {{
                    const response = await fetch('/metrics');
                    const data = await response.json();
                    
                    // Update metric values
                    document.getElementById('mcp-count').textContent = data.mcp_message_count || 0;
                    document.getElementById('total-cost').textContent = '$' + parseFloat(data.total_cost || 0).toFixed(6);
                    document.getElementById('game-duration').textContent = Math.round(data.game_duration_seconds || 0) + 's';
                    
                    // Calculate average response time
                    const responseTimes = data.avg_response_times || {{}};
                    const avgResponse = Object.values(responseTimes).reduce((sum, time) => sum + time, 0) / Math.max(Object.keys(responseTimes).length, 1);
                    document.getElementById('avg-response').textContent = avgResponse < 1 ? avgResponse.toFixed(2) + 'ms' : Math.round(avgResponse) + 'ms';
                    
                    // Update LLM costs
                    const costs = data.llm_costs || {{}};
                    document.getElementById('gpt4-cost').textContent = '$' + parseFloat(costs.gpt4 || 0).toFixed(6);
                    document.getElementById('claude-cost').textContent = '$' + parseFloat(costs.claude || 0).toFixed(6);
                    document.getElementById('llama-cost').textContent = '$' + parseFloat(costs.llama || 0).toFixed(6);
                    
                    // Update individual agent response times
                    const scoutTime = responseTimes.scout || 0;
                    const strategistTime = responseTimes.strategist || 0;
                    const executorTime = responseTimes.executor || 0;
                    
                    document.getElementById('scout-response').textContent = scoutTime < 1 ? scoutTime.toFixed(2) + 'ms' : Math.round(scoutTime) + 'ms';
                    document.getElementById('strategist-response').textContent = strategistTime < 1 ? strategistTime.toFixed(2) + 'ms' : Math.round(strategistTime) + 'ms';
                    document.getElementById('executor-response').textContent = executorTime < 1 ? executorTime.toFixed(2) + 'ms' : Math.round(executorTime) + 'ms';
                    
                }} catch (error) {{
                    console.error('Error loading metrics:', error);
                }}
            }}
            
            async function loadModels() {{
                try {{
                    const response = await fetch('/models');
                    const data = await response.json();
                    const modelsContent = document.getElementById('models-content');
                    
                    const models = data.models || {{}};
                    const currentModels = data.current_models || {{}};
                    
                    let html = '<div class="model-selection">';
                    
                    // Create model selection for each agent
                    const agents = [
                        {{ name: 'scout', display: '🔍 Scout Agent', emoji: '🔍' }},
                        {{ name: 'strategist', display: '🧠 Strategist Agent', emoji: '🧠' }},
                        {{ name: 'executor', display: '⚡ Executor Agent', emoji: '⚡' }}
                    ];
                    
                    agents.forEach(agent => {{
                        const currentModel = currentModels[agent.name] || 'Unknown';
                        const cardStart = '<div class="agent-model-card">';
                        const headerStart = '<div class="agent-model-header">';
                        const titleDiv = '<div class="agent-model-title">' + agent.display + '</div>';
                        const currentDiv = '<div class="current-model">Current: ' + currentModel + '</div>';
                        const headerEnd = '</div>';
                        const selectorStart = '<div class="model-selector">';
                        
                        html += cardStart + headerStart + titleDiv + currentDiv + headerEnd + selectorStart;
                        
                        // Add model options
                        Object.entries(models).forEach(([modelName, modelInfo]) => {{
                            const isActive = currentModel === modelName;
                            const isAvailable = modelInfo.is_available;
                            const cost = modelInfo.estimated_cost_per_1k_tokens;
                            const costDisplay = cost > 0 ? '$' + cost.toFixed(6) : 'Free';
                            
                            const optionClass = (isActive ? 'active' : '') + ' ' + (!isAvailable ? 'unavailable' : '');
                            const onClickHandler = isAvailable ? 'switchModel(\'' + agent.name + '\', \'' + modelName + '\')' : '';
                            const optionStart = '<div class="model-option ' + optionClass + '" onclick="' + onClickHandler + '">';
                            const nameDiv = '<div>' + modelInfo.display_name + '</div>';
                            const infoDiv = '<div class="model-info">' + costDisplay + ' per 1K tokens</div>';
                            const optionEnd = '</div>';
                            html += optionStart + nameDiv + infoDiv + optionEnd;
                        }});
                        
                        const cardEnd = '</div></div>';
                        html += cardEnd;
                    }});
                    
                    html += '</div>';
                    modelsContent.innerHTML = html;
                    
                }} catch (error) {{
                    document.getElementById('models-content').innerHTML = '<p style="color: #ff4444; font-size: 12px; text-align: center; padding: 15px;">Error loading models</p>';
                }}
            }}
            
            async function switchModel(agent, modelName) {{
                try {{
                    const response = await fetch('/switch-model', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ agent: agent, model_name: modelName }})
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        showNotification('✅ ' + result.message, 'success');
                        // Reload models to show updated state
                        setTimeout(() => loadModels(), 500);
                        // Also reload agents to show new model info
                        setTimeout(() => loadAgents(), 500);
                    }} else {{
                        showNotification('❌ ' + result.error, 'error');
                    }}
                }} catch (error) {{
                    showNotification('❌ Error switching model: ' + error.message, 'error');
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

@app.get("/metrics")
async def get_metrics():
    """Get game metrics"""
    try:
        return game_state.get_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


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


@app.get("/models")
async def get_available_models():
    """Get all available models"""
    try:
        return {
            "models": model_registry.get_model_info(),
            "current_models": game_state.get_current_models(),
            "model_usage_history": game_state.get_model_usage_history()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")


@app.post("/switch-model")
async def switch_agent_model(request: dict):
    """Switch the model for a specific agent"""
    try:
        agent = request.get("agent")
        model_name = request.get("model_name")
        
        if not agent or not model_name:
            return {"error": "Agent and model_name are required"}
        
        # Validate model availability
        if not ModelFactory.validate_model_availability(model_name):
            return {"error": f"Model {model_name} is not available"}
        
        success = False
        
        if agent == "scout" and scout_agent:
            success = scout_agent.switch_model(model_name)
        elif agent == "strategist" and strategist_agent:
            success = strategist_agent.switch_model(model_name)
        elif agent == "executor" and executor_agent:
            success = executor_agent.switch_model(model_name)
        else:
            return {"error": f"Unknown agent: {agent}"}
        
        if success:
            return {
                "success": True,
                "message": f"Successfully switched {agent} to {model_name}",
                "current_models": game_state.get_current_models()
            }
        else:
            return {"error": f"Failed to switch {agent} to {model_name}"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching model: {str(e)}")


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