import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="MCP Multiplayer Game",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #00ff00;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 0 0 10px #00ff00;
    }
    .game-board {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 5px;
        max-width: 300px;
        margin: 0 auto;
    }
    .board-cell {
        width: 80px;
        height: 80px;
        background: #222;
        border: 2px solid #00ff00;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 36px;
        font-weight: bold;
        color: #00ff00;
        cursor: pointer;
    }
    .metric-card {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid #00ff00;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .agent-card {
        background: rgba(0, 255, 0, 0.05);
        border: 1px solid #00ff00;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = None
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

# API base URL
API_BASE = "http://localhost:8000"

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
            result = response.json()
            if result.get("success"):
                st.success(f"Successfully switched {agent} to {model_name}")
                return True
            else:
                st.error(f"Error switching model: {result.get('error')}")
                return False
        else:
            st.error(f"Error switching model: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error switching model: {e}")
        return False

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🎮 MCP Multiplayer Game</h1>', unsafe_allow_html=True)
    st.markdown("### Watch three AI agents work together using MCP protocol!")
    
    # Check if API is running
    try:
        health_response = requests.get(f"{API_BASE}/health")
        if health_response.status_code != 200:
            st.error("⚠️ API server is not running. Please start the server with: `python main.py`")
            st.stop()
    except:
        st.error("⚠️ Cannot connect to API server. Please start the server with: `python main.py`")
        st.stop()
    
    # Auto-refresh every 5 seconds
    if time.time() - st.session_state.last_refresh > 5:
        st.session_state.game_state = get_game_state()
        st.session_state.last_refresh = time.time()
    
    # Get current game state
    game_state = st.session_state.game_state or get_game_state()
    if game_state is None:
        st.error("Failed to load game state")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎮 Game", "🤖 Agents", "📡 MCP Logs", "📊 Metrics", "🔄 Models"])
    
    with tab1:
        st.header("Tic Tac Toe Game")
        
        # Game status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Move", game_state.get('move_number', 0))
        with col2:
            current_player = game_state.get('current_player', 'player')
            st.metric("Turn", f"{'👤 Player' if current_player == 'player' else '🤖 AI'}")
        with col3:
            if game_state.get('game_over'):
                winner = game_state.get('winner')
                if winner:
                    st.metric("Winner", f"{'👤 Player' if winner == 'player' else '🤖 AI'}")
                else:
                    st.metric("Result", "🤝 Draw")
            else:
                st.metric("Status", "🎮 Playing")
        
        # Game board
        st.subheader("Game Board")
        board = game_state.get('board', [['', '', ''], ['', '', ''], ['', '', '']])
        
        # Create game board with clickable cells
        for i in range(3):
            cols = st.columns(3)
            for j in range(3):
                with cols[j]:
                    cell_value = board[i][j]
                    if cell_value == '':
                        if st.button(f"Empty ({i},{j})", key=f"cell_{i}_{j}", 
                                   disabled=game_state.get('game_over', False) or current_player != 'player'):
                            if make_move(i, j):
                                st.success("Move made! AI is thinking...")
                                time.sleep(1)
                                ai_result = simulate_ai_turn()
                                if ai_result:
                                    st.success("AI has made its move!")
                                st.rerun()
                    else:
                        st.markdown(f"<div style='text-align: center; font-size: 2rem; color: #00ff00;'>{cell_value}</div>", 
                                  unsafe_allow_html=True)
        
        # Game controls
        st.subheader("Game Controls")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Game", use_container_width=True):
                if reset_game():
                    st.rerun()
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Move history
        st.subheader("Move History")
        game_history = game_state.get('game_history', [])
        if game_history:
            moves_df = pd.DataFrame(game_history)
            moves_df['Player'] = moves_df['player'].map({'player': '👤 Player', 'ai': '🤖 AI'})
            moves_df['Position'] = moves_df['position'].apply(lambda x: f"({x['row']},{x['col']})")
            moves_df['Display'] = moves_df.apply(lambda row: f"Move {row['move_number']}: {row['Player']} placed {row['position']['value']} at {row['Position']}", axis=1)
            for move in moves_df['Display'].tolist():
                st.write(move)
        else:
            st.info("No moves yet. Start the game by clicking any cell!")
    
    with tab2:
        st.header("AI Agents")
        agents_data = get_agents()
        if agents_data and agents_data.get('agents'):
            for agent_name, agent_info in agents_data['agents'].items():
                with st.expander(f"🤖 {agent_info.get('name', agent_name.upper())}", expanded=True):
                    st.write(f"**Role:** {agent_info.get('role', 'N/A')}")
                    st.write(f"**Model:** {agent_info.get('model', 'N/A')}")
                    st.write(f"**Status:** {agent_info.get('status', 'Active')}")
        else:
            st.info("No agent information available")
    
    with tab3:
        st.header("MCP Protocol Logs")
        mcp_logs = get_mcp_logs()
        if mcp_logs and mcp_logs.get('mcp_logs'):
            logs = mcp_logs['mcp_logs']
            for log in logs[-10:]:  # Show last 10 logs
                with st.expander(f"📡 {log['agent']} - {log['message_type']} ({log['timestamp']})"):
                    st.json(log['data'])
        else:
            st.info("No MCP logs yet. Play the game to see protocol in action!")
    
    with tab4:
        st.header("Game Metrics")
        metrics = get_metrics()
        if metrics:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("MCP Messages", metrics.get('mcp_message_count', 0))
            with col2:
                st.metric("Total Cost", f"${metrics.get('total_cost', 0):.6f}")
            with col3:
                st.metric("Game Duration", f"{metrics.get('game_duration_seconds', 0):.1f}s")
            with col4:
                avg_response = metrics.get('avg_response_times', {})
                if avg_response:
                    avg = sum(avg_response.values()) / len(avg_response)
                    st.metric("Avg Response", f"{avg:.2f}ms")
                else:
                    st.metric("Avg Response", "0ms")
            
            # LLM Cost Breakdown
            st.subheader("LLM Cost Breakdown")
            costs = metrics.get('llm_costs', {})
            if costs:
                cost_df = pd.DataFrame([
                    {"LLM": "GPT-4", "Cost": costs.get('gpt4', 0)},
                    {"LLM": "Claude", "Cost": costs.get('claude', 0)},
                    {"LLM": "Llama2", "Cost": costs.get('llama', 0)}
                ])
                st.bar_chart(cost_df.set_index('LLM'))
            
            # Agent Response Times
            st.subheader("Agent Response Times")
            response_times = metrics.get('avg_response_times', {})
            if response_times:
                response_df = pd.DataFrame([
                    {"Agent": "Scout", "Time (ms)": response_times.get('scout', 0)},
                    {"Agent": "Strategist", "Time (ms)": response_times.get('strategist', 0)},
                    {"Agent": "Executor", "Time (ms)": response_times.get('executor', 0)}
                ])
                st.bar_chart(response_df.set_index('Agent'))
        else:
            st.info("No metrics available yet")
    
    with tab5:
        st.header("Hot-Swappable LLM Models")
        models_data = get_models()
        if models_data:
            current_models = models_data.get('current_models', {})
            models = models_data.get('models', {})
            
            # Model switching interface
            for agent_name in ['scout', 'strategist', 'executor']:
                st.subheader(f"{'🔍' if agent_name == 'scout' else '🧠' if agent_name == 'strategist' else '⚡'} {agent_name.title()} Agent")
                current_model = current_models.get(agent_name, 'Unknown')
                st.write(f"**Current Model:** {current_model}")
                
                # Model selection
                available_models = []
                for model_name, model_info in models.items():
                    if model_info.get('is_available', False):
                        cost = model_info.get('estimated_cost_per_1k_tokens', 0)
                        display_name = f"{model_info.get('display_name', model_name)} (${cost:.6f}/1K tokens)"
                        available_models.append((display_name, model_name))
                
                if available_models:
                    selected_model = st.selectbox(
                        f"Select model for {agent_name}",
                        options=[m[1] for m in available_models],
                        format_func=lambda x: next(m[0] for m in available_models if m[1] == x),
                        key=f"model_select_{agent_name}"
                    )
                    
                    if st.button(f"Switch {agent_name} to {selected_model}", key=f"switch_{agent_name}"):
                        if switch_model(agent_name, selected_model):
                            st.rerun()
                else:
                    st.warning("No available models")
        else:
            st.info("No model information available")

if __name__ == "__main__":
    main() 