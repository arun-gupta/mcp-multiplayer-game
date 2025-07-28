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
from schemas.observation import BoardPosition

class ExecutorAgent:
    """Executor agent that executes strategic plans"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.llm = Ollama(
            model="llama2:7b",
            temperature=0.1
        )
        
        self.agent = Agent(
            role="Game Executor",
            goal="Execute strategic plans by making optimal Tic Tac Toe moves",
            backstory="""You are an expert Tic Tac Toe executor with perfect execution skills.
            Your job is to take the strategist's plan and execute it flawlessly by making the chosen move.
            You focus on:
            - Following the strategist's recommendations precisely
            - Executing moves with confidence and accuracy
            - Validating move legality before execution
            - Adapting if the primary strategy fails
            - Maintaining consistency with the overall game plan
            - Ensuring proper board state updates""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def execute_plan(self, plan: Plan) -> ActionResult:
        """Execute the strategic plan by making a move"""
        try:
            start_time = time.time()
            
            # Validate the plan
            if not self._validate_plan(plan):
                return self._create_error_result(plan, "Invalid plan - no valid moves available")
            
            # Execute the primary strategy
            primary_move = plan.primary_strategy.position
            success = self.game_state.make_move(primary_move.row, primary_move.col, "ai")
            
            if not success:
                # Try alternative strategies
                for alt_strategy in plan.alternative_strategies:
                    alt_move = alt_strategy.position
                    if self.game_state.make_move(alt_move.row, alt_move.col, "ai"):
                        primary_move = alt_move
                        success = True
                        break
            
            execution_time = time.time() - start_time
            
            if not success:
                return self._create_error_result(plan, "Failed to execute any strategy")
            
            # Create move result
            move_result = MoveResult(
                position=primary_move,
                move_type=plan.primary_strategy.move_type,
                success=True,
                execution_time=execution_time
            )
            
            # Create action result
            return ActionResult(
                move_number=plan.move_number,
                plan_id=plan.plan_id,
                move_executed=move_result,
                strategy_followed=plan.primary_strategy.move_type,
                success=True,
                message=f"Successfully executed {plan.primary_strategy.move_type} move at position ({primary_move.row}, {primary_move.col})",
                new_board_state=self.game_state.board,
                game_over=self.game_state.game_over,
                winner=self.game_state.winner,
                next_player=self.game_state.current_player
            )
            
        except Exception as e:
            print(f"Error in ExecutorAgent.execute_plan: {e}")
            return self._create_error_result(plan, f"Execution error: {str(e)}")
    
    def _validate_plan(self, plan: Plan) -> bool:
        """Validate that the plan contains valid moves"""
        if not plan.primary_strategy or not plan.primary_strategy.position:
            return False
        
        # Check if the primary move is valid
        pos = plan.primary_strategy.position
        if not self._is_valid_move(pos.row, pos.col):
            return False
        
        # Check if any alternative moves are valid
        for alt_strategy in plan.alternative_strategies:
            if alt_strategy.position and self._is_valid_move(alt_strategy.position.row, alt_strategy.position.col):
                return True
        
        return True
    
    def _is_valid_move(self, row: int, col: int) -> bool:
        """Check if a move is valid (within bounds and empty)"""
        if row < 0 or row >= 3 or col < 0 or col >= 3:
            return False
        return self.game_state.board[row][col] == ""
    
    def _create_error_result(self, plan: Plan, error_message: str) -> ActionResult:
        """Create an error result when execution fails"""
        return ActionResult(
            move_number=plan.move_number,
            plan_id=plan.plan_id,
            move_executed=MoveResult(
                position=BoardPosition(row=0, col=0, value=""),
                move_type="error",
                success=False,
                execution_time=0.0,
                validation_errors=[error_message]
            ),
            strategy_followed="error",
            success=False,
            message=error_message,
            new_board_state=self.game_state.board,
            game_over=self.game_state.game_over,
            winner=self.game_state.winner,
            next_player=self.game_state.current_player
        )
    
    def get_agent_info(self) -> dict:
        """Get information about this agent"""
        return {
            "name": "Executor Agent",
            "role": "Move Executor",
            "model": "Ollama Llama2:7B",
            "description": "Executes strategic plans by making board moves",
            "capabilities": ["Plan Execution", "Move Validation", "Board Updates", "Game State Management"]
        } 