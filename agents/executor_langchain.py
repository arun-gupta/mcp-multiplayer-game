"""
LangChain-based Executor Agent for Tic-Tac-Toe
Replaces CrewAI Executor with direct LangChain implementation
"""

import json
import asyncio
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatLiteLLM
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class MoveExecution(BaseModel):
    """Structured output for move execution"""
    move: Dict[str, int] = Field(description="Move to execute with row and col")
    validation: str = Field(description="Move validation result")
    execution_status: str = Field(description="Execution status: SUCCESS, FAILED, INVALID")
    reasoning: str = Field(description="Reasoning for the move execution")


class ExecutorLangChain:
    """LangChain-based Executor agent for move execution"""
    
    def __init__(self, model_name: str = "gpt-5-mini"):
        self.model_name = model_name
        self.llm = self._create_llm()
        self.parser = PydanticOutputParser(pydantic_object=MoveExecution)
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Tic-Tac-Toe move execution expert. Your job is to validate and execute moves.

VALIDATION RULES:
1. Check if the move is within bounds (0-2 for row and col)
2. Check if the position is empty
3. Ensure the move follows Tic-Tac-Toe rules

EXECUTION:
- If valid, execute the move
- If invalid, provide a valid alternative
- Always provide clear reasoning

{format_instructions}"""),
            ("human", """Execute this Tic-Tac-Toe move:
Recommended Move: {recommended_move}
Board: {board}
Strategy: {strategy}
Current Player: {current_player}

Validate and execute the move:""")
        ])
    
    def _create_llm(self):
        """Create the appropriate LLM based on model name"""
        if "gpt" in self.model_name.lower():
            # GPT-5 models don't support custom temperature, use default
            return ChatOpenAI(
                model=self.model_name,
                timeout=10.0
            )
        elif "claude" in self.model_name.lower():
            return ChatAnthropic(
                model=self.model_name,
                temperature=0.1,
                timeout=10.0
            )
        else:
            # Use LiteLLM for other models
            return ChatLiteLLM(
                model=self.model_name,
                temperature=0.1,
                timeout=10.0
            )
    
    async def execute_move(self, execution_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a move based on strategy recommendation"""
        try:
            print(f"[DEBUG] ExecutorLangChain: Starting move execution")
            
            # Prepare the input
            recommended_move = execution_input.get("recommended_move", {})
            board = execution_input.get("board", [])
            strategy = execution_input.get("strategy", "")
            current_player = "O"  # AI player
            
            # Create the chain
            chain = self.prompt | self.llm | self.parser
            
            # Make the call
            result = await chain.ainvoke({
                "recommended_move": json.dumps(recommended_move),
                "board": json.dumps(board),
                "strategy": strategy,
                "current_player": current_player,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            print(f"[DEBUG] ExecutorLangChain: Move execution completed")
            
            return {
                "success": True,
                "move": result.move,
                "validation": result.validation,
                "execution_status": result.execution_status,
                "reasoning": result.reasoning
            }
            
        except Exception as e:
            print(f"[DEBUG] ExecutorLangChain: Move execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "move": {"row": 1, "col": 1},  # Fallback to center
                "validation": "Failed validation",
                "execution_status": "FAILED",
                "reasoning": "Move execution failed, using fallback"
            }
    
    async def validate_move(self, move: Dict[str, int], board: List[List[str]]) -> Dict[str, Any]:
        """Validate a move"""
        try:
            row, col = move.get("row", 0), move.get("col", 0)
            
            # Basic validation
            if not (0 <= row <= 2 and 0 <= col <= 2):
                return {"valid": False, "reason": "Move out of bounds"}
            
            if board[row][col] != "":
                return {"valid": False, "reason": "Position already occupied"}
            
            return {"valid": True, "reason": "Move is valid"}
            
        except Exception as e:
            return {"valid": False, "reason": f"Validation error: {e}"}
    
    async def update_game_state(self, move: Dict[str, int], board: List[List[str]]) -> Dict[str, Any]:
        """Update the game state with the move"""
        try:
            row, col = move.get("row", 0), move.get("col", 0)
            
            # Make a copy of the board
            new_board = [row[:] for row in board]
            new_board[row][col] = "O"  # AI player
            
            return {
                "success": True,
                "board": new_board,
                "move_made": move
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "board": board
            }
    
    async def confirm_execution(self, move: Dict[str, int]) -> Dict[str, Any]:
        """Confirm the move execution"""
        return {
            "success": True,
            "move": move,
            "confirmation": "Move executed successfully"
        }
