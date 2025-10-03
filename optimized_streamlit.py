#!/usr/bin/env python3
"""
Optimized Streamlit UI for the optimized local mode
Connects to main_optimized.py backend
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, List, Optional

# Configure Streamlit
st.set_page_config(
    page_title="Optimized Tic Tac Toe",
    page_icon="🎮",
    layout="wide"
)

# API base URL
API_BASE = "http://localhost:8000"

def make_request(endpoint: str, method: str = "GET", data: dict = None) -> Optional[dict]:
    """Make API request with error handling"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            return None
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {e}")
        return None

def check_backend_health() -> bool:
    """Check if backend is running"""
    health = make_request("/health")
    if health:
        st.success(f"✅ Backend connected: {health.get('architecture', 'Unknown')}")
        return True
    else:
        st.error("❌ Backend offline - Cannot connect to optimized API")
        st.info("Make sure to run: python main_optimized.py")
        return False

def start_new_game():
    """Start a new game"""
    result = make_request("/game/new", "POST")
    if result and result.get("success"):
        # Calculate move count from board
        move_count = sum(1 for row in result["board"] for cell in row if cell != "")
        st.session_state.game_state = {
            **result,
            "move_count": move_count
        }
        st.session_state.game_over = False
        st.rerun()
    else:
        st.error("Failed to start new game")

def make_move(row: int, col: int, player: str = "X"):
    """Make a player move"""
    result = make_request("/game/move", "POST", {
        "row": row,
        "col": col,
        "player": player
    })
    return result

def get_ai_move():
    """Get AI move"""
    result = make_request("/game/ai-move", "POST")
    return result

def check_winner(board: List[List[str]]) -> Optional[str]:
    """Check for winner"""
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] != "":
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "":
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    
    return None

def render_board(board: List[List[str]], game_over: bool = False):
    """Render the Tic Tac Toe board"""
    cols = st.columns(3)
    
    for i in range(3):
        with cols[i]:
            for j in range(3):
                cell_value = board[i][j] if board[i][j] else ""
                if st.button(
                    cell_value or " ", 
                    key=f"cell_{i}_{j}",
                    disabled=cell_value != "" or game_over,
                    use_container_width=True
                ):
                    # Make player move
                    result = make_move(i, j)
                    if result and result.get('success'):
                        # Update session state with player move
                        move_count = sum(1 for row in result["board"] for cell in row if cell != "")
                        st.session_state.game_state = {
                            "board": result["board"],
                            "current_player": result["current_player"],
                            "game_over": result["game_over"],
                            "winner": result.get("winner"),
                            "move_count": move_count
                        }
                        
                        # Show player move first, then trigger AI move
                        st.success("✅ Your move recorded!")
                        st.rerun()  # Show player move first
                        
                        # Check if AI should move (this will happen after rerun)
                        if not result.get('game_over', False) and result.get('current_player') == 'O':
                            # Set flag to trigger AI move on next render
                            st.session_state.trigger_ai_move = True
                    else:
                        st.error("Invalid move!")

def main():
    """Main Streamlit app"""
    
    # Title
    st.title("🎮 Optimized Tic Tac Toe")
    st.subheader("Shared Resources • < 1 Second Per Move • No MCP Servers")
    
    # Check backend health
    if not check_backend_health():
        st.stop()
    
    # Initialize game state
    if 'game_state' not in st.session_state:
        start_new_game()
    
    game_state = st.session_state.game_state
    
    # Handle AI move trigger
    if st.session_state.get('trigger_ai_move', False):
        st.session_state.trigger_ai_move = False  # Reset flag
        
        with st.spinner("🤖 AI is thinking..."):
            start_time = time.time()
            ai_result = get_ai_move()
            duration = time.time() - start_time
        
        if ai_result and ai_result.get('success'):
            st.success(f"✅ AI move completed in {duration:.3f}s")
            # Update session state with AI move
            move_count = sum(1 for row in ai_result["board"] for cell in row if cell != "")
            st.session_state.game_state = {
                "board": ai_result["board"],
                "current_player": ai_result["current_player"],
                "game_over": ai_result["game_over"],
                "winner": ai_result.get("winner"),
                "move_count": move_count
            }
            st.rerun()
        else:
            st.error(f"❌ AI move failed after {duration:.3f}s")
            if ai_result:
                st.error(f"Error: {ai_result.get('error', 'Unknown error')}")
    
    # Calculate move count from board
    move_count = sum(1 for row in game_state['board'] for cell in row if cell != "")
    
    # Check for game over state
    game_over = game_state.get('game_over', False)
    if not game_over:
        # Check if board is full (9 moves)
        game_over = move_count >= 9
        # Check for winner
        winner = check_winner(game_state['board'])
        if winner:
            game_over = True
    
    # Display game info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Current Player:** {game_state['current_player']}")
    with col2:
        st.write(f"**Moves Made:** {move_count}")
    with col3:
        status = "Game Over" if game_over else "Playing"
        st.write(f"**Status:** {status}")
    
    # New Game button
    if st.button("🔄 New Game", type="primary"):
        start_new_game()
        st.rerun()
    
    st.subheader("Game Board")
    render_board(game_state['board'], game_over)
    
    # Game over message
    if game_over:
        st.session_state.game_over = True
        winner = game_state.get('winner')
        if not winner:
            winner = check_winner(game_state['board'])
        
        if winner == "draw" or (not winner and move_count >= 9):
            st.info("🤝 It's a Draw!")
        elif winner:
            st.success(f"🎉 Player {winner} wins!")
        else:
            st.error("Game Over with no winner?")
    
    # Informational message
    if not game_over and game_state['current_player'] == 'X':
        st.info("👉 Make your move!")
    elif not game_over and game_state['current_player'] == 'O':
        st.info("🤖 AI is thinking...")
    
    # Performance info
    with st.expander("🚀 Performance Info"):
        perf = make_request("/performance")
        if perf:
            st.write(f"**Architecture:** {perf.get('architecture', 'Unknown')}")
            st.write(f"**Expected Speed:** {perf.get('expected_speed', 'Unknown')}")
            st.write(f"**Complexity:** {perf.get('complexity', 'Unknown')}")
            st.write(f"**LLM Calls per Move:** {perf.get('llm_calls_per_move', 'Unknown')}")
            st.write(f"**Overhead:** {perf.get('overhead', 'Unknown')}")
            
            benefits = perf.get('benefits', [])
            if benefits:
                st.write("**Benefits:**")
                for benefit in benefits:
                    st.write(f"• {benefit}")
    
    # Agent status
    with st.expander("🤖 Agent Status"):
        status = make_request("/agents/status")
        if status:
            st.write(f"**Mode:** {status.get('mode', 'Unknown')}")
            st.write(f"**Coordinator:** {status.get('coordinator', 'Unknown')}")
            st.write(f"**Transport:** {status.get('transport', 'Unknown')}")
            
            agents = status.get('agents', {})
            if agents:
                st.write("**Agents:**")
                for agent, info in agents.items():
                    st.write(f"• **{agent.title()}:** {info}")

if __name__ == "__main__":
    main()
