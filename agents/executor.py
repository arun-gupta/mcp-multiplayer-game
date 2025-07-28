"""
Executor Agent Module
Executes strategic plans for Rock-Paper-Scissors moves
"""
import os
import time
from crewai import Agent
from langchain_community.llms import Ollama
from schemas.plan import Plan
from schemas.action_result import ActionResult, MoveResult
from game.state import RPSGameState

class ExecutorAgent:
    """Executor agent that executes strategic plans"""
    
    def __init__(self, game_state: RPSGameState):
        self.game_state = game_state
        
        # Initialize LLM (Ollama Llama2:7B)
        try:
            self.llm = Ollama(
                model="llama2:7b",
                temperature=0.1
            )
        except Exception as e:
            print(f"Warning: Could not initialize Ollama LLM: {e}")
            self.llm = None
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Game Executor",
            goal="Execute strategic plans by making the optimal Rock-Paper-Scissors move",
            backstory="""You are an expert Rock-Paper-Scissors executor with perfect execution skills.
            Your job is to take the strategist's plan and execute it flawlessly by making the chosen move.
            You focus on:
            - Following the strategist's recommendations
            - Executing moves with confidence
            - Adapting if the primary strategy fails
            - Maintaining consistency with the overall game plan""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def execute_plan(self, plan: Plan) -> ActionResult:
        """Execute the strategic plan and return the result"""
        try:
            start_time = time.time()
            
            # Get the move to execute
            move = plan.primary_strategy.move
            confidence = plan.primary_strategy.confidence
            
            # Generate opponent's move
            opponent_move = self.game_state.generate_opponent_move()
            
            # Determine the result
            result = self.game_state.determine_winner(move, opponent_move)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create move result
            move_result = MoveResult(
                move=move,
                opponent_move=opponent_move,
                result=result,
                confidence=confidence,
                execution_time=execution_time
            )
            
            # Determine score change
            score_change = 0
            if result == "win":
                score_change = 1
            elif result == "lose":
                score_change = -1
            
            # Create action result
            action_result = ActionResult(
                round_number=plan.round_number,
                plan_id=plan.plan_id,
                move_executed=move_result,
                strategy_followed="primary",
                success=True,
                message=f"Successfully executed {move} against opponent's {opponent_move} - {result}",
                score_change=score_change,
                game_continues=len(self.game_state.game_history) < self.game_state.max_rounds
            )
            
            return action_result
            
        except Exception as e:
            print(f"Error in ExecutorAgent.execute_plan: {e}")
            # Return a fallback result
            return self._create_fallback_result(plan)
    
    def _create_fallback_result(self, plan: Plan) -> ActionResult:
        """Create a fallback result if execution fails"""
        # Default to rock if execution fails
        move = "rock"
        opponent_move = self.game_state.generate_opponent_move()
        result = self.game_state.determine_winner(move, opponent_move)
        
        move_result = MoveResult(
            move=move,
            opponent_move=opponent_move,
            result=result,
            confidence=0.1,
            execution_time=0.1
        )
        
        score_change = 0
        if result == "win":
            score_change = 1
        elif result == "lose":
            score_change = -1
        
        return ActionResult(
            round_number=plan.round_number,
            plan_id=plan.plan_id,
            move_executed=move_result,
            strategy_followed="fallback",
            success=False,
            message=f"Fallback execution: {move} vs {opponent_move} - {result}",
            score_change=score_change,
            game_continues=len(self.game_state.game_history) < self.game_state.max_rounds
        )
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "Executor Agent",
            "role": "Move Executor",
            "model": "Ollama Llama2:7B",
            "description": "Executes strategic plans by making moves",
            "capabilities": ["Plan Execution", "Move Selection", "Result Analysis", "Adaptive Execution"]
        } 