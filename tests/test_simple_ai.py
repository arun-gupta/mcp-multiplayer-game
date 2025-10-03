#!/usr/bin/env python3
"""
Simple Tic Tac Toe AI implementation - should be < 1 second
This bypasses all the complex CrewAI/MCP architecture
"""

import asyncio
import json
import time
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class SimpleTicTacToeAI:
    """Simple AI that makes moves in < 1 second"""
    
    def __init__(self, model="gpt-5-mini"):
        self.model = model
        try:
            if "gpt" in model.lower():
                self.llm = ChatOpenAI(model=model, timeout=5.0)
            elif "claude" in model.lower():
                self.llm = ChatAnthropic(model=model, timeout=5.0)
            else:
                # Fallback to OpenAI
                self.llm = ChatOpenAI(model="gpt-5-mini", timeout=5.0)
        except Exception as e:
            # Silently fallback to Ollama - this is expected when no API keys are set
            from langchain_community.llms import Ollama
            self.llm = Ollama(model="llama3.2:1b", timeout=10.0)
            self.model = "llama3.2:1b"  # Update model name to reflect actual usage
    
    def format_board(self, board: List[List[str]]) -> str:
        """Format board for display"""
        result = []
        for i, row in enumerate(board):
            row_str = " | ".join([cell if cell else '_' for cell in row])
            result.append(f"Row {i}: {row_str}")
        return "\n".join(result)
    
    def get_available_moves(self, board: List[List[str]]) -> List[Dict]:
        """Get available moves"""
        moves = []
        for i in range(3):
            for j in range(3):
                if board[i][j] == "":
                    moves.append({"row": i, "col": j})
        return moves
    
    def check_winner(self, board: List[List[str]]) -> Optional[str]:
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
    
    def find_immediate_win(self, board: List[List[str]], player: str) -> Optional[Dict]:
        """Find immediate winning move"""
        for i in range(3):
            for j in range(3):
                if board[i][j] == "":
                    # Test this move
                    board[i][j] = player
                    winner = self.check_winner(board)
                    board[i][j] = ""  # Reset
                    
                    if winner == player:
                        return {"row": i, "col": j}
        return None
    
    def find_blocking_move(self, board: List[List[str]], opponent: str) -> Optional[Dict]:
        """Find move to block opponent"""
        return self.find_immediate_win(board, opponent)
    
    async def get_move(self, board: List[List[str]], player: str = "O") -> Dict:
        """Get AI move - should be < 1 second"""
        start_time = time.time()
        
        # First, check for immediate wins or blocks
        opponent = "X" if player == "O" else "O"
        
        # Check for immediate win
        win_move = self.find_immediate_win(board, player)
        if win_move:
            duration = time.time() - start_time
            print(f"✅ Immediate win found in {duration:.3f}s")
            return win_move
        
        # Check for blocking move
        block_move = self.find_blocking_move(board, opponent)
        if block_move:
            duration = time.time() - start_time
            print(f"✅ Blocking move found in {duration:.3f}s")
            return block_move
        
        # Use LLM for strategic positioning
        available_moves = self.get_available_moves(board)
        if not available_moves:
            return {"row": 1, "col": 1}  # Fallback
        
        # Simple prompt optimized for Ollama
        prompt = f"""Tic Tac Toe board:
{self.format_board(board)}

You are {player}. Choose best move from: {available_moves}

IMPORTANT: Respond with ONLY a JSON object like this: {{"row": 0, "col": 1}}
Do not include any other text, just the JSON."""
        
        try:
            # Single LLM call
            response = await self.llm.ainvoke(prompt)
            
            # Parse response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Clean up the response to extract JSON
            content = content.strip()
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{[^}]*"row"[^}]*"col"[^}]*\}', content)
            if json_match:
                content = json_match.group()
            
            try:
                move = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract coordinates from text
                import re
                coords = re.findall(r'(\d+),(\d+)', content)
                if coords:
                    row, col = map(int, coords[0])
                    move = {"row": row, "col": col}
                else:
                    # Fallback to center
                    move = {"row": 1, "col": 1}
            
            # Validate move
            if move in available_moves:
                duration = time.time() - start_time
                print(f"✅ LLM move in {duration:.3f}s")
                return move
            else:
                # Invalid move, use first available
                duration = time.time() - start_time
                print(f"⚠️ Invalid LLM move, using fallback in {duration:.3f}s")
                return available_moves[0]
            
        except Exception as e:
            print(f"❌ LLM error: {e}")
            # Fallback to center or first available
            center = {"row": 1, "col": 1}
            if center in available_moves:
                return center
            else:
                return available_moves[0]

class SimpleGame:
    """Simple Tic Tac Toe game with fast AI"""
    
    def __init__(self, ai_model="gpt-5-mini"):
        self.board = [["", "", ""], ["", "", ""], ["", "", ""]]
        self.ai = SimpleTicTacToeAI(ai_model)
        self.current_player = "X"  # Human starts
    
    def make_move(self, row: int, col: int, player: str) -> bool:
        """Make a move"""
        if self.board[row][col] != "":
            return False
        
        self.board[row][col] = player
        return True
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        # Check for winner
        winner = self.ai.check_winner(self.board)
        if winner:
            return True
        
        # Check for draw
        for row in self.board:
            for cell in row:
                if cell == "":
                    return False
        return True
    
    def get_winner(self) -> Optional[str]:
        """Get winner"""
        return self.ai.check_winner(self.board)
    
    async def ai_move(self) -> Dict:
        """Get AI move"""
        return await self.ai.get_move(self.board)

async def test_simple_ai():
    """Test the simple AI"""
    
    print("🧪 Testing Simple Tic Tac Toe AI")
    print("=" * 50)
    
    game = SimpleGame()
    
    # Test scenario: Human plays X at (0,0), AI should block
    print("📋 Initial board:")
    print(game.ai.format_board(game.board))
    
    # Human move
    game.make_move(0, 0, "X")
    print(f"\n👤 Human plays X at (0,0)")
    print(game.ai.format_board(game.board))
    
    # AI move
    print(f"\n🤖 AI thinking...")
    ai_move = await game.ai_move()
    game.make_move(ai_move["row"], ai_move["col"], "O")
    print(f"🤖 AI plays O at ({ai_move['row']},{ai_move['col']})")
    print(game.ai.format_board(game.board))
    
    # Check game state
    if game.is_game_over():
        winner = game.get_winner()
        if winner:
            print(f"\n🎉 Winner: {winner}")
        else:
            print(f"\n🤝 Draw!")

if __name__ == "__main__":
    asyncio.run(test_simple_ai())
