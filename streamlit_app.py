import streamlit as st
import requests
import time
import json
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="🎮 X⚔️O Multi-Agent Battle",
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
        st.title("🎮 Tic Tac Toe 🎯 X ⚔️ O 🎯 Multi-Agent Battle 🎮")
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
        - **Scout Agent** (Llama2 7B): Analyzes the board state
        - **Strategist Agent** (Llama3 Latest): Creates strategic plans
        - **Executor Agent** (Llama2 7B): Makes the actual moves
        
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
        st.header("🎯 X ⚔️ O Battle 🎯")
        
        # Game status
        current_player = game_state.get('current_player', 'player')
        if current_player == 'player':
            st.info("👤 Your Turn")
        else:
            st.info("🕵️‍♂️ Double-O-AI Thinking")
        
        # Debug info (temporary)
        with st.expander("🔍 Debug Info"):
            st.write(f"Current Player: {current_player}")
            st.write(f"Game Over: {game_state.get('game_over', False)}")
            st.write(f"Winner: {game_state.get('winner', 'None')}")
            st.write(f"Move Number: {game_state.get('move_number', 0)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Show game result banner if game is over
        if game_state.get('game_over'):
            winner = game_state.get('winner')
            if winner == 'player':
                st.success("🎉 **Congratulations! You defeated Double-O-AI!** 🎉")
            elif winner == 'ai':
                st.error("🕵️‍♂️ **Double-O-AI has achieved victory! The secret agent prevails!** 🕵️‍♂️")
            elif winner == 'draw':
                st.warning("🤝 **A strategic stalemate! Both minds proved equally matched!** 🤝")
            else:
                st.warning("🤝 **Game ended in a draw! Well played by both sides!** 🤝")
        
        # Game board
        board = game_state.get('board', [['' for _ in range(3)] for _ in range(3)])
        
        # Create game board using pure Streamlit
        st.subheader("🎮 Tic Tac Toe Board")
        
        # Create 3x3 grid using Streamlit columns
        for i in range(3):
            cols = st.columns(3)
            for j in range(3):
                with cols[j]:
                    cell_value = board[i][j]
                    if cell_value == '':
                        # Empty cell - make it clickable
                        if not game_state.get('game_over', False) and current_player == 'player':
                            if st.button("⬜", key=f"cell_{i}_{j}", 
                                       use_container_width=True,
                                       help=f"Click to place your move at ({i}, {j})"):
                                st.session_state.pending_move = (i, j)
                                st.rerun()
                        else:
                            # Disabled cell
                            st.button("⬜", key=f"cell_{i}_{j}_disabled", 
                                    disabled=True, use_container_width=True)
                    else:
                        # Filled cell with custom colors
                        if cell_value == 'X':
                            st.markdown(f"""
                            <div style="
                                background-color: #2d2d2d; 
                                border: 2px solid #00ff88; 
                                border-radius: 8px; 
                                padding: 20px; 
                                text-align: center; 
                                font-size: 2.5rem; 
                                font-weight: bold; 
                                color: #00ff88;
                                margin: 4px;
                                box-shadow: 0 0 15px rgba(0, 255, 136, 0.3);
                            ">❌</div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="
                                background-color: #2d2d2d; 
                                border: 2px solid #ff6b6b; 
                                border-radius: 8px; 
                                padding: 20px; 
                                text-align: center; 
                                font-size: 2.5rem; 
                                font-weight: bold; 
                                color: #ff6b6b;
                                margin: 4px;
                                box-shadow: 0 0 15px rgba(255, 107, 107, 0.3);
                            ">⭕</div>
                            """, unsafe_allow_html=True)
        
        # Handle pending move
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
        
        # Game controls
        if st.button("🔄 New Game", use_container_width=True):
            if reset_game():
                # Clear session state and refresh game state
                st.session_state.game_state = None
                st.session_state.pending_move = None
                st.session_state.last_refresh = 0
                st.rerun()
        
        # Move history
        st.markdown("<br>", unsafe_allow_html=True)
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
    
    with tab2:
        st.header("🤖 AI Agents & Models")
        
        # Get metrics data for Model Switch History
        metrics = get_metrics()
        
        # Model Switch History
        st.subheader("🔄 Model Switch History")
        model_usage_history = metrics.get('model_usage_history', [])
        
        if model_usage_history:
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
        
        st.markdown("---")
        
        # Agent Information
        st.subheader("🤖 Agent Information")
        agents_data = get_agents()
        if agents_data and 'agents' in agents_data:
            for agent_name, agent in agents_data['agents'].items():
                with st.expander(f"**{agent['name']}** - {agent['role']}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Model:** {agent['model']}")
                        st.markdown(f"**Provider:** {agent['provider_type']} {agent['provider_icon']}")
                        st.markdown(f"**Description:** {agent['description']}")
                    with col2:
                        st.markdown("**Capabilities:**")
                        for capability in agent['capabilities']:
                            st.markdown(f"• {capability}")
        else:
            st.error("❌ Failed to load agent information")
        
        st.markdown("---")
        
        # Hot-Swappable Models
        st.subheader("🔄 Hot-Swappable Models")
        st.markdown("**Switch any agent to a different LLM mid-game!**")
        
        # Get available models
        models_data = get_models()
        if models_data and 'models' in models_data:
            current_models = models_data.get('current_models', {})
            available_models = models_data['models']
            
            # Simple model switching interface
            st.markdown("**Current Models:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Scout:** {current_models.get('scout', 'Unknown')}")
            with col2:
                st.markdown(f"**Strategist:** {current_models.get('strategist', 'Unknown')}")
            with col3:
                st.markdown(f"**Executor:** {current_models.get('executor', 'Unknown')}")
            
            st.markdown("---")
            
            # Model switching controls
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                agent_choice = st.selectbox(
                    "Select Agent:",
                    ["scout", "strategist", "executor"],
                    format_func=lambda x: x.title()
                )
            
            with col2:
                # Get available models for this agent
                current_model = current_models.get(agent_choice, 'Unknown')
                available_model_names = [name for name, info in available_models.items() if info.get('is_available', False)]
                model_options = [name for name in available_model_names if name != current_model]
                
                if model_options:
                    new_model = st.selectbox(
                        f"Switch to:",
                        model_options,
                        help=f"Current: {current_model}"
                    )
                else:
                    st.info("All models in use")
                    new_model = None
            
            with col3:
                if new_model and st.button(f"Switch", type="primary", key=f"switch_{agent_choice}_{new_model}"):
                    result = switch_model(agent_choice, new_model)
                    if result and result.get('success'):
                        st.success(f"✅ Switched!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            # Available models section
            st.markdown("---")
            st.markdown("**Available Models:**")
            
            # Provider icons legend
            st.markdown("**Provider Icons:** 🤖 OpenAI | 🧠 Anthropic | 🦙 Ollama")
            
            st.markdown("---")
            
            # Sort available models alphabetically
            sorted_models = sorted(
                [(model_name, model_info) for model_name, model_info in available_models.items() 
                 if model_info.get('is_available', False)],
                key=lambda x: x[0].lower()  # Case-insensitive sorting
            )
            
            for model_name, model_info in sorted_models:
                provider = model_info.get('provider', 'Unknown')
                provider_icon = {"openai": "🤖", "anthropic": "🧠", "ollama": "🦙"}.get(provider, "❓")
                
                # Determine if it's cloud or local
                model_type = "☁️ Cloud" if provider in ["openai", "anthropic"] else "🖥️ Local"
                
                st.markdown(f"✅ **{model_name}** {provider_icon} ({model_type})")
                    
        else:
            st.error("❌ Failed to load model information")
    
    with tab3:
        st.header("📡 MCP Protocol Logs")
        
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
                        # Regular message styling
                        with st.expander(f"📡 {agent} - {timestamp}", expanded=False):
                            st.markdown(f"**Agent:** {agent}")
                            st.markdown(f"**Message Type:** {message_type}")
                            st.markdown(f"**Timestamp:** {timestamp}")
                            
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