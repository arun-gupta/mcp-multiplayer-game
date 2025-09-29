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

# Configure page
st.set_page_config(
    page_title="Agentic Tic-Tac-Toe: MCP Protocol Showcase",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE = "http://localhost:8000"

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
        response = requests.get(f"{API_BASE}/state")
        if response.status_code == 200:
            return response.json()
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
        response = requests.post(f"{API_BASE}/make-move", 
                               json={"row": row, "col": col})
        if response.status_code == 200:
            return response.json()
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
            st.error(f"Error switching model: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error switching model: {e}")
        return None

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
    
    /* Force bright green for secondary buttons (NEW GAME button) */
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="baseButton-secondary"]:focus,
    button[data-testid="baseButton-secondary"]:active {
        background: #00ff00 !important;
        background-color: #00ff00 !important;
        background-image: none !important;
        color: white !important;
        border: 3px solid #00ff00 !important;
        box-shadow: 0 0 20px rgba(0,255,0,0.4) !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    
    /* Target the specific NEW GAME button by key */
    button[key="new_game"],
    button[key="new_game"]:hover,
    button[key="new_game"]:focus,
    button[key="new_game"]:active {
        background: #00ff00 !important;
        background-color: #00ff00 !important;
        background-image: none !important;
        color: white !important;
        border: 3px solid #00ff00 !important;
        box-shadow: 0 0 20px rgba(0,255,0,0.4) !important;
        font-weight: bold !important;
        font-size: 18px !important;
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
                            result = make_move(row, col)
                            if result:
                                st.rerun()
                    else:
                        # Disabled empty cell
                        st.button("", key=f"disabled_{row}_{col}", disabled=True, use_container_width=True)
    
    # Single NEW GAME button - spans across the board
    if st.button("🔄 NEW GAME", key="new_game", help="Start a new game", type="secondary", use_container_width=True):
        st.session_state.board = [['', '', ''] for _ in range(3)]
        st.session_state.current_player = 'X'
        st.session_state.game_over = False
        st.session_state.winner = None
        st.session_state.move_history = []
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
                col1, col2, col3 = st.columns(3)
            
                with col1:
                    st.metric(
                        "Request Count",
                        metrics.get('request_count', 0)
                    )
                
                with col2:
                    st.metric(
                        "Avg Response Time",
                        f"{metrics.get('avg_response_time', 0):.3f}s"
                    )
                
                with col3:
                    st.metric(
                        "Memory Usage",
                        f"{metrics.get('memory_usage', 0):.2f} MB"
                    )
                
                # Show actual model name instead of generic "LLM"
                model_name = metrics.get('current_model', 'Unknown')
                if model_name == 'LLM' or model_name == 'Unknown':
                    # Try to get the actual model name from the metrics data
                    actual_model = metrics.get('model_name', metrics.get('llm_model', 'gpt-5-mini'))
                    st.markdown(f"**Current Model:** {actual_model}")
                else:
                    st.markdown(f"**Current Model:** {model_name}")
                st.markdown(f"**Timestamp:** {metrics.get('timestamp', 'Unknown')}")

def render_model_switching():
    """Render model switching interface"""
    st.markdown("### 🔄 Model Switching")
    
    agent_status = get_agent_status()
    if not agent_status:
        st.error("Failed to load agent status")
        return
    
    # Available models
    available_models = [
        "gpt-5",
        "gpt-5-mini", 
        "gpt-4",
        "llama3:latest",
        "llama3.2:3b"
    ]
    
    agents = ["scout", "strategist", "executor"]
    agent_names = {
        "scout": "🔍 Scout Agent",
        "strategist": "🧠 Strategist Agent",
        "executor": "⚡ Executor Agent"
    }
    
    for agent_id in agents:
        agent_data = agent_status.get(agent_id)
        if agent_data:
            # Get the actual model name, not generic "LLM"
            current_model = agent_data.get('current_model', 'Unknown')
            if current_model == 'LLM' or current_model == 'Unknown':
                # Try to get the actual model name from other fields
                actual_model = agent_data.get('model_name', agent_data.get('llm_model', 'gpt-5-mini'))
                current_model = actual_model
            
            with st.expander(f"{agent_names.get(agent_id, agent_id)} - Current: {current_model}", expanded=False):
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
                        st.error(f"Failed to switch {agent_id} model")

def main():
    """Main Streamlit app"""
    # Header
    st.markdown('<h1 class="mcp-header">🤖 Agentic Tic-Tac-Toe: MCP Protocol Showcase</h1>', unsafe_allow_html=True)
    st.markdown('<p class="mcp-sub-header">Watch three AI agents work together using CrewAI and MCP protocol!</p>', unsafe_allow_html=True)
    
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
            
            
            # Create two-column layout: Game Board (50%) and Player Moves (50%)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 🎮 Game Board")
                
                # Render game board
                render_game_board(board, game_over)
                
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
                
                # Show move history from current board state
                moves = []
                for row_idx, row in enumerate(board):
                    for col_idx, cell in enumerate(row):
                        if cell:
                            moves.append({
                                'symbol': cell,
                                'row': row_idx,
                                'col': col_idx
                            })
                
                if moves:
                    for i, move in enumerate(moves, 1):
                        symbol = move['symbol']
                        row = move['row']
                        col = move['col']
                        
                        if symbol == 'X':
                            st.write(f"{i}. 👤 You placed X at ({row}, {col})")
                        else:
                            st.write(f"{i}. 🤖 Double-O-AI placed O at ({row}, {col})")
                else:
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
