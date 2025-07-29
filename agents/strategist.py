"""
Strategist Agent Module
Analyzes scout observations and creates strategic plans for Tic Tac Toe
"""
import os
from crewai import Agent
from models.factory import ModelFactory
from models.registry import model_registry
from schemas.observation import Observation
from schemas.plan import Plan, Strategy
from schemas.observation import BoardPosition
import uuid

class StrategistAgent:
    """Strategist agent that creates plans based on game observations"""
    
    def __init__(self, game_state=None, model_name: str = "llama3-latest"):
        self.game_state = game_state
        self.model_name = model_name
        self.llm = self._create_llm(model_name)
        
        self.agent = Agent(
            role="Game Strategist",
            goal="Analyze game observations and create optimal strategies for Tic Tac Toe",
            backstory="""You are an expert Tic Tac Toe strategist with deep understanding of:
            - Board position analysis and strategic planning
            - Threat detection and blocking strategies
            - Opening, midgame, and endgame tactics
            - Pattern recognition and opponent behavior analysis
            - Optimal move selection based on game state
            
            Your job is to analyze the scout's observations and create the best possible strategy
            for the next move, considering the current board state, threats, and strategic opportunities.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_llm(self, model_name: str):
        """Create LLM instance for the specified model"""
        llm = ModelFactory.create_llm(model_name)
        if llm is None:
            # Fallback to default model
            print(f"Warning: Could not create LLM for {model_name}, falling back to llama3-latest")
            llm = ModelFactory.create_llm("llama3-latest")
        return llm
    
    def switch_model(self, model_name: str):
        """Switch to a different model"""
        new_llm = self._create_llm(model_name)
        if new_llm:
            self.llm = new_llm
            self.model_name = model_name
            # Update the agent's LLM
            self.agent.llm = new_llm
            return True
        return False
    
    def create_plan(self, observation: Observation) -> Plan:
        """Create a strategic plan based on the current observation"""
        import time
        start_time = time.time()
        
        try:
            # Analyze the board state
            board_analysis = self._analyze_board_state(observation)
            threat_assessment = self._assess_threats(observation)
            game_phase = self._determine_game_phase(observation)
            
            # Create primary strategy
            primary_strategy = self._create_primary_strategy(observation, board_analysis)
            
            # Create alternative strategies
            alternative_strategies = self._create_alternative_strategies(observation, primary_strategy)
            
            # Generate plan reasoning
            reasoning = self._generate_reasoning(observation, board_analysis, threat_assessment, game_phase)
            
            plan = Plan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                move_number=observation.move_number + 1,
                current_board=observation.current_board,
                primary_strategy=primary_strategy,
                alternative_strategies=alternative_strategies,
                board_analysis=board_analysis,
                threat_assessment=threat_assessment,
                confidence_level=self._calculate_confidence(observation, threat_assessment),
                reasoning=reasoning,
                game_phase=game_phase
            )
            
            # Track metrics if game_state is available
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            if self.game_state:
                self.game_state.increment_mcp_messages()
                self.game_state.add_message_flow_pattern("strategist_to_executor")
                self.game_state.add_response_time("strategist", response_time)
                self.game_state.add_message_latency(response_time)
                
                # Add estimated cost and token usage (Claude pricing)
                estimated_cost = 0.000015  # Rough estimate per message
                estimated_tokens = 200  # Rough estimate per strategy
                self.game_state.add_llm_cost("claude", estimated_cost)
                self.game_state.add_token_usage("strategist", estimated_tokens)
                
                # Update resource utilization
                try:
                    import psutil
                    cpu_percent = psutil.cpu_percent()
                    memory_mb = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB
                    self.game_state.update_resource_utilization(cpu_percent, memory_mb)
                except:
                    pass  # Ignore if psutil is not available
            
            return plan
            
        except Exception as e:
            print(f"Error in StrategistAgent.create_plan: {e}")
            # Return a fallback plan
            return self._create_fallback_plan(observation)
    
    def _analyze_board_state(self, observation: Observation) -> str:
        """Analyze the current board state"""
        board = observation.current_board
        available_moves = len(observation.available_moves)
        
        analysis = f"Board has {available_moves} available moves. "
        
        # Check for immediate threats
        if observation.threats:
            analysis += f"AI has {len(observation.threats)} winning opportunities. "
        
        if observation.blocking_moves:
            analysis += f"Player has {len(observation.blocking_moves)} winning opportunities that need blocking. "
        
        # Analyze strategic positions
        center_available = board[1][1] == ""
        corners_available = sum(1 for r, c in [(0,0), (0,2), (2,0), (2,2)] if board[r][c] == "")
        
        if center_available:
            analysis += "Center position is available. "
        if corners_available > 0:
            analysis += f"{corners_available} corner positions available. "
        
        return analysis
    
    def _assess_threats(self, observation: Observation) -> str:
        """Assess the current threat level"""
        if observation.threats:
            return "critical"  # AI can win immediately
        elif observation.blocking_moves:
            return "high"  # Player can win, must block
        elif observation.move_number < 3:
            return "low"  # Early game
        elif observation.move_number < 6:
            return "medium"  # Mid game
        else:
            return "high"  # End game
    
    def _determine_game_phase(self, observation: Observation) -> str:
        """Determine the current game phase"""
        if observation.move_number < 3:
            return "opening"
        elif observation.move_number < 6:
            return "midgame"
        else:
            return "endgame"
    
    def _create_primary_strategy(self, observation: Observation, board_analysis: str) -> Strategy:
        """Create the primary strategy for the next move"""
        # Priority 1: Win if possible
        if observation.threats:
            pos = observation.threats[0]
            return Strategy(
                position=pos,
                move_type="winning",
                confidence=0.95,
                reasoning="Immediate winning move available",
                expected_outcome="win"
            )
        
        # Priority 2: Block opponent's win
        if observation.blocking_moves:
            pos = observation.blocking_moves[0]
            return Strategy(
                position=pos,
                move_type="blocking",
                confidence=0.9,
                reasoning="Must block opponent's winning move",
                expected_outcome="continue"
            )
        
        # Priority 3: Take center
        if observation.current_board[1][1] == "":
            return Strategy(
                position=BoardPosition(row=1, col=1, value=""),
                move_type="center",
                confidence=0.8,
                reasoning="Center position is strategically valuable",
                expected_outcome="continue"
            )
        
        # Priority 4: Take corner
        corners = [(0,0), (0,2), (2,0), (2,2)]
        for r, c in corners:
            if observation.current_board[r][c] == "":
                return Strategy(
                    position=BoardPosition(row=r, col=c, value=""),
                    move_type="corner",
                    confidence=0.7,
                    reasoning="Corner position provides strategic advantage",
                    expected_outcome="continue"
                )
        
        # Priority 5: Take any available edge
        edges = [(0,1), (1,0), (1,2), (2,1)]
        for r, c in edges:
            if observation.current_board[r][c] == "":
                return Strategy(
                    position=BoardPosition(row=r, col=c, value=""),
                    move_type="edge",
                    confidence=0.5,
                    reasoning="Taking available edge position",
                    expected_outcome="continue"
                )
        
        # Fallback
        if observation.available_moves:
            pos = observation.available_moves[0]
            return Strategy(
                position=pos,
                move_type="random",
                confidence=0.3,
                reasoning="No clear strategic advantage, taking available move",
                expected_outcome="uncertain"
            )
    
    def _create_alternative_strategies(self, observation: Observation, primary: Strategy) -> list[Strategy]:
        """Create alternative strategies"""
        alternatives = []
        
        # Add a few alternative moves with lower confidence
        for i, move in enumerate(observation.available_moves[:3]):
            if move.row != primary.position.row or move.col != primary.position.col:
                alternatives.append(Strategy(
                    position=move,
                    move_type="alternative",
                    confidence=0.3 - (i * 0.1),
                    reasoning=f"Alternative move option {i+1}",
                    expected_outcome="continue"
                ))
        
        return alternatives
    
    def _calculate_confidence(self, observation: Observation, threat_assessment: str) -> float:
        """Calculate confidence level based on game state"""
        base_confidence = 0.5
        
        if threat_assessment == "critical":
            base_confidence = 0.95
        elif threat_assessment == "high":
            base_confidence = 0.8
        elif threat_assessment == "medium":
            base_confidence = 0.6
        elif threat_assessment == "low":
            base_confidence = 0.4
        
        # Adjust based on available moves
        if len(observation.available_moves) <= 2:
            base_confidence += 0.1
        
        return min(0.95, base_confidence)
    
    def _generate_reasoning(self, observation: Observation, board_analysis: str, 
                          threat_assessment: str, game_phase: str) -> str:
        """Generate reasoning for the plan"""
        return f"""Move {observation.move_number + 1} strategy: {board_analysis} 
        Threat assessment: {threat_assessment}. Game phase: {game_phase}. 
        Current player: {observation.current_player}. Available moves: {len(observation.available_moves)}."""
    
    def _create_fallback_plan(self, observation: Observation) -> Plan:
        """Create a fallback plan if the main strategy fails"""
        if observation.available_moves:
            fallback_move = observation.available_moves[0]
            return Plan(
                plan_id=f"fallback_{uuid.uuid4().hex[:8]}",
                move_number=observation.move_number + 1,
                current_board=observation.current_board,
                primary_strategy=Strategy(
                    position=fallback_move,
                    move_type="fallback",
                    confidence=0.3,
                    reasoning="Fallback strategy due to error",
                    expected_outcome="uncertain"
                ),
                alternative_strategies=[],
                board_analysis="Fallback analysis",
                threat_assessment="unknown",
                confidence_level=0.3,
                                 reasoning="Fallback plan created due to error",
                 game_phase="unknown"
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
            "name": "Strategist Agent",
            "role": "Strategy Creator",
            "model": model_display,
            "model_name": self.model_name,
            "provider": provider,
            "provider_type": provider_type,
            "provider_icon": provider_icon,
            "description": "Analyzes board state and creates strategic plans",
            "capabilities": ["Board Analysis", "Strategy Creation", "Threat Assessment", "Move Planning"]
        } 