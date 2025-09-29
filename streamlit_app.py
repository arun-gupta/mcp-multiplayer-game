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

def render_game_board(board):
    """Render the Tic Tac Toe board with proper styling"""
    
    # Add custom CSS for game board styling
    st.markdown("""
    <style>
    .game-board-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Create the game board using Streamlit columns
    st.markdown('<div class="game-board-container">', unsafe_allow_html=True)
    
    # Create 3x3 grid using Streamlit columns
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            with cols[col]:
                cell_value = board[row][col] if board[row][col] else ""
                if cell_value:
                    # Filled cell - display as styled div
                    st.markdown(f"""
                    <div class="game-cell filled" style="margin: 0 auto; display: flex; align-items: center; justify-content: center; width: 80px; height: 80px; border: 2px solid #00ff88; border-radius: 8px; background-color: #00ff88; color: #000; font-size: 28px; font-weight: bold; box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);">
                        {cell_value}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Empty cell - clickable button
                    if st.button(
                        " ",
                        key=f"move_{row}_{col}",
                        help=f"Click to place X at ({row}, {col})",
                        use_container_width=True
                    ):
                        # Make the move
                        result = make_move(row, col)
                        if result:
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
                    st.markdown(f"**Model:** {agent_data.get('current_model', 'Unknown')}")
                    st.markdown(f"**MCP Port:** {agent_data.get('mcp_port', 'Unknown')}")
                    st.markdown(f"**Memory Size:** {agent_data.get('memory_size', 0)}")
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
                
                st.markdown(f"**Current Model:** {metrics.get('current_model', 'Unknown')}")
                st.markdown(f"**Timestamp:** {metrics.get('timestamp', 'Unknown')}")

def render_model_switching():
    """Render model switching interface"""
                        st.markdown("### 🔄 Model Switching")
                        
    agent_status = get_agent_status()
    if not agent_status:
        st.error("Failed to load agent status")
        return
    
    # Available models (mock data for now)
    available_models = [
        "gpt-4",
        "gpt-3.5-turbo", 
        "claude-3-sonnet",
        "claude-3-haiku",
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
            current_model = agent_data.get('current_model', 'Unknown')
            
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
                render_game_board(board)
                
                # Add New Game button below the game board
                # NEW GAME button
                if st.button("🔄 NEW GAME", use_container_width=True, type="primary"):
                    result = reset_game()
                    if result:
                        st.success("Game reset successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to reset game")
            
            with col2:
                st.markdown("### 📝 Player Moves")
                
                # Show move history
                if 'move_history' in game_state:
                    move_history = game_state.get('move_history', [])
                    if move_history:
                        for i, move in enumerate(move_history, 1):
                            player = move.get('player', 'Unknown')
                            position = move.get('position', {})
                            row = position.get('row', '?')
                            col = position.get('col', '?')
                            st.write(f"**Move {i}:** {player} at ({row}, {col})")
                            else:
                        st.info("No moves yet")
                    else:
                    st.info("Move history not available")
                
                # Show game statistics
                st.markdown("---")
                st.markdown("### 📊 Game Statistics")
                
                if move_number > 0:
                    st.write(f"**Total Moves:** {move_number}")
                    if game_over:
                        if winner:
                            st.success(f"🎉 **Winner:** {winner}")
                            else:
                            st.info("🤝 **Game Over:** It's a draw!")
                    else:
                        st.info("🔄 **Game in Progress**")
                    else:
                    st.info("🎮 **Ready to Start**")
                else:
            st.error("Failed to load game state")
    
    with tab2:
        st.markdown("### 🤖 MCP Agent Status")
        
        # Get agent status
        agent_status = get_agent_status()
        if agent_status:
            render_agent_status(agent_status)
        else:
            st.error("Failed to load agent status")
    
    with tab3:
        st.markdown("### 📡 MCP Protocol Communication")
        
        # Get MCP logs
        logs_data = get_mcp_logs()
        if logs_data:
            render_mcp_logs(logs_data)
                    else:
            st.error("Failed to load MCP logs")
    
    with tab4:
        st.markdown("### 📊 Performance Analytics")
        
        # Agent metrics
        render_agent_metrics()
    
    with tab5:
        st.markdown("### ⚙️ MCP Configuration")
        
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
