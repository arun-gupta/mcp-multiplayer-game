"""
Executor Agent Module
Executes strategic plans for Tic Tac Toe moves
"""
import os
import time
from crewai import Agent
from models.factory import ModelFactory
from models.registry import model_registry
from schemas.plan import Plan
from schemas.action_result import ActionResult, MoveResult
from schemas.observation import BoardPosition

class ExecutorAgent:
    """Executor agent that executes strategic plans"""
    
    def __init__(self, game_state, model_name: str = "mistral-latest"):
        self.game_state = game_state
        self.model_name = model_name
        self.llm = self._create_llm(model_name)
        
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
    
    def _create_llm(self, model_name: str):
        """Create LLM instance for the specified model"""
        llm = ModelFactory.create_llm(model_name)
        if llm is None:
            # Fallback to default model
            print(f"Warning: Could not create LLM for {model_name}, falling back to mistral-latest")
            llm = ModelFactory.create_llm("mistral-latest")
        return llm
    
    def switch_model(self, model_name: str):
        """Switch to a different model"""
        new_llm = self._create_llm(model_name)
        if new_llm:
            self.llm = new_llm
            self.model_name = model_name
            # Update the agent's LLM
            self.agent.llm = new_llm
            # Update game state
            self.game_state.set_agent_model("executor", model_name)
            return True
        return False
    
    def execute_plan(self, plan: Plan) -> ActionResult:
        """Execute the strategic plan by making a move"""
        try:
            import psutil
            start_time = time.time()
            
            # Track MCP metrics
            self.game_state.increment_mcp_messages()
            self.game_state.add_message_flow_pattern("executor_to_scout")
            
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
            
            # Track response time and other metrics
            response_time = execution_time * 1000  # Convert to milliseconds
            self.game_state.add_response_time("executor", response_time)
            self.game_state.add_message_latency(response_time)
            
            # Add estimated cost and token usage (Llama pricing - free)
            estimated_cost = 0.0  # Llama is free
            estimated_tokens = 50  # Rough estimate per execution
            self.game_state.add_llm_cost("llama", estimated_cost)
            self.game_state.add_token_usage("executor", estimated_tokens)
            
            # Update resource utilization
            try:
                cpu_percent = psutil.cpu_percent()
                memory_mb = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB
                self.game_state.update_resource_utilization(cpu_percent, memory_mb)
            except:
                pass  # Ignore if psutil is not available
            
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
        model_config = model_registry.get_model(self.model_name)
        model_display = model_config.display_name if model_config else self.model_name
        provider = model_config.provider if model_config else "Unknown"
        
        # Determine provider type and icon
        provider_str = str(provider).upper()
        if "OPENAI" in provider_str or "ANTHROPIC" in provider_str:
            provider_type = "☁️ Cloud"
            provider_icon = "☁️"
        elif "OLLAMA" in provider_str:
            provider_type = "🖥️ Local"
            provider_icon = "🖥️"
        else:
            provider_type = "❓ Unknown"
            provider_icon = "❓"
        
        return {
            "name": "Executor Agent",
            "role": "Move Executor",
            "model": model_display,
            "model_name": self.model_name,
            "provider": provider,
            "provider_type": provider_type,
            "provider_icon": provider_icon,
            "description": "Executes strategic plans by making board moves",
            "capabilities": ["Plan Execution", "Move Validation", "Board Updates", "Game State Management"]
        } 