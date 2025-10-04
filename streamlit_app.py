"""
Streamlit MCP App
Streamlit dashboard for MCP Protocol
"""
import streamlit as st
import requests
import time
import json
from datetime import datetime
import asyncio

# Load configuration first (before page config)
from utils.config import config

# Configure page
st.set_page_config(
    page_title="Agentic Tic-Tac-Toe: MCP Protocol Showcase",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration from config file
api_config = config.get_api_config()
API_BASE = f"http://localhost:{api_config['port']}"

# Enhanced CSS for MCP theme
st.markdown("""
<style>
    /* MCP Dark Theme */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* MCP Header styling */
    .mcp-header {
        color: #00d4ff;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 30px #00d4ff;
        animation: mcpGlow 2s ease-in-out infinite alternate;
    }
    
    .mcp-sub-header {
        color: #00d4ff;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    @keyframes mcpGlow {
        from { text-shadow: 0 0 5px #00d4ff, 0 0 10px #00d4ff, 0 0 15px #00d4ff; }
        to { text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 30px #00d4ff; }
    }
    
    /* MCP Agent Cards */
    .mcp-agent-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        position: relative;
    }
    
    .mcp-agent-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #00d4ff, #0099cc, #00d4ff);
        border-radius: 17px;
        z-index: -1;
        animation: mcpBorderGlow 3s ease-in-out infinite;
    }
    
    @keyframes mcpBorderGlow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Improve metrics text visibility */
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stMetric > div > div {
        color: #ffffff !important;
    }
    
    .stMetric > div > div > div {
        color: #ffffff !important;
        font-weight: bold;
    }
    
    .stMetric label {
        color: #cccccc !important;
        font-weight: 500;
    }
    
    /* Make metric values more visible */
    .stMetric [data-testid="metric-value"] {
        color: #ffffff !important;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .stMetric [data-testid="metric-label"] {
        color: #cccccc !important;
        font-weight: 500;
    }
    
    /* Improve section headers */
    h4 {
        color: #ffffff !important;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Make markdown text more visible */
    .stMarkdown p {
        color: #ffffff !important;
    }
    
    .stMarkdown strong {
        color: #ffffff !important;
        font-weight: bold;
    }
    
    /* MCP Status Indicators */
    .mcp-status-online {
        color: #00ff88;
        font-weight: bold;
    }
    
    .mcp-status-offline {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* MCP Protocol Logs */
    .mcp-log-entry {
        background: rgba(0, 212, 255, 0.1);
        border-left: 3px solid #00d4ff;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
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
        background-color: #00d4ff;
        color: #0e1117;
        font-weight: bold;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
        border: 1px solid #00d4ff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00d4ff;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #cccccc;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

def get_game_state():
    """Get current game state from MCP API"""
    try:
        import time
        import random
        # Add multiple cache-busting parameters to force fresh data
        cache_buster = int(time.time() * 1000)  # milliseconds
        random_seed = random.randint(1000, 9999)  # random number
        print(f"[DEBUG] Fetching game state from API (cache-buster: {cache_buster}, random: {random_seed})")
        response = requests.get(f"{API_BASE}/state?t={cache_buster}&r={random_seed}")
        print(f"[DEBUG] Game state API response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[DEBUG] Game state: {result}")
            return result
        else:
            st.error(f"Error fetching game state: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching game state: {e}")
        return None

def get_agent_status():
    """Get MCP agent status"""
    try:
        response = requests.get(f"{API_BASE}/agents/status")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching agent status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching agent status: {e}")
        return None

def get_mcp_logs():
    """Get MCP protocol logs"""
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

def make_move(row, col):
    """Make a move via MCP API"""
    try:
        print(f"[DEBUG] Making move: row={row}, col={col}")
        response = requests.post(f"{API_BASE}/make-move", 
                               json={"row": row, "col": col})
        print(f"[DEBUG] API response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[DEBUG] API response: {result}")
            return result
        else:
            st.error(f"Error making move: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error making move: {e}")
        return None

def reset_game():
    """Reset game via MCP API"""
    try:
        response = requests.post(f"{API_BASE}/reset-game")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error resetting game: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error resetting game: {e}")
        return None

def switch_agent_model(agent_id, model):
    """Switch agent model via MCP API"""
    try:
        response = requests.post(f"{API_BASE}/agents/{agent_id}/switch-model",
                               json={"model": model})
        if response.status_code == 200:
            return response.json()
        else:
            # Parse error message from API
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            
            return {"success": False, "error": error_msg}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_agent_metrics(agent_id):
    """Get agent performance metrics"""
    try:
        response = requests.get(f"{API_BASE}/agents/{agent_id}/metrics")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching metrics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")
        return None

def render_game_board(board, game_over=False):
    """Render the Tic Tac Toe board with proper styling"""
    
    # Add custom CSS for game board styling
    st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean modern page styling */
    .main .block-container {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Remove excessive top spacing */
    .main .block-container > div {
        padding-top: 0 !important;
    }
    
    /* Reduce header spacing */
    header {
        display: none !important;
    }
    
    /* Remove Streamlit's default top padding */
    .stApp > div:first-child {
        padding-top: 0 !important;
    }
    
    /* Clean modern title styling */
    h1 {
        color: #2c3e50 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin-top: 0 !important;
        margin-bottom: 1rem !important;
        padding-top: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Clean modern button styling - white with green borders for empty cells */
    .stButton > button {
        background: #ffffff !important;
        color: #6c757d !important;
        border: 3px solid #00ff88 !important;
        border-radius: 8px !important;
        padding: 0 !important;
        font-size: 24px !important;
        font-weight: bold !important;
        box-shadow: 0 0 10px rgba(0,255,136,0.3) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        min-height: 100px !important;
        height: 100px !important;
        margin: 0 !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3) !important;
    }
    
    .game-board-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        padding: 20px;
        background: transparent;
        margin: 20px 0;
    }
    
    /* Filled cells should be bright green */
    .stButton > button[type="primary"] {
        background-color: #00ff88 !important;
        color: white !important;
        border: 3px solid #00ff88 !important;
        box-shadow: 0 0 15px rgba(0,255,136,0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 20px rgba(0,255,136,0.5) !important;
        border-color: #00ff88 !important;
    }
    
    .stButton > button:disabled {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
        border-color: #dee2e6 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* NEW GAME button styling - bright green with more specific selectors */
    .stButton > button[key="new_game"],
    .stButton > button[data-testid="baseButton-primary"],
    .stButton > button[type="submit"],
    .stButton > button:has-text("NEW GAME") {
        background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%) !important;
        background-color: #00ff00 !important;
        color: white !important;
        border: 3px solid #00ff00 !important;
        border-radius: 12px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 15px 30px !important;
        width: 100% !important;
        max-width: 400px !important;
        margin: 0 auto !important;
        box-shadow: 0 0 20px rgba(0,255,0,0.4) !important;
        transition: all 0.3s ease !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    .stButton > button[key="new_game"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover,
    .stButton > button[type="submit"]:hover,
    .stButton > button:has-text("NEW GAME"):hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 0 30px rgba(0,255,0,0.6) !important;
        background: linear-gradient(135deg, #00ff00 0%, #00ff00 100%) !important;
        background-color: #00ff00 !important;
    }
    
    /* Force bright green for all primary buttons */
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-primary"]:focus,
    button[data-testid="baseButton-primary"]:active {
        background: #00ff00 !important;
        background-color: #00ff00 !important;
        background-image: none !important;
        color: white !important;
        border: 3px solid #00ff00 !important;
        box-shadow: 0 0 20px rgba(0,255,0,0.4) !important;
    }
    
    
    /* Lighter info boxes */
    .stAlert {
        background-color: #2a3a4a !important;
        border: 1px solid #4a5a6a !important;
        border-radius: 8px !important;
    }
    
    .stAlert > div {
        background-color: #2a3a4a !important;
        color: #e0e0e0 !important;
    }
    
    .stInfo {
        background-color: #2a3a4a !important;
        border: 1px solid #4a5a6a !important;
        border-radius: 8px !important;
    }
    
    .stInfo > div {
        background-color: #2a3a4a !important;
        color: #e0e0e0 !important;
    }

    .game-board {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 4px;
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .game-cell {
        width: 80px;
        height: 80px;
        border: 2px solid #333;
                    border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s ease;
        background-color: #ffffff;
        color: #000;
    }
    
    .game-cell.filled {
        background-color: #00ff88;
        color: #000;
        border-color: #00ff88;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
        cursor: default;
        font-size: 32px !important;
        font-weight: 900 !important;
        font-family: 'Arial Black', Arial, sans-serif !important;
    }
    
    /* Target Streamlit buttons that contain X or O - more aggressive selectors */
    .stButton > button:not(:empty),
    button[data-testid="baseButton-primary"]:not(:empty),
    button[data-testid="baseButton-secondary"]:not(:empty),
    .stButton button:not(:empty),
    button:not(:empty) {
        font-size: 32px !important;
        font-weight: 900 !important;
        font-family: 'Arial Black', Arial, sans-serif !important;
        line-height: 1 !important;
        padding: 0 !important;
    }
    
    /* Even more specific targeting for game buttons */
    div[data-testid="column"] .stButton > button:not(:empty) {
        font-size: 32px !important;
        font-weight: 900 !important;
        font-family: 'Arial Black', Arial, sans-serif !important;
    }
    
    .game-cell.empty:hover {
        background-color: #f0f0f0;
        border-color: #00ff88;
        box-shadow: 0 0 8px rgba(0, 255, 136, 0.3);
    }
    
    .game-cell.empty:active {
        background-color: #e0e0e0;
        transform: scale(0.95);
    }
    
    /* Game board buttons only - not all buttons */
    .game-board .stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        width: 80px !important;
        height: 80px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .game-board .stButton > button:hover {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* NEW GAME button styling - bright green */
    .stButton > button[kind="primary"] {
        background-color: #00ff00 !important;
        color: white !important;
        border: 3px solid #00ff00 !important;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.4) !important;
        font-weight: bold !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #00ff00 !important;
        color: white !important;
        box-shadow: 0 0 30px rgba(0, 255, 0, 0.6) !important;
    }
    
    /* Game board button styling to match div size exactly */
    .game-board-container .stButton > button {
        width: 80px !important;
        height: 80px !important;
        min-width: 80px !important;
        min-height: 80px !important;
        max-width: 80px !important;
        max-height: 80px !important;
        margin: 0 auto !important;
        padding: 0 !important;
        border: 2px solid #666 !important;
        border-radius: 8px !important;
        background-color: #333 !important;
        color: #666 !important;
        font-size: 28px !important;
        font-weight: bold !important;
        box-shadow: 0 0 5px rgba(102, 102, 102, 0.3) !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Filled cells (disabled buttons) - neon green styling with maximum specificity */
    .game-board-container .stButton > button[disabled],
    .game-board-container .stButton > button:disabled,
    .game-board-container button[disabled],
    .game-board-container button:disabled {
        border: 2px solid #00ff88 !important;
        background-color: #00ff88 !important;
        background: #00ff88 !important;
        color: #000 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.4) !important;
        opacity: 1 !important;
        cursor: default !important;
        font-weight: bold !important;
    }
    
    
    /* Remove extra spacing */
    .game-board-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .game-board-container .stButton {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Force exact button dimensions - no size changes allowed */
    .game-board-container .stButton {
        width: 100px !important;
        height: 100px !important;
        min-width: 100px !important;
        max-width: 100px !important;
        min-height: 100px !important;
        max-height: 100px !important;
        margin: 0 !important;
        padding: 0 !important;
        flex: none !important;
        display: inline-block !important;
        position: relative !important;
    }
    
    /* Hide buttons completely - use only custom divs */
    .game-board-container .stButton > button {
        display: none !important;
    }
    
    
    </style>
    """, unsafe_allow_html=True)    # Simple 3x3 grid using Streamlit columns
    st.markdown('<div class="game-board-container">', unsafe_allow_html=True)
    
    # Create 3x3 grid using Streamlit columns with equal spacing
    for row in range(3):
        cols = st.columns(3, gap="small")
        for col in range(3):
            with cols[col]:
                cell_value = board[row][col] if board[row][col] else ""
                
                if cell_value:
                    # Filled cell - show the value with custom styling
                    st.markdown(f"""
                    <style>
                    button[key="filled_{row}_{col}"] {{
                        font-size: 32px !important;
                        font-weight: 900 !important;
                        font-family: 'Arial Black', Arial, sans-serif !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                    st.button(cell_value, key=f"filled_{row}_{col}", disabled=True, type="primary", use_container_width=True)
                else:
                    # Empty cell - clickable button
                    if not game_over:
                        if st.button("", key=f"move_{row}_{col}", help=f"Click to place X at ({row}, {col})", use_container_width=True):
                            # Make move instantly
                            result = make_move(row, col)
                            if result and result.get('success'):
                                st.success(f"✅ Your move recorded at ({row}, {col})")
                                
                                # Force refresh of game state to update Move History immediately
                                print(f"[DEBUG] Player move result: {result}")
                                print(f"[DEBUG] Forcing game state refresh for Move History update")
                                
                                # Force Move History refresh by updating session state
                                st.session_state.move_history_refresh = time.time()
                                print(f"[DEBUG] Set move_history_refresh = {st.session_state.move_history_refresh}")
                                
                                # Force immediate Move History update by clearing cache
                                if 'game_state_cache' in st.session_state:
                                    del st.session_state.game_state_cache
                                    print(f"[DEBUG] Cleared game_state_cache")
                                
                                # Set flag to force Move History refresh on next render
                                st.session_state.force_move_history_refresh = True
                                print(f"[DEBUG] Set force_move_history_refresh = True")
                                
                                # Check if AI should move (set flag for next render)
                                if not result.get('game_over', False) and result.get('current_player') == 'ai':
                                    st.session_state.trigger_ai_move = True
                                    print(f"[DEBUG] Set trigger_ai_move = True")
                                else:
                                    print(f"[DEBUG] Not setting trigger_ai_move - game_over: {result.get('game_over')}, current_player: {result.get('current_player')}")
                                
                                st.rerun()  # Show player move first
                            else:
                                st.error("Failed to make move")
                    else:
                        # Disabled empty cell
                        st.button("", key=f"disabled_{row}_{col}", disabled=True, use_container_width=True)
    
    # Single NEW GAME button - spans across the board
    if st.button("🔄 NEW GAME", key="new_game", help="Start a new game", type="primary", use_container_width=True):
        # Reset backend game state
        try:
            response = requests.post(f"{API_BASE}/reset-game")
            if response.status_code == 200:
                st.success("🎮 New game started!")
            else:
                st.error("Failed to reset game on server")
        except Exception as e:
            st.error(f"Error resetting game: {e}")
        
        # Reset frontend session state
        st.session_state.board = [['', '', ''] for _ in range(3)]
        st.session_state.current_player = 'X'
        st.session_state.game_over = False
        st.session_state.winner = None
        st.session_state.move_history = []
        
        # Clear Move History session state
        if 'fresh_move_history' in st.session_state:
            del st.session_state.fresh_move_history
        if 'force_move_history_refresh' in st.session_state:
            del st.session_state.force_move_history_refresh
        if 'move_history_refresh' in st.session_state:
            del st.session_state.move_history_refresh
        if 'game_state_cache' in st.session_state:
            del st.session_state.game_state_cache
        
        print(f"[DEBUG] NEW GAME: Cleared all Move History session state")
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_agent_status(agent_status):
    """Render MCP agent status"""
    st.markdown("### 🤖 MCP Agent Status")
    
    if not agent_status:
        st.error("Failed to load agent status")
        return
    
    # Coordinator status
    coordinator = agent_status.get("coordinator", {})
    st.markdown(f"**Coordinator Status:** {coordinator.get('coordinator_status', 'Unknown')}")
    
    # Individual agent status
    agents = ["scout", "strategist", "executor"]
    agent_names = {
        "scout": "🔍 Scout Agent",
        "strategist": "🧠 Strategist Agent", 
        "executor": "⚡ Executor Agent"
    }
    
    for agent_id in agents:
        agent_data = agent_status.get(agent_id)
        if agent_data:
            with st.expander(f"{agent_names.get(agent_id, agent_id)} Status", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Agent ID:** {agent_data.get('agent_id', 'Unknown')}")
                    st.markdown(f"**Role:** {agent_data.get('role', 'Unknown')}")
                    st.markdown(f"**Status:** {'🟢 Online' if agent_data.get('is_running') else '🔴 Offline'}")
                
                with col2:
                    # Show specific LLM model instead of generic "LLM"
                    model_name = agent_data.get('current_model', 'Unknown')
                    if model_name == 'LLM' or model_name == 'Unknown':
                        # Try to get the actual model name from the agent data
                        actual_model = agent_data.get('model_name', agent_data.get('llm_model', 'gpt-5-mini'))
                        st.markdown(f"**LLM Model:** {actual_model}")
                    else:
                        st.markdown(f"**LLM Model:** {model_name}")
                    st.markdown(f"**MCP Port:** {agent_data.get('mcp_port', 'Unknown')}")
                    # Remove memory size as it's not relevant
        else:
            st.warning(f"{agent_names.get(agent_id, agent_id)}: Not available")

def render_mcp_logs(logs_data):
    """Render MCP protocol logs"""
    st.markdown("### 📡 MCP Protocol Logs")
    
    if not logs_data or not logs_data.get('mcp_logs'):
        st.info("No MCP logs available")
        return
    
    logs = logs_data['mcp_logs']
    
    # Show recent logs (last 10)
    recent_logs = logs[-10:] if len(logs) > 10 else logs
    
    for log in reversed(recent_logs):
        timestamp = log.get('timestamp', 'Unknown')
        agent = log.get('agent', 'Unknown')
        message_type = log.get('message_type', 'Unknown')
        data = log.get('data', {})
                    
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%H:%M:%S')
        except:
            formatted_time = timestamp
        
        # Agent emoji mapping
        agent_emojis = {
            'scout': '🔍',
            'strategist': '🧠',
            'executor': '⚡',
            'GameEngine': '🎮'
        }
        
        emoji = agent_emojis.get(agent, '🤖')
        
        with st.expander(f"{emoji} {agent} - {message_type} ({formatted_time})", expanded=False):
            st.markdown(f"**Timestamp:** {timestamp}")
            st.markdown(f"**Agent:** {agent}")
            st.markdown(f"**Message Type:** {message_type}")
            st.markdown("**Data:**")
            st.json(data)

def render_agent_metrics():
    """Render agent performance metrics"""
    st.markdown("### 📊 Agent Performance Metrics")
    
    agents = ["scout", "strategist", "executor"]
    agent_names = {
        "scout": "🔍 Scout Agent",
        "strategist": "🧠 Strategist Agent",
        "executor": "⚡ Executor Agent"
    }
    
    for agent_id in agents:
        metrics = get_agent_metrics(agent_id)
        if metrics:
            with st.expander(f"{agent_names.get(agent_id, agent_id)} Metrics", expanded=True):
                # Performance Metrics Section
                st.markdown("#### ⚡ Performance Metrics")
                col1, col2, col3, col4 = st.columns(4)
            
                with col1:
                    st.metric("Requests", metrics.get('request_count', 0))
                
                with col2:
                    avg_time = metrics.get('avg_response_time', 0)
                    st.metric("Avg Time", f"{avg_time:.6f}s")
                
                with col3:
                    min_time = metrics.get('min_response_time', 0)
                    st.metric("Min Time", f"{min_time:.6f}s")
                
                with col4:
                    max_time = metrics.get('max_response_time', 0)
                    st.metric("Max Time", f"{max_time:.6f}s")

                # LLM-Specific Metrics Section
                st.markdown("#### 🤖 LLM Metrics")
                col5, col6, col7, col8 = st.columns(4)

                with col5:
                    st.metric("Total Tokens", metrics.get('total_tokens', 0))

                with col6:
                    tokens_per_req = metrics.get('tokens_per_request', 0)
                    st.metric("Tokens/Request", f"{tokens_per_req:.1f}")

                with col7:
                    success_rate = metrics.get('api_success_rate', 100)
                    st.metric("API Success", f"{success_rate:.1f}%")

                with col8:
                    errors = metrics.get('api_error_count', 0)
                    timeouts = metrics.get('timeout_count', 0)
                    st.metric("Errors/Timeouts", f"{errors}/{timeouts}")

                # Model and Timestamp with better visibility
                st.markdown("---")
                model_name = metrics.get('current_model', 'Unknown')
                if model_name == 'LLM' or model_name == 'Unknown':
                    actual_model = metrics.get('model_name', metrics.get('llm_model', 'gpt-5-mini'))
                    st.markdown(f"**Current Model:** {actual_model}")
                else:
                    st.markdown(f"**Current Model:** {model_name}")

                # Make timestamp more visible
                timestamp = metrics.get('timestamp', 'Unknown')
                st.markdown(f"**Last updated:** {timestamp}")
        else:
            st.warning(f"⚠️ {agent_names.get(agent_id, agent_id)} metrics not available")

def render_model_switching():
    """Render model switching interface"""
    st.markdown("### 🔄 Model Switching")
    
    agent_status = get_agent_status()
    if not agent_status:
        st.error("Failed to load agent status")
        return
    
    # Fetch available models from API
    try:
        models_response = requests.get(f"{API_BASE}/models")
        if models_response.status_code == 200:
            models_data = models_response.json()
            available_models = []
            model_descriptions = {}
            
            for model_name, model_info in models_data.get("models", {}).items():
                if model_info.get("is_available", False):
                    available_models.append(model_name)
                    model_descriptions[model_name] = f"{model_info.get('display_name', model_name)} - {model_info.get('description', '')}"
            
            # If no available models, show all models with their status
            if not available_models:
                st.warning("No models are currently available. Showing all models:")
                for model_name, model_info in models_data.get("models", {}).items():
                    available_models.append(model_name)
                    status = "✅ Available" if model_info.get("is_available", False) else "❌ Unavailable"
                    reason = model_info.get("unavailable_reason", "")
                    model_descriptions[model_name] = f"{model_info.get('display_name', model_name)} - {status} - {reason}"
            
            # Debug info
            st.info(f"Found {len(available_models)} models: {available_models}")
        else:
            st.error(f"Failed to load available models: HTTP {models_response.status_code}")
            return
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return
    
    agents = ["scout", "strategist", "executor"]
    agent_names = {
        "scout": "🔍 Scout Agent",
        "strategist": "🧠 Strategist Agent",
        "executor": "⚡ Executor Agent"
    }
    
    for agent_id in agents:
        agent_data = agent_status.get(agent_id)
        
        # Get the current model name
        if agent_data:
            current_model = agent_data.get('current_model', 'Unknown')
            if current_model == 'LLM' or current_model == 'Unknown':
                # Try to get the actual model name from other fields
                actual_model = agent_data.get('model_name', agent_data.get('llm_model', 'gpt-5-mini'))
                current_model = actual_model
        else:
            # Default model when agent is not available
            current_model = 'llama3.2-1b'  # Default model
        
        with st.expander(f"{agent_names.get(agent_id, agent_id)} - Current: {current_model}", expanded=False):
            if available_models:
                # Show model descriptions
                st.markdown("**Available Models:**")
                for model in available_models[:5]:  # Show first 5 models
                    if model in model_descriptions:
                        st.markdown(f"• **{model}**: {model_descriptions[model]}")
                
                selected_model = st.selectbox(
                    f"Select new model for {agent_id}:",
                    available_models,
                    key=f"model_{agent_id}"
                )
                
                if st.button(f"Switch {agent_id} to {selected_model}", key=f"switch_{agent_id}"):
                    result = switch_agent_model(agent_id, selected_model)
                    if result and result.get('success'):
                        st.success(f"Successfully switched {agent_id} to {selected_model}")
                        st.rerun()
                    else:
                        error_msg = result.get('error', 'Unknown error') if result else 'No response from server'
                        st.error(f"Failed to switch {agent_id} model: {error_msg}")
            else:
                st.warning("No available models found")

def main():
    """Main Streamlit app"""
    
    # Initialize trigger_ai_move if not set
    if 'trigger_ai_move' not in st.session_state:
        st.session_state.trigger_ai_move = False
        print(f"[DEBUG] Initialize trigger_ai_move to False")
    
    
    # Header with GitHub link
    st.markdown("""
    <style>
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .github-link {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: linear-gradient(135deg, #24292e 0%, #1a1e22 100%);
        border-radius: 8px;
        text-decoration: none;
        color: white;
        font-weight: 500;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .github-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        text-decoration: none;
        color: white;
    }
    .github-logo {
        width: 24px;
        height: 24px;
    }
    </style>
    
    <div class="header-container">
        <div>
            <h1 style='text-align: center;'>
                🎮 🤖 <span style='background: linear-gradient(90deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>Agentic Tic-Tac-Toe with CrewAI and MCP</span> 🚀 ⚡
            </h1>
        </div>
        <a href="https://github.com/arun-gupta/mcp-multiplayer-game" target="_blank" class="github-link">
            <svg class="github-logo" viewBox="0 0 16 16" fill="white">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            <span>View on GitHub</span>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API connection
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.success("✅ AI Team Ready - Three agents are online and ready to play!")
        else:
            st.error("❌ AI Team Offline - Backend connection failed")
            return
    except Exception as e:
        st.error("❌ AI Team Offline - Cannot connect to backend")
        st.info("Make sure to run: `python main.py`")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎮 Game", 
        "🤖 Agents", 
        "📡 MCP Logs", 
        "📊 Metrics",
        "⚙️ Settings"
    ])
    
    with tab1:
        print("DEBUG: Entering Game tab (tab1)")
        
        
        # Get and display game state
        game_state = get_game_state()
        print(f"DEBUG: game_state = {game_state}")
        if game_state:
            board = game_state.get('board', [])
            current_player = game_state.get('current_player', 'player')
            move_number = game_state.get('move_number', 0)
            game_over = game_state.get('game_over', False)
            winner = game_state.get('winner')
            
            print(f"[DEBUG] Game state - current_player: {current_player}, move_number: {move_number}, trigger_ai_move: {st.session_state.get('trigger_ai_move', False)}")
            
            # Create two-column layout: Game Board (50%) and Player Moves (50%)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 🎮 Game Board")
                
                # Show first-move delay explanation
                if move_number == 0:
                    st.info("💡 **First move tip**: The AI may take a few seconds to respond on the first move as it loads the model. Subsequent moves will be faster!")
                
                # Render game board
                print(f"[DEBUG] Rendering board with state: {board}")
                render_game_board(board, game_over)
            
            # Handle AI move trigger AFTER board is rendered
            if st.session_state.get('trigger_ai_move', False):
                st.session_state.trigger_ai_move = False  # Reset flag
                print(f"[DEBUG] AI move trigger activated - current_player: {current_player}")
                print(f"[DEBUG] AI move should now be triggered")
                
                with st.spinner("🤖 AI is thinking..."):
                    start_time = time.time()
                    try:
                        ai_result = requests.post(f"{API_BASE}/ai-move")
                        duration = time.time() - start_time
                        
                        if ai_result.status_code == 200:
                            result = ai_result.json()
                            print(f"[DEBUG] AI move result: {result}")
                            if result.get("success"):
                                # Update local move history with AI move
                                if 'local_move_history' not in st.session_state:
                                    st.session_state.local_move_history = []
                                
                                ai_move = result.get('move', {})
                                if ai_move and 'row' in ai_move and 'col' in ai_move:
                                    move_number = len(st.session_state.local_move_history) + 1
                                    st.session_state.local_move_history.append({
                                        'move_number': move_number,
                                        'player': 'ai',
                                        'position': {'row': ai_move['row'], 'col': ai_move['col'], 'value': 'O'}
                                    })
                                    print(f"[DEBUG] Updated local move history with AI move: {st.session_state.local_move_history}")
                                
                                st.success(f"✅ AI move completed in {duration:.3f}s")
                                
                                
                                print(f"[DEBUG] AI move successful, calling st.rerun()")
                                st.rerun()
                            else:
                                st.error(f"❌ AI move failed after {duration:.3f}s")
                                st.error(f"Error: {result.get('error', 'Unknown error')}")
                        else:
                            st.error("Failed to trigger AI move")
                    except Exception as e:
                        st.error(f"Error triggering AI move: {e}")
            
            # Game board already has NEW GAME button
            
            # Display winner if game is over (after NEW GAME button)
            if game_over and winner:
                    if winner == "player":
                        st.success("🎉 You Win! Congratulations!")
                    elif winner == "ai":
                        st.error("🤖 Double-O-AI Wins! Better luck next time!")
                    elif winner == "draw":
                        st.info("🤝 It's a Draw! Good game!")
            
            with col2:
                st.markdown("### 📝 Move History")
                
                # Show move history - force fresh data from API
                print(f"[DEBUG] Move History - game_state keys: {list(game_state.keys()) if game_state else 'None'}")
                print(f"[DEBUG] Move History - game_history: {game_state.get('game_history', 'NOT_FOUND') if game_state else 'None'}")
                print(f"[DEBUG] Move History - local_move_history: {st.session_state.get('local_move_history', 'NOT_FOUND')}")
                print(f"[DEBUG] Move History - move_history_refresh: {st.session_state.get('move_history_refresh', 'NOT_SET')}")
                print(f"[DEBUG] Move History - force_move_history_refresh: {st.session_state.get('force_move_history_refresh', 'NOT_SET')}")
                
                
                # Fetch fresh game state for Move History to ensure we have latest data
                st.write(f"🔍 **Debug - About to call get_game_state() for Move History**")
                
                # Try direct API call to bypass any caching
                import time
                import random
                cache_buster = int(time.time() * 1000)
                random_seed = random.randint(1000, 9999)
                st.write(f"🔍 **Debug - Making direct API call with cache-buster: {cache_buster}, random: {random_seed}**")
                
                try:
                    import requests
                    response = requests.get(f"{API_BASE}/state?t={cache_buster}&r={random_seed}")
                    st.write(f"🔍 **Debug - Direct API response status: {response.status_code}**")
                    if response.status_code == 200:
                        fresh_game_state = response.json()
                        st.write(f"🔍 **Debug - Direct API response: {fresh_game_state}**")
                    else:
                        st.write(f"🔍 **Debug - Direct API failed: {response.status_code}**")
                        fresh_game_state = get_game_state()
                except Exception as e:
                    st.write(f"🔍 **Debug - Direct API error: {e}**")
                    fresh_game_state = get_game_state()
                
                move_history = []
                
                # Debug: Show fresh game_state info in UI
                st.write(f"🔍 **Debug - fresh_game_state type:** {type(fresh_game_state)}")
                st.write(f"🔍 **Debug - fresh_game_state is None:** {fresh_game_state is None}")
                if fresh_game_state:
                    st.write(f"🔍 **Debug - fresh_game_state keys:** {list(fresh_game_state.keys())}")
                    st.write(f"🔍 **Debug - fresh_game_state full content:** {fresh_game_state}")
                    st.write(f"🔍 **Debug - fresh_game_history:** {fresh_game_state.get('game_history', 'NOT_FOUND')}")
                else:
                    st.write(f"🔍 **Debug - fresh_game_state is None or empty**")
                
                if fresh_game_state and 'game_history' in fresh_game_state:
                    move_history = fresh_game_state['game_history']
                    st.write(f"🔍 **Debug - Using fresh game_history: {len(move_history)} moves**")
                    st.write(f"🔍 **Debug - Move History content:** {move_history}")
                else:
                    st.write(f"🔍 **Debug - No game_history in fresh game_state**")
                
                if move_history:
                    print(f"[DEBUG] Rendering {len(move_history)} moves in Move History")
                    for move in move_history:
                        move_number = move.get('move_number', 0)
                        player = move.get('player', 'unknown')
                        position = move.get('position', {})
                        row = position.get('row', 0)
                        col = position.get('col', 0)
                        symbol = position.get('value', '')
                        
                        if player == 'player':
                            st.write(f"{move_number}. 👤 You placed {symbol} at ({row}, {col})")
                        else:
                            st.write(f"{move_number}. 🤖 Double-O-AI placed {symbol} at ({row}, {col})")
                else:
                    print(f"[DEBUG] No moves to display - showing default message")
                    st.info("No moves yet - click a cell to start!")
                
                # Game outcome is already shown at the top of the game board
                # No need to duplicate it in the move history
        else:
            st.error("Failed to load game state")
    
    with tab2:
        # Get agent status
        agent_status = get_agent_status()
        if agent_status:
            render_agent_status(agent_status)
        else:
            st.error("Failed to load agent status")
    
    with tab3:
        # Get MCP logs
        logs_data = get_mcp_logs()
        if logs_data:
            render_mcp_logs(logs_data)
        else:
            st.error("Failed to load MCP logs")
    
    with tab4:
        # Agent metrics
        render_agent_metrics()
    
    with tab5:
        # Model switching
        render_model_switching()
        
        # System info
        st.markdown("### 🔧 System Information")
        try:
            health_response = requests.get(f"{API_BASE}/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                st.json(health_data)
        except Exception as e:
            st.error(f"Failed to get system info: {e}")
    
if __name__ == "__main__":
    main() 
