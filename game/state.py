"""
Game State Module
Manages the overall game state, turn management, and game progression
"""
import random
from datetime import datetime
from typing import List, Dict, Any
from schemas.observation import Observation, GameHistory
from schemas.action_result import ActionResult, MoveResult

class RPSGameState:
    """Manages the state of a Rock-Paper-Scissors game"""
    
    def __init__(self):
        self.current_round = 0
        self.player_score = 0
        self.opponent_score = 0
        self.game_history: List[GameHistory] = []
        self.max_rounds = 10
        self.game_mode = "tournament"
        self.game_over = False
        self.winner = None
        
    def initialize_new_game(self):
        """Start a new game"""
        self.current_round = 0
        self.player_score = 0
        self.opponent_score = 0
        self.game_history = []
        self.game_over = False
        self.winner = None
        
    def get_observation(self) -> Observation:
        """Get current game state for the Scout agent"""
        last_opponent_moves = [h.opponent_move for h in self.game_history[-5:]]
        
        # Determine current streak
        if len(self.game_history) == 0:
            current_streak = "neutral"
        else:
            last_result = self.game_history[-1].result
            if last_result == "win":
                current_streak = "winning"
            elif last_result == "lose":
                current_streak = "losing"
            else:
                current_streak = "drawing"
        
        return Observation(
            current_round=self.current_round + 1,  # Next round
            player_score=self.player_score,
            opponent_score=self.opponent_score,
            game_history=self.game_history,
            last_opponent_moves=last_opponent_moves,
            total_rounds_played=len(self.game_history),
            current_streak=current_streak,
            game_mode=self.game_mode,
            max_rounds=self.max_rounds
        )
        
    def generate_opponent_move(self) -> str:
        """Generate the opponent's move (AI opponent)"""
        # Simple AI: sometimes follows patterns, sometimes random
        if len(self.game_history) >= 3:
            # 30% chance to counter the player's most common move
            player_moves = [h.player_move for h in self.game_history[-3:]]
            if player_moves.count(player_moves[0]) >= 2:
                # Player seems to favor one move, counter it
                if random.random() < 0.3:
                    if player_moves[0] == "rock":
                        return "paper"
                    elif player_moves[0] == "paper":
                        return "scissors"
                    else:
                        return "rock"
        
        # Default to random
        return random.choice(["rock", "paper", "scissors"])
        
    def determine_winner(self, player_move: str, opponent_move: str) -> str:
        """Determine the winner of a round"""
        if player_move == opponent_move:
            return "draw"
        
        winning_combinations = {
            ("rock", "scissors"): "win",
            ("paper", "rock"): "win", 
            ("scissors", "paper"): "win"
        }
        
        return winning_combinations.get((player_move, opponent_move), "lose")
        
    def update_from_result(self, result: ActionResult) -> Dict[str, Any]:
        """Update game state from execution result"""
        move_result = result.move_executed
        
        # Create game history entry
        history_entry = GameHistory(
            round_number=result.round_number,
            player_move=move_result.move,
            opponent_move=move_result.opponent_move,
            result=move_result.result,
            timestamp=datetime.now().isoformat()
        )
        
        self.game_history.append(history_entry)
        
        # Update scores
        if move_result.result == "win":
            self.player_score += 1
        elif move_result.result == "lose":
            self.opponent_score += 1
        
        # Check if game is over
        if len(self.game_history) >= self.max_rounds:
            self.game_over = True
            if self.player_score > self.opponent_score:
                self.winner = "player"
            elif self.opponent_score > self.player_score:
                self.winner = "opponent"
            else:
                self.winner = "tie"
        
        return {
            "round_number": result.round_number,
            "player_score": self.player_score,
            "opponent_score": self.opponent_score,
            "last_move": {
                "player": move_result.move,
                "opponent": move_result.opponent_move,
                "result": move_result.result
            },
            "game_over": self.game_over,
            "winner": self.winner,
            "rounds_remaining": max(0, self.max_rounds - len(self.game_history))
        }
        
    def get_state_for_api(self) -> Dict[str, Any]:
        """Get formatted state for API response"""
        return {
            "game_state": {
                "current_round": self.current_round + 1,
                "player_score": self.player_score,
                "opponent_score": self.opponent_score,
                "game_over": self.game_over,
                "winner": self.winner,
                "max_rounds": self.max_rounds,
                "rounds_remaining": max(0, self.max_rounds - len(self.game_history))
            },
            "game_history": [h.dict() for h in self.game_history],
            "recent_moves": [h.dict() for h in self.game_history[-5:]],
            "statistics": {
                "total_rounds": len(self.game_history),
                "player_wins": sum(1 for h in self.game_history if h.result == "win"),
                "opponent_wins": sum(1 for h in self.game_history if h.result == "lose"),
                "draws": sum(1 for h in self.game_history if h.result == "draw")
            }
        } 