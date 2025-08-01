import streamlit as st
import requests
import time
import json
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="X⚔️O Multi-Agent Battle",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimal CSS for dark theme
st.markdown("""
<style>
    /* Simple dark theme */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Header styling */
    .main-header {
        color: #00ff88;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    .sub-header {
        color: #00ff88;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 5px #00ff88, 0 0 10px #00ff88, 0 0 15px #00ff88; }
        to { text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88; }
    }
    
    /* Game console styling */
    .game-console {
        background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
        border: 2px solid #00ff88;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        position: relative;
    }
    
    .game-console::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #00ff88, #00cc6a, #00ff88);
        border-radius: 17px;
        z-index: -1;
        animation: borderGlow 3s ease-in-out infinite;
    }
    
    @keyframes borderGlow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #2d2d2d;
        border-radius: 6px;
        color: #fafafa;
        font-weight: 500;
        padding: 8px 16px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00ff88;
        color: #0e1117;
        font-weight: bold;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #00ff88;
        text-align: center;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00ff88;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #ccc;
        margin-top: 4px;
    }
    
    /* Status bar styling */
    .status-bar {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 16px 24px;
        border: 1px solid #00ff88;
        text-align: center;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        margin: 20px auto;
        max-width: 400px;
    }
    
    .status-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }
    
    .status-icon {
        font-size: 1.5rem;
        color: #87ceeb;
    }
    
    .status-text {
        font-size: 1.2rem;
        font-weight: bold;
        color: #00ff88;
        font-family: 'Courier New', monospace;
    }
    
    /* Game board styling */
    .game-board {
        width: 320px;
        margin: 30px auto;
        background: transparent;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #00ff88;
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.4);
    }
    
    /* Game board styling with CSS Grid */
    .game-board {
        width: 320px;
        margin: 30px auto;
        background: transparent;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #00ff88;
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.4);
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: repeat(3, 1fr);
        gap: 6px;
        height: 240px;
    }
    
    /* Override Streamlit layout completely */
    .game-board > * {
        grid-column: span 1;
        grid-row: span 1;
    }
    
    /* Style Streamlit buttons as game cells */
    .game-board .stButton {
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
    }
    
    .game-board .stButton > button {
        width: 100%;
        height: 100%;
        background-color: #2d2d2d;
        border: 2px solid #00ff88;
        border-radius: 8px;
        color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        text-transform: none;
        letter-spacing: normal;
        padding: 0;
        margin: 0;
        min-height: 80px;
    }
    
    .game-board .stButton > button:hover {
        background-color: #3a3a3a;
        border-color: #00ff88;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
    }
    
    .game-cell {
        background-color: #2d2d2d;
        border: 2px solid #00ff88;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #00ff88;
        width: 100%;
        height: 100%;
        box-sizing: border-box;
    }
    
    .game-cell:hover {
        background-color: #3a3a3a;
        border-color: #00ff88;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
    }
    
    .game-cell.empty {
        cursor: pointer;
    }
    
    .game-cell.empty:hover {
        background-color: #3a3a3a;
        border-color: #00ff88;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
    }
    
    .game-cell.empty-disabled {
        cursor: not-allowed;
        opacity: 0.7;
    }
    
    .game-cell.player {
        color: #00ff88;
        border-color: #00ff88;
        background-color: #2d2d2d;
    }
    
    .game-cell.ai {
        color: #ff6b6b;
        border-color: #ff6b6b;
        background-color: #2d2d2d;
    }
    
    /* Ensure grid stability */
    .game-board > * {
        box-sizing: border-box;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #00ff88;
        color: #0e1117;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background-color: #00cc6a;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 255, 136, 0.6);
    }
    
    /* Game board button styling */
    .game-board .stButton > button {
        background-color: #2d2d2d;
        color: transparent;
        border: 2px solid #00ff88;
        border-radius: 8px;
        padding: 0;
        font-weight: bold;
        font-size: 2.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        text-transform: none;
        letter-spacing: normal;
        min-height: 80px;
        width: 100%;
        height: 100%;
    }
    
    .game-board .stButton > button:hover {
        background-color: #3a3a3a;
        border-color: #00ff88;
        transform: scale(1.05);
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
    }
    
    .game-board .stButton > button:disabled {
        background-color: #2d2d2d;
        border-color: #444;
        color: transparent;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    /* Status indicators */
    .status-playing {
        color: #00ff88;
        font-weight: bold;
    }
    
    .status-winner {
        color: #ff6b6b;
        font-weight: bold;
    }
    
    .status-draw {
        color: #ffd93d;
        font-weight: bold;
    }
    
    /* Log containers */
    .log-container {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #333;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .log-entry {
        background-color: #2d2d2d;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 4px solid #00ff88;
    }
    
    .log-time {
        color: #888;
        font-size: 0.8rem;
    }
    
    .log-agent {
        color: #00ff88;
        font-weight: bold;
    }
    
    .log-message {
        color: #fafafa;
        margin-top: 4px;
    }
    
    /* Model cards */
    .model-card {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #333;
        margin-bottom: 16px;
    }
    
    .model-header {
        color: #00ff88;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .model-info {
        color: #ccc;
        font-size: 0.9rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .game-board {
            max-width: 250px;
        }
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE = "http://localhost:8000"

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0
if 'game_state' not in st.session_state:
    st.session_state.game_state = None
if 'pending_move' not in st.session_state:
    st.session_state.pending_move = None

def get_game_state():
    """Fetch current game state from API"""
    try:
        response = requests.get(f"{API_BASE}/state")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching game state: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def make_move(row, col):
    """Make a player move"""
    try:
        response = requests.post(f"{API_BASE}/make-move", json={"row": row, "col": col})
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error making move: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error making move: {e}")
        return False

def simulate_ai_turn():
    """Simulate AI turn"""
    try:
        response = requests.post(f"{API_BASE}/simulate-turn")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error simulating AI turn: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error simulating AI turn: {e}")
        return None

def reset_game():
    """Reset the game"""
    try:
        response = requests.post(f"{API_BASE}/reset-game")
        if response.status_code == 200:
            st.success("Game reset successfully!")
            return True
        else:
            st.error(f"Error resetting game: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error resetting game: {e}")
        return False

def get_agents():
    """Get agent information"""
    try:
        response = requests.get(f"{API_BASE}/agents")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching agents: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching agents: {e}")
        return None

def get_mcp_logs():
    """Get MCP logs"""
    try:
        response = requests.get(f"{API_BASE}/mcp-logs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching MCP logs: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching MCP logs: {e}")
        return None

def get_metrics():
    """Get game metrics"""
    try:
        response = requests.get(f"{API_BASE}/metrics")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching metrics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")
        return None

def get_models():
    """Get available models"""
    try:
        response = requests.get(f"{API_BASE}/models")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching models: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return None

def switch_model(agent, model_name):
    """Switch model for an agent"""
    try:
        response = requests.post(f"{API_BASE}/switch-model", json={"agent": agent, "model_name": model_name})
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Main app
def main():
    # Header
    # Header with GitHub link in top right
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎮 Agentic Tic-Tac-Toe: MCP Protocol Showcase")
        st.markdown("🎲 Watch three AI agents work together using CrewAI and MCP protocol! 🚀")
    
    with col2:
        st.markdown("""
        <div style="text-align: right; margin-top: 20px;">
            <a href="https://github.com/arungupta/mcp-multiplayer-game" target="_blank" style="text-decoration: none;">
                <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" 
                     alt="GitHub" 
                     style="width: 32px; height: 32px; vertical-align: middle; margin-right: 8px;">
                <span style="color: #00ff88; font-size: 1.1rem; font-weight: bold;">View on GitHub</span>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start guide
    with st.expander("🚀 **Quick Start Guide**", expanded=False):
        st.markdown("""
        **How to play:**
        1. **🎮 Game Tab**: Click any empty cell on the Tic Tac Toe board to make your move
        2. **🕵️‍♂️ Watch Double-O-AI**: The three agents (Scout, Strategist, Executor) will communicate and respond
        3. **📡 MCP Logs**: See real-time communication between agents in the MCP Logs tab
        4. **📊 Metrics**: Monitor performance and costs in the Metrics tab
        5. **🔄 Models**: Switch between different LLM providers in the Models tab
        
        **What you'll see:**
        - **Scout Agent** (Available Model): Analyzes the board state
        - **Strategist Agent** (Available Model): Creates strategic plans
        - **Executor Agent** (Available Model): Makes the actual moves
        
        **Status Meanings:**
        - **🎯 Active**: Game is currently being played
        - **Current Turn**: Shows whose turn it is (You or Double-O-AI)
        - **Turn Status**: Whether it's your turn or AI's turn
        
        Start by making a move in the Game tab!
        """)
    
    # Check if API is running
    try:
        health_response = requests.get(f"{API_BASE}/health")
        if health_response.status_code != 200:
            st.error("⚠️ **API Server Not Running**\n\nPlease start the API server by running:\n```bash\npython main.py\n```\n\nThen refresh this page.")
            st.stop()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ **Cannot Connect to API Server**\n\nPlease make sure the API server is running:\n```bash\npython main.py\n```\n\nThen refresh this page.")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ **Connection Error**\n\nUnexpected error connecting to API server: {str(e)}\n\nPlease check if the server is running and try again.")
        st.stop()
    
    # Auto-refresh every 5 seconds
    if time.time() - st.session_state.last_refresh > 5:
        st.session_state.game_state = get_game_state()
        st.session_state.last_refresh = time.time()
    
    # Get current game state
    game_state = st.session_state.game_state or get_game_state()
    if game_state is None:
        st.error("❌ **Game State Unavailable**\n\nUnable to load the current game state. Please refresh the page or restart the API server.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎮 Game", "🤖 Agents & Models", "📡 MCP Logs", "📊 Metrics"])
    
    with tab1:
        # AI Team Status Overview
        try:
            ai_team_status = requests.get(f"{API_BASE}/ai-team-status").json()
            
            if ai_team_status.get("team_ready", False):
                st.success("🎯 **AI Team Status: READY** - All agents have working models!")
            else:
                st.error("🚫 **AI Team Status: NOT READY** - Some agents need configuration")
                
                # Show detailed status
                for agent, status in ai_team_status.get("agents", {}).items():
                    agent_name = agent.title()
                    if status.get("status") == "ready":
                        st.success(f"✅ **{agent_name}**: {status.get('model_name', 'Unknown')}")
                    else:
                        st.error(f"❌ **{agent_name}**: {status.get('status', 'Unknown')}")
        except Exception as e:
            st.warning(f"⚠️ **Unable to check AI team status** - Error: {str(e)}")
        
        # Game board and move history side by side
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Game board
            board = game_state.get('board', [['' for _ in range(3)] for _ in range(3)])
            current_player = game_state.get('current_player', 'player')
            
            for i in range(3):
                cols = st.columns(3)
                for j in range(3):
                    with cols[j]:
                        cell_value = board[i][j]
                        if cell_value == '':
                            # Empty cell - make it clickable
                            if not game_state.get('game_over', False) and current_player == 'player':
                                if st.button("+", key=f"cell_{i}_{j}", 
                                           use_container_width=True,
                                           help=f"Click to place your move at ({i}, {j})",
                                           type="secondary"):
                                    st.session_state.pending_move = (i, j)
                                    st.rerun()
                            else:
                                # Disabled cell
                                st.button("·", key=f"cell_{i}_{j}_disabled", 
                                        disabled=True, use_container_width=True,
                                        type="secondary")
                        else:
                            # Filled cell with custom colors using inline styles
                            if cell_value == 'X':
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(145deg, #1a2a1a, #0a1a0a);
                                    border: 2px solid #00ff88;
                                    border-radius: 8px;
                                    padding: 8px 4px;
                                    text-align: center;
                                    font-size: 1.2rem;
                                    font-weight: bold;
                                    margin: 2px;
                                    color: #00ff88;
                                    box-shadow: 0 0 8px rgba(0, 255, 136, 0.3);
                                    text-shadow: 0 0 4px rgba(0, 255, 136, 0.4);
                                    min-height: 40px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                ">
                                    ❌
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(145deg, #2a1a1a, #1a0a0a);
                                    border: 2px solid #ff6b6b;
                                    border-radius: 8px;
                                    padding: 8px 4px;
                                    text-align: center;
                                    font-size: 1.2rem;
                                    font-weight: bold;
                                    margin: 2px;
                                    color: #ff6b6b;
                                    box-shadow: 0 0 8px rgba(255, 107, 107, 0.3);
                                    text-shadow: 0 0 4px rgba(255, 107, 107, 0.4);
                                    min-height: 40px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                ">
                                    ⭕
                                </div>
                                """, unsafe_allow_html=True)
            
            # Game controls
            if st.button("🔄 New Game", use_container_width=True):
                if reset_game():
                    # Clear session state and refresh game state
                    st.session_state.game_state = None
                    st.session_state.pending_move = None
                    st.session_state.last_refresh = 0
                    st.rerun()
        
        with col2:
            # Move history
            st.subheader("📜 Move History")
            moves = game_state.get('game_history', [])
            if moves:
                for i, move in enumerate(moves[-8:], 1):  # Show last 8 moves
                    player = "👤 You" if move['player'] == 'player' else "🕵️‍♂️ Double-O-AI"
                    position = move['position']
                    row, col = position['row'], position['col']
                    value = position['value']
                    st.markdown(f"**{move['move_number']}.** {player} placed {value} at ({row}, {col})")
            else:
                st.markdown("*No moves yet. Start the game by clicking any cell!*")
        
        # Show game result below the game board
        if game_state.get('game_over'):
            winner = game_state.get('winner')
            if winner == 'player':
                st.markdown("""
                <div style="background: linear-gradient(135deg, #4CAF50, #45a049); border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; margin: 15px 0; text-align: center; box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);">
                    <h2 style="color: white; margin: 0; font-size: 2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🎉 You Won! 🎉</h2>
                    <p style="color: #e8f5e8; margin: 10px 0 0 0; font-size: 1.1em;">Congratulations! You've defeated the AI!</p>
                </div>
                """, unsafe_allow_html=True)
            elif winner == 'ai':
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f44336, #d32f2f); border: 2px solid #f44336; border-radius: 10px; padding: 20px; margin: 15px 0; text-align: center; box-shadow: 0 4px 8px rgba(244, 67, 54, 0.3);">
                    <h2 style="color: white; margin: 0; font-size: 2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🤖 AI Won! 🤖</h2>
                    <p style="color: #ffebee; margin: 10px 0 0 0; font-size: 1.1em;">The AI has outsmarted you this time!</p>
                </div>
                """, unsafe_allow_html=True)
            elif winner == 'draw':
                st.markdown("""
                <div style="background: linear-gradient(135deg, #ff9800, #f57c00); border: 2px solid #ff9800; border-radius: 10px; padding: 20px; margin: 15px 0; text-align: center; box-shadow: 0 4px 8px rgba(255, 152, 0, 0.3);">
                    <h2 style="color: white; margin: 0; font-size: 2em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🤝 It's a Draw! 🤝</h2>
                    <p style="color: #fff3e0; margin: 10px 0 0 0; font-size: 1.1em;">A well-fought battle with no clear winner!</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Handle pending move (outside columns to avoid layout issues)
        if hasattr(st.session_state, 'pending_move') and st.session_state.pending_move is not None:
            row, col = st.session_state.pending_move
            st.session_state.pending_move = None  # Reset to None instead of deleting
            
            # Make the move
            if make_move(row, col):
                st.success(f"✅ Move made at ({row}, {col})! Double-O-AI is thinking...")
                # Simulate AI turn
                ai_result = simulate_ai_turn()
                if ai_result:
                    st.success("🕵️‍♂️ Double-O-AI has made its move!")
                # Force refresh game state
                st.session_state.game_state = get_game_state()
                st.session_state.last_refresh = 0  # Force immediate refresh
                st.rerun()
    
    with tab2:
        st.header("🤖 AI Agents & Models")
        
        # Tabbed Agents & Models Interface
        st.subheader("🤖 Agents & Models")
        
        # Get data
        agents_data = get_agents()
        models_data = get_models()
        
        if agents_data and 'agents' in agents_data and models_data and 'models' in models_data:
            current_models = models_data.get('current_models', {})
            available_models = models_data['models']
            
            # Create tabs for each agent plus models reference and model history tabs
            agent_tabs = st.tabs([f"🤖 {agent['name']}" for agent in agents_data['agents'].values()] + ["📋 Models Reference", "🔄 Model History"])
            
            # Agent tabs
            for i, (agent_name, agent) in enumerate(agents_data['agents'].items()):
                with agent_tabs[i]:
                    current_model = current_models.get(agent_name, 'Unknown')
                    
                    # Agent header with current model
                    st.markdown(f"### {agent['name']} - {agent['role']}")
                    
                    # Check if current model is actually available
                    current_model_available = False
                    if current_model in available_models:
                        current_model_available = available_models[current_model].get('is_available', False)
                    
                    # Current model display with availability status
                    if current_model_available:
                        status_icon = "✅"
                        status_color = "#4CAF50"
                        status_bg = "rgba(76, 175, 80, 0.1)"
                        status_text = "Available"
                    else:
                        status_icon = "⚠️"
                        status_color = "#FF9800"
                        status_bg = "rgba(255, 152, 0, 0.1)"
                        status_text = "Not Available"
                    
                    st.markdown(f"""
                    <div style="background: {status_bg}; border: 1px solid {status_color}; border-radius: 8px; padding: 12px; margin: 8px 0;">
                        <strong>🔄 Currently using:</strong> <span style="color: {status_color}; font-weight: bold;">{current_model}</span> {agent['provider_icon']}
                        <br><small>{status_icon} <strong>Status:</strong> {status_text}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Warning if current model is not available
                    if not current_model_available:
                        st.warning(f"⚠️ **Warning:** The Executor agent is configured to use '{current_model}' but this model is not available. The agent may not be working properly.")
                    
                    # Agent information with better formatting
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("### 📋 Agent Details")
                        
                        # Provider info
                        st.markdown(f"""
                        <div style="background: rgba(33, 150, 243, 0.1); border: 1px solid #2196F3; border-radius: 6px; padding: 10px; margin: 8px 0;">
                            <strong>🏢 Provider:</strong> {agent['provider_type']} {agent['provider_icon']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Description
                        st.markdown(f"""
                        <div style="background: rgba(255, 193, 7, 0.1); border: 1px solid #FFC107; border-radius: 6px; padding: 10px; margin: 8px 0;">
                            <strong>📝 Description:</strong><br>
                            {agent['description']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Capabilities
                        st.markdown("**⚡ Capabilities:**")
                        capabilities_text = ""
                        for capability in agent['capabilities']:
                            capabilities_text += f"• {capability}<br>"
                        
                        st.markdown(f"""
                        <div style="background: rgba(156, 39, 176, 0.1); border: 1px solid #9C27B0; border-radius: 6px; padding: 10px; margin: 8px 0;">
                            {capabilities_text}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Model switching for this agent
                        st.markdown("### 🔄 Model Switching")
                        
                        # Get available models for this agent (including current model)
                        available_model_names = [name for name, info in available_models.items() if info.get('is_available', False)]
                        
                        if available_model_names:
                            st.markdown("**Select Model:**")
                            
                            # Use session state to track the previous selection
                            prev_model_key = f"prev_model_{agent_name}"
                            if prev_model_key not in st.session_state:
                                st.session_state[prev_model_key] = current_model
                            
                            # Show current model as default, with all available models as options
                            new_model = st.selectbox(
                                f"Available Models:",
                                available_model_names,
                                index=available_model_names.index(current_model) if current_model in available_model_names else 0,
                                key=f"switch_{agent_name}",
                                help=f"Select a model to switch to (changes apply immediately)"
                            )
                            
                            # Auto-switch when a different model is selected
                            if new_model != st.session_state[prev_model_key]:
                                st.session_state[prev_model_key] = new_model
                                if new_model != current_model:
                                    result = switch_model(agent_name, new_model)
                                    if result and result.get('success'):
                                        st.success(f"✅ Switched to {new_model}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed to switch: {result.get('error', 'Unknown error')}")
                                else:
                                    st.session_state[prev_model_key] = current_model
                            else:
                                st.markdown(f"""
                                <div style="background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; border-radius: 6px; padding: 10px; margin: 8px 0;">
                                    <strong>✅ Currently using:</strong> <span style="color: #4CAF50; font-weight: bold;">{current_model}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="background: rgba(244, 67, 54, 0.1); border: 1px solid #F44336; border-radius: 6px; padding: 10px; margin: 8px 0;">
                                <strong>❌ No models available</strong>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Models Reference tab with nested tabs
            with agent_tabs[-2]:
                st.markdown("### 📋 Available Models Reference")
                
                # Dynamic provider icons legend based on all models (not just available ones)
                all_providers = set()
                for model_info in available_models.values():
                    provider = model_info.get('provider', 'Unknown')
                    all_providers.add(provider)
                
                # Create dynamic legend
                provider_icons = {"openai": "🤖", "anthropic": "🧠", "ollama": "🦙"}
                legend_parts = []
                for provider in sorted(all_providers):
                    icon = provider_icons.get(provider, "❓")
                    provider_name = provider.title()
                    legend_parts.append(f"{icon} {provider_name}")
                
                if legend_parts:
                    st.markdown(f"**Provider Icons:** {' | '.join(legend_parts)}")
                else:
                    st.markdown("**Provider Icons:** No models available")
                
                st.markdown("---")
                
                # Sort all models alphabetically (including unavailable ones)
                sorted_models = sorted(
                    [(model_name, model_info) for model_name, model_info in available_models.items()],
                    key=lambda x: x[0].lower()  # Case-insensitive sorting
                )
                
                # Group models by provider for better organization
                cloud_models = []
                local_models = []
                
                for model_name, model_info in sorted_models:
                    provider = model_info.get('provider', 'Unknown')
                    provider_icon = {"openai": "🤖", "anthropic": "🧠", "ollama": "🦙"}.get(provider, "❓")
                    
                    # Determine if it's cloud or local
                    model_type = "☁️ Cloud" if provider in ["openai", "anthropic"] else "🖥️ Local"
                    
                    if model_type == "☁️ Cloud":
                        cloud_models.append((model_name, provider_icon, provider))
                    else:
                        local_models.append((model_name, provider_icon, provider))
                
                # Sort local models alphabetically by model name
                local_models.sort(key=lambda x: x[0].lower())
                
                # Create nested tabs for Cloud and Local models (Summary first)
                summary_tab, cloud_tab, local_tab = st.tabs(["📊 Summary", "☁️ Cloud Models", "🖥️ Local Models"])
                
                # Summary Tab (now first)
                with summary_tab:
                    total_models = len(cloud_models) + len(local_models)
                    available_cloud = len([m for m in cloud_models if available_models.get(m[0], {}).get('is_available', False)])
                    available_local = len([m for m in local_models if available_models.get(m[0], {}).get('is_available', False)])
                    
                    st.markdown("### 📊 Models Summary")
                    
                    # Summary cards
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: rgba(33, 150, 243, 0.1); border: 1px solid #2196F3; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                            <strong style="color: #2196F3; font-size: 1.5em;">{len(cloud_models)}</strong><br>
                            <small>Cloud Models</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                            <strong style="color: #4CAF50; font-size: 1.5em;">{len(local_models)}</strong><br>
                            <small>Local Models</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style="background: rgba(255, 193, 7, 0.1); border: 1px solid #FFC107; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                            <strong style="color: #FFC107; font-size: 1.5em;">{total_models}</strong><br>
                            <small>Total Models</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Availability breakdown
                    st.markdown("### 📈 Availability Breakdown")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: rgba(33, 150, 243, 0.1); border: 1px solid #2196F3; border-radius: 6px; padding: 12px; margin: 8px 0;">
                            <strong>☁️ Cloud Models:</strong><br>
                            <small>✅ Available: {available_cloud}</small><br>
                            <small>❌ Unavailable: {len(cloud_models) - available_cloud}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; border-radius: 6px; padding: 12px; margin: 8px 0;">
                            <strong>🖥️ Local Models:</strong><br>
                            <small>✅ Available: {available_local}</small><br>
                            <small>❌ Unavailable: {len(local_models) - available_local}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Cloud Models Tab
                with cloud_tab:
                    if cloud_models:
                        st.markdown("### ☁️ Cloud Models")
                        st.markdown("**Hosted models requiring API keys and internet connection**")
                        
                        # Cloud Models Summary
                        available_cloud = len([m for m in cloud_models if available_models.get(m[0], {}).get('is_available', False)])
                        unavailable_cloud = len(cloud_models) - available_cloud
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"""
                            <div style="background: rgba(33, 150, 243, 0.1); border: 1px solid #2196F3; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                                <strong style="color: #2196F3; font-size: 1.5em;">{len(cloud_models)}</strong><br>
                                <small>Total Cloud Models</small>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div style="background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                                <strong style="color: #4CAF50; font-size: 1.5em;">{available_cloud}</strong><br>
                                <small>✅ Available</small>
                            </div>
                            """, unsafe_allow_html=True)
                        with col3:
                            st.markdown(f"""
                            <div style="background: rgba(244, 67, 54, 0.1); border: 1px solid #F44336; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                                <strong style="color: #F44336; font-size: 1.5em;">{unavailable_cloud}</strong><br>
                                <small>❌ Unavailable</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        for model_name, provider_icon, provider in cloud_models:
                            # Get model info for availability details
                            model_info = available_models.get(model_name, {})
                            is_available = model_info.get('is_available', False)
                            unavailable_reason = model_info.get('unavailable_reason', '')
                            
                            if is_available:
                                status_icon = "✅"
                                status_text = "Available"
                                status_color = "#4CAF50"
                                border_color = "#2196F3"
                                bg_color = "rgba(33, 150, 243, 0.1)"
                            else:
                                status_icon = "❌"
                                status_text = "Not Available"
                                status_color = "#F44336"
                                border_color = "#F44336"
                                bg_color = "rgba(244, 67, 54, 0.1)"
                            
                            st.markdown(f"""
                            <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 6px; padding: 12px; margin: 8px 0;">
                                <strong>{status_icon} {model_name}</strong> {provider_icon} <span style="color: #2196F3;">(☁️ Cloud)</span>
                                <br><small style="color: {status_color};"><strong>Status:</strong> {status_text}</small>
                                {f'<br><small style="color: #FF9800;"><strong>Reason:</strong> {unavailable_reason}</small>' if not is_available and unavailable_reason else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("☁️ **No cloud models available**")
                
                # Local Models Tab
                with local_tab:
                    if local_models:
                        st.markdown("### 🖥️ Local Models")
                        st.markdown("**Models running on your machine via Ollama (offline capable)**")
                        
                        # Local Models Summary
                        available_local = len([m for m in local_models if available_models.get(m[0], {}).get('is_available', False)])
                        unavailable_local = len(local_models) - available_local
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"""
                            <div style="background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                                <strong style="color: #4CAF50; font-size: 1.5em;">{len(local_models)}</strong><br>
                                <small>Total Local Models</small>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div style="background: rgba(76, 175, 80, 0.1); border: 1px solid #4CAF50; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                                <strong style="color: #4CAF50; font-size: 1.5em;">{available_local}</strong><br>
                                <small>✅ Available</small>
                            </div>
                            """, unsafe_allow_html=True)
                        with col3:
                            st.markdown(f"""
                            <div style="background: rgba(244, 67, 54, 0.1); border: 1px solid #F44336; border-radius: 6px; padding: 12px; margin: 8px 0; text-align: center;">
                                <strong style="color: #F44336; font-size: 1.5em;">{unavailable_local}</strong><br>
                                <small>❌ Unavailable</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        for model_name, provider_icon, provider in local_models:
                            # Get model info for lifecycle details
                            model_info = available_models.get(model_name, {})
                            lifecycle_status = model_info.get('lifecycle_status', 'unknown')
                            unavailable_reason = model_info.get('unavailable_reason', '')
                            
                            # Set status based on lifecycle
                            if lifecycle_status == "available":
                                status_icon = "✅"
                                status_text = "Available"
                                status_color = "#4CAF50"
                                border_color = "#4CAF50"
                                bg_color = "rgba(76, 175, 80, 0.1)"
                                lifecycle_badge = "🟢 Running"
                            elif lifecycle_status == "downloaded":
                                status_icon = "📦"
                                status_text = "Downloaded"
                                status_color = "#FF9800"
                                border_color = "#FF9800"
                                bg_color = "rgba(255, 152, 0, 0.1)"
                                lifecycle_badge = "🟡 Installed"
                            elif lifecycle_status == "need_download":
                                status_icon = "⬇️"
                                status_text = "Need Download"
                                status_color = "#2196F3"
                                border_color = "#2196F3"
                                bg_color = "rgba(33, 150, 243, 0.1)"
                                lifecycle_badge = "🔵 Not Installed"
                            else:
                                status_icon = "❓"
                                status_text = "Unknown"
                                status_color = "#9E9E9E"
                                border_color = "#9E9E9E"
                                bg_color = "rgba(158, 158, 158, 0.1)"
                                lifecycle_badge = "⚪ Unknown"
                            
                            st.markdown(f"""
                            <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 6px; padding: 12px; margin: 8px 0;">
                                <strong>{status_icon} {model_name}</strong> {provider_icon} <span style="color: #4CAF50;">(🖥️ Local)</span>
                                <br><small style="color: {status_color};"><strong>Status:</strong> {status_text}</small>
                                <br><small style="color: #666;"><strong>Lifecycle:</strong> {lifecycle_badge}</small>
                                {f'<br><small style="color: #FF9800;"><strong>Action:</strong> {unavailable_reason}</small>' if lifecycle_status != "available" and unavailable_reason else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("🖥️ **No local models available**")
            
            # Model History tab
            with agent_tabs[-1]:
                st.markdown("### 🔄 Model Switch History")
                metrics = get_metrics()
                if metrics:
                    model_usage_history = metrics.get('model_usage_history', [])
                    
                    if model_usage_history:
                        st.subheader("📋 Recent Model Switches")
                        for switch in model_usage_history:
                            st.markdown(f"""
                            <div style="background: rgba(255, 215, 0, 0.1); border: 1px solid #FFD700; border-radius: 4px; padding: 8px; margin: 4px 0;">
                                <strong>{switch.get('agent', 'Unknown').title()}</strong> switched from 
                                <span style="color: #FF6B6B;">{switch.get('old_model', 'unknown')}</span> to 
                                <span style="color: #4ECDC4;">{switch.get('new_model', 'unknown')}</span>
                                <br><small>Move: {switch.get('move_number', 'N/A')} | Time: {switch.get('timestamp', 'N/A')}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("🔄 **Model Switch Tracking Ready!** Model changes will be tracked here as agents switch between different LLMs.")
                else:
                    st.info("🔄 **Model Switch Tracking Ready!** The system will track model switches as agents change between different LLMs during gameplay.")

        else:
            st.error("❌ Failed to load agent or model information")
    
    with tab3:
        st.header("📡 MCP Protocol Logs")
        
        # Legend for message types
        st.markdown("**Message Type Legend:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("👤 **Player Move**")
        with col2:
            st.markdown("🤖 **AI Agent**")
        with col3:
            st.markdown("🎮 **Game State**")
        with col4:
            st.markdown("🔄 **Model Switch**")
        
        st.markdown("---")
        
        # JSON display toggle
        show_json = st.checkbox("🔍 Show JSON for each message", value=False, help="Toggle to see the raw JSON structure of each MCP message")
        
        logs_data = get_mcp_logs()
        if logs_data and logs_data.get('mcp_logs'):
            logs = logs_data['mcp_logs']
            if logs:
                for i, log in enumerate(logs[-10:]):  # Show last 10 logs
                    timestamp = log.get('timestamp', '')
                    agent = log.get('agent', '')
                    message_type = log.get('message_type', '')
                    data = log.get('data', {})
                    
                    # Check if this is a model switch message
                    is_model_switch = message_type == "ModelSwitch"
                    
                    # Create expandable section for each log with special styling for model switches
                    if is_model_switch:
                        # Special styling for model switch messages
                        old_model = data.get('old_model', 'unknown')
                        new_model = data.get('new_model', 'unknown')
                        switch_agent = data.get('agent', 'unknown')
                        
                        with st.expander(f"🔄 **MODEL SWITCH** - {switch_agent.title()} Agent", expanded=True):
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.1)); 
                                        border: 2px solid #FFD700; border-radius: 8px; padding: 12px; margin: 8px 0;">
                                <h4 style="color: #FFD700; margin: 0 0 8px 0;">🔄 Model Switch Event</h4>
                                <p style="margin: 4px 0;"><strong>Agent:</strong> {switch_agent.title()}</p>
                                <p style="margin: 4px 0;"><strong>From:</strong> <span style="color: #FF6B6B;">{old_model}</span></p>
                                <p style="margin: 4px 0;"><strong>To:</strong> <span style="color: #4ECDC4;">{new_model}</span></p>
                                <p style="margin: 4px 0;"><strong>Timestamp:</strong> {timestamp}</p>
                                <p style="margin: 4px 0;"><strong>Move Number:</strong> {data.get('move_number', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show JSON if toggle is enabled
                            if show_json:
                                st.markdown("**Raw JSON:**")
                                st.json(log)
                    else:
                        # Determine icon based on agent type
                        if agent == "GameEngine":
                            # GameEngine messages are usually player moves or game state changes
                            if message_type == "PlayerMove":
                                icon = "👤"  # Player move
                                color = "#4CAF50"  # Green
                                bg_color = "rgba(76, 175, 80, 0.1)"
                            else:
                                icon = "🎮"  # Game state change
                                color = "#2196F3"  # Blue
                                bg_color = "rgba(33, 150, 243, 0.1)"
                        elif agent in ["Scout", "Strategist", "Executor"]:
                            # AI agent messages
                            icon = "🤖"  # AI agent
                            color = "#FF9800"  # Orange
                            bg_color = "rgba(255, 152, 0, 0.1)"
                        else:
                            # Unknown agent type
                            icon = "📡"  # Default
                            color = "#9C27B0"  # Purple
                            bg_color = "rgba(156, 39, 176, 0.1)"
                        
                        # Regular message styling with dynamic icons
                        with st.expander(f"{icon} {agent} - {timestamp}", expanded=False):
                            st.markdown(f"""
                            <div style="background: {bg_color}; border: 1px solid {color}; border-radius: 6px; padding: 10px; margin: 8px 0;">
                                <strong>Agent:</strong> {agent}<br>
                                <strong>Message Type:</strong> {message_type}<br>
                                <strong>Timestamp:</strong> {timestamp}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show message data in a more readable format
                            if data:
                                st.markdown("**Data:**")
                                for key, value in data.items():
                                    st.markdown(f"- **{key}:** {value}")
                            
                            # Show JSON if toggle is enabled
                            if show_json:
                                st.markdown("**Raw JSON:**")
                                st.json(log)
            else:
                st.info("📡 **MCP Protocol Ready!** No logs yet because no game has been played. Make a move in the Game tab to see the agents communicate using the Multi-Agent Communication Protocol!")
        else:
            st.info("📡 **MCP Protocol Ready!** The communication system is active. Start playing to see real-time protocol logs between the AI agents.")
    
    with tab4:
        st.header("📊 Game Metrics")
        metrics = get_metrics()
        if metrics:
            # Create nested tabs for different metric categories
            overview_tab, mcp_tab, agent_tab, resource_tab = st.tabs(["📈 Overview", "📡 MCP Performance", "🤖 Agent Analytics", "⚡ Resources"])
            
            with overview_tab:
                st.subheader("📈 Game Overview")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('total_message_count', 0)}</div>
                        <div class="metric-label">Total Messages</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">${metrics.get('total_cost', 0):.6f}</div>
                        <div class="metric-label">Total Cost</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    duration = metrics.get('game_duration_seconds', 0)
                    duration_text = f"{duration:.1f}s" if duration > 0 else "0s"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{duration_text}</div>
                        <div class="metric-label">Game Duration</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    avg_times = metrics.get('avg_response_times', {})
                    if avg_times:
                        avg_time = sum(avg_times.values()) / len(avg_times)
                        avg_time_text = f"{avg_time:.2f}ms" if avg_time > 0 else "0ms"
                    else:
                        avg_time_text = "0ms"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{avg_time_text}</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with mcp_tab:
                st.subheader("📡 MCP Protocol Performance")
                
                # Message count breakdown
                st.markdown("**📊 Message Counts:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('total_message_count', 0)}</div>
                        <div class="metric-label">Total Messages</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('mcp_message_count', 0)}</div>
                        <div class="metric-label">Agent Messages</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    system_messages = metrics.get('total_message_count', 0) - metrics.get('mcp_message_count', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{system_messages}</div>
                        <div class="metric-label">GameEngine Messages</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Explanation of message counts
                st.info("💡 **Message Counts Explained:** Total Messages includes all system events (GameEngine) + agent communications. Message Flow Patterns below show only inter-agent communication.")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    # Message Latency
                    latency = metrics.get('avg_message_latency_ms', 0)
                    latency_text = f"{latency:.2f}ms" if latency > 0 else "0ms"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{latency_text}</div>
                        <div class="metric-label">Avg Message Latency</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Protocol Errors
                    errors = metrics.get('protocol_errors', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{errors}</div>
                        <div class="metric-label">Protocol Errors</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Cost per MCP Message
                    mcp_count = metrics.get('mcp_message_count', 0)
                    total_cost = metrics.get('total_cost', 0)
                    cost_per_message = total_cost / mcp_count if mcp_count > 0 else 0
                    cost_per_message_text = f"${cost_per_message:.6f}" if cost_per_message > 0 else "$0.000000"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{cost_per_message_text}</div>
                        <div class="metric-label">Cost per MCP Message</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Message Queue Depth
                    queue_depth = metrics.get('message_queue_depth', 0)
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{queue_depth}</div>
                        <div class="metric-label">Message Queue Depth</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Message Flow Patterns
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("🔄 Message Flow Patterns")
                message_patterns = metrics.get('message_flow_patterns', {})
                if message_patterns:
                    for pattern, count in message_patterns.items():
                        st.markdown(f"**{pattern}:** {count} messages")
                else:
                    st.info("🔄 **Message Flow Tracking Ready!** Communication patterns will be analyzed as agents interact.")
            
            with agent_tab:
                st.subheader("🤖 Agent Analytics")
                
                # Inter-Agent Response Times
                st.markdown("**Response Times:**")
                agent_response_times = metrics.get('agent_response_times', {})
                current_models = metrics.get('current_models', {})
                if agent_response_times:
                    for agent, response_time in agent_response_times.items():
                        response_text = f"{response_time:.2f}ms" if response_time > 0 else "0ms"
                        current_model = current_models.get(agent, "Unknown")
                        st.markdown(f"**{agent.title()}** ({current_model}): {response_text}")
                else:
                    st.info("🤖 **Agent Response Tracking Ready!** Response times will be tracked as agents communicate.")
                
                # Token Usage per Agent
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Token Usage:**")
                token_usage = metrics.get('token_usage_per_agent', {})
                if token_usage:
                    for agent, tokens in token_usage.items():
                        st.markdown(f"**{agent.title()}:** {tokens:,} tokens")
                else:
                    st.info("💬 **Token Usage Tracking Ready!** Token consumption will be tracked per agent.")
                
                # Performance Impact Analysis
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**📊 Performance Impact Analysis:**")
                model_usage_history = metrics.get('model_usage_history', [])
                if model_usage_history and agent_response_times:
                    st.info("🔄 **Model Switch Impact Analysis:** Compare response times and token usage before/after model switches to see performance changes.")
                    
                    # Show current model assignments
                    st.markdown("**Current Model Assignments:**")
                    current_models = metrics.get('current_models', {})
                    for agent, model in current_models.items():
                        st.markdown(f"**{agent.title()}:** {model}")
                else:
                    st.info("📊 **Performance Analysis Ready!** Impact of model switches on agent performance will be analyzed here.")
            
            with resource_tab:
                st.subheader("⚡ Resource Utilization")
                
                # System Resources
                st.markdown("**System Resources:**")
                resource_usage = metrics.get('resource_utilization', {})
                if resource_usage:
                    cpu_usage = resource_usage.get('cpu_percent', 0)
                    memory_usage = resource_usage.get('memory_mb', 0)
                    st.markdown(f"**CPU Usage:** {cpu_usage:.1f}%")
                    st.markdown(f"**Memory Usage:** {memory_usage:.1f} MB")
                else:
                    st.info("⚡ **Resource Monitoring Ready!** System resource usage will be tracked during MCP operations.")
                
                # LLM cost breakdown
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**LLM Cost Breakdown:**")
                llm_costs = metrics.get('llm_costs', {})
                if llm_costs:
                    has_costs = any(cost > 0 for cost in llm_costs.values())
                    if has_costs:
                        for model, cost in llm_costs.items():
                            if cost > 0:
                                st.markdown(f"**{model.title()}:** ${cost:.6f}")
                    else:
                        st.info("💰 **Cost Tracking Active!** No costs yet because no game has been played. Start playing to see real-time cost tracking across different LLM providers.")
                else:
                    st.info("💰 **Cost Tracking Ready!** The system will track costs across OpenAI, Anthropic, and Ollama models as you play.")
        else:
            st.info("📊 **Metrics System Ready!** Performance tracking is active. Play a game to see real-time metrics including MCP messages, costs, and response times.")
    
if __name__ == "__main__":
    main() 