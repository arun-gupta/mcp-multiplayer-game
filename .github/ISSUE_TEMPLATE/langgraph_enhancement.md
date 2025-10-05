---
name: 🔄 LangGraph Integration Enhancement
about: Replace manual agent coordination with LangGraph workflow orchestration
title: '[ENHANCEMENT] Migrate from manual agent coordination to LangGraph workflow'
labels: enhancement, langgraph, architecture, good first issue
assignees: ''
---

## 🎯 Overview

Replace the current manual agent coordination system with **LangGraph** workflow orchestration to improve state management, enable conditional routing, and provide better observability into the multi-agent workflow.

## 📋 Current Implementation

**Current Architecture (`main.py` LangChain mode):**
```python
# Manual sequential coordination
scout_result = await scout_agent.analyze_board(board_state)
strategist_result = await strategist_agent.create_strategy({
    "board_state": board_state,
    "threats": scout_result.get("threats", []),
    "opportunities": scout_result.get("opportunities", [])
})
executor_result = await executor_agent.execute_move({
    "recommended_move": strategist_result.get("move"),
    "strategy": strategist_result.get("strategy")
})
```

**Problems:**
- ❌ Manual state passing between agents (dict manipulation)
- ❌ No conditional routing (always Scout → Strategist → Executor)
- ❌ Sequential execution (no parallelization)
- ❌ No workflow visualization
- ❌ No checkpointing or state persistence

## 🎯 Proposed LangGraph Implementation

### **1. Define State Schema**

```python
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END

class GameState(TypedDict):
    """Shared state across all agents"""
    board: List[List[str]]
    current_player: str
    move_count: int

    # Scout outputs
    threats: List[Dict[str, int]]
    opportunities: List[Dict[str, int]]
    strategic_moves: List[Dict[str, int]]
    scout_analysis: str

    # Strategist outputs
    strategy: str
    recommended_move: Dict[str, int]
    priority: str
    strategy_reasoning: str

    # Executor outputs
    executed_move: Dict[str, int]
    execution_status: str
    game_over: bool
    winner: Optional[str]
```

### **2. Create LangGraph Workflow**

```python
# Create workflow graph
workflow = StateGraph(GameState)

# Add agent nodes
workflow.add_node("scout", scout_agent_node)
workflow.add_node("strategist", strategist_agent_node)
workflow.add_node("executor", executor_agent_node)

# Add conditional routing
workflow.add_conditional_edges(
    "scout",
    route_after_scout,  # Conditional: immediate win/block vs strategy
    {
        "immediate_action": "executor",  # Skip strategist if immediate threat/opportunity
        "strategic": "strategist"         # Normal flow through strategist
    }
)

workflow.add_edge("strategist", "executor")
workflow.add_edge("executor", END)

# Set entry point
workflow.set_entry_point("scout")

# Compile with checkpointing (optional)
app = workflow.compile(checkpointer=MemorySaver())
```

### **3. Implement Agent Nodes**

```python
async def scout_agent_node(state: GameState) -> GameState:
    """Scout agent as LangGraph node"""
    result = await scout_agent.analyze_board({
        "board": state["board"],
        "current_player": state["current_player"],
        "available_moves": get_available_moves(state["board"])
    })

    return {
        **state,
        "threats": result.get("threats", []),
        "opportunities": result.get("opportunities", []),
        "strategic_moves": result.get("strategic_moves", []),
        "scout_analysis": result.get("analysis", "")
    }

async def strategist_agent_node(state: GameState) -> GameState:
    """Strategist agent as LangGraph node"""
    result = await strategist_agent.create_strategy({
        "board_state": state["board"],
        "threats": state["threats"],
        "opportunities": state["opportunities"],
        "available_moves": state["strategic_moves"]
    })

    return {
        **state,
        "strategy": result.get("strategy", ""),
        "recommended_move": result.get("move", {}),
        "priority": result.get("priority", "STRATEGIC"),
        "strategy_reasoning": result.get("reasoning", "")
    }

async def executor_agent_node(state: GameState) -> GameState:
    """Executor agent as LangGraph node"""
    result = await executor_agent.execute_move({
        "recommended_move": state["recommended_move"],
        "board": state["board"],
        "strategy": state["strategy"]
    })

    return {
        **state,
        "executed_move": result.get("move", {}),
        "execution_status": result.get("execution_status", ""),
        "game_over": check_game_over(state["board"]),
        "winner": get_winner(state["board"])
    }
```

### **4. Implement Conditional Routing**

```python
def route_after_scout(state: GameState) -> str:
    """
    Conditional routing after scout analysis

    If immediate win/block opportunity exists, skip strategist
    Otherwise, proceed to strategist for complex analysis
    """
    # Check for immediate opportunities (winning move)
    if state["opportunities"] and len(state["opportunities"]) > 0:
        # Direct execution of winning move
        state["recommended_move"] = state["opportunities"][0]
        state["priority"] = "WIN"
        return "immediate_action"

    # Check for immediate threats (blocking move)
    if state["threats"] and len(state["threats"]) > 0:
        # Direct execution of blocking move
        state["recommended_move"] = state["threats"][0]
        state["priority"] = "BLOCK"
        return "immediate_action"

    # No immediate action needed, proceed to strategist
    return "strategic"
```

## 📦 Implementation Tasks

### **Phase 1: Setup & Dependencies**
- [ ] Add `langgraph` to `requirements.txt`
- [ ] Create `agents/langgraph_workflow.py` module
- [ ] Define `GameState` TypedDict schema
- [ ] Update `main.py` to support `--langgraph` mode flag

### **Phase 2: Node Implementation**
- [ ] Convert Scout agent to LangGraph node (`scout_agent_node`)
- [ ] Convert Strategist agent to LangGraph node (`strategist_agent_node`)
- [ ] Convert Executor agent to LangGraph node (`executor_agent_node`)
- [ ] Add error handling and fallback logic to each node

### **Phase 3: Workflow & Routing**
- [ ] Create StateGraph with agent nodes
- [ ] Implement conditional routing function (`route_after_scout`)
- [ ] Add edges and conditional edges
- [ ] Set entry point and compile workflow

### **Phase 4: Integration**
- [ ] Create LangGraph coordinator class (`LangGraphCoordinator`)
- [ ] Update FastAPI `/game/ai-move` endpoint to support LangGraph mode
- [ ] Add LangGraph metrics and monitoring
- [ ] Update Streamlit UI to show LangGraph workflow visualization

### **Phase 5: Advanced Features (Optional)**
- [ ] Add memory/checkpointing for game state persistence
- [ ] Implement parallel execution (threats + opportunities detection)
- [ ] Add workflow visualization endpoint (`/workflow/graph`)
- [ ] Implement branching strategies (multiple strategies evaluated in parallel)
- [ ] Add LangSmith integration for workflow tracing

### **Phase 6: Documentation & Testing**
- [ ] Update README with LangGraph mode instructions
- [ ] Add LangGraph architecture diagram
- [ ] Write unit tests for workflow nodes
- [ ] Add integration tests for conditional routing
- [ ] Document performance comparison vs manual coordination

## 📊 Expected Benefits

### **Performance**
- ⚡ **Parallel execution**: Run threat detection + opportunity detection simultaneously
- 🚀 **Conditional routing**: Skip strategist for immediate win/block (faster response)
- 💾 **Checkpointing**: Save/resume game state at any point

### **Architecture**
- 🎯 **State management**: Automatic state passing, no manual dict manipulation
- 🔄 **Workflow clarity**: Declarative graph structure vs imperative code
- 📊 **Observability**: Built-in workflow visualization and tracing
- 🧪 **Testability**: Test individual nodes and routing logic independently

### **Scalability**
- 🌐 **Branching**: Evaluate multiple strategies in parallel
- 🔁 **Loops**: Support iterative refinement (strategist → executor → strategist)
- 📈 **Complexity**: Handle more complex workflows without code complexity

## 📚 Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangGraph Tutorial**: https://langchain-ai.github.io/langgraph/tutorials/introduction/
- **State Management**: https://langchain-ai.github.io/langgraph/how-tos/state-model/
- **Conditional Routing**: https://langchain-ai.github.io/langgraph/how-tos/branching/
- **Example Multi-Agent**: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/

## 🎓 Good First Issue Guide

This is marked as "good first issue" because:

1. **Self-contained**: Adds new mode alongside existing implementations
2. **Clear scope**: Well-defined tasks and acceptance criteria
3. **Learning opportunity**: Hands-on experience with LangGraph
4. **Documentation**: Extensive resources and examples provided
5. **Testable**: Easy to verify against existing manual coordination

### **Getting Started:**
1. Fork the repository
2. Install development dependencies: `pip install -r requirements.txt`
3. Add `langgraph` to requirements.txt
4. Start with Phase 1 tasks (setup)
5. Test against existing LangChain mode for parity
6. Submit PR with tests and documentation

## ✅ Acceptance Criteria

- [ ] LangGraph mode accessible via `./quickstart.sh --langgraph` flag
- [ ] All three agents (Scout, Strategist, Executor) work as LangGraph nodes
- [ ] Conditional routing skips strategist for immediate win/block scenarios
- [ ] State properly flows between nodes without manual dict passing
- [ ] Performance is equal to or better than manual coordination
- [ ] Workflow visualization available via `/workflow/graph` endpoint
- [ ] Documentation updated with LangGraph architecture
- [ ] Tests cover node execution and conditional routing
- [ ] Backward compatible (existing modes still work)

## 🤝 Contributing

Interested in implementing this? Great! Here's how to get started:

1. Comment on this issue expressing interest
2. Review the current LangChain implementation in `main.py`
3. Read through the LangGraph documentation
4. Start with Phase 1 tasks (setup)
5. Ask questions in comments if anything is unclear
6. Submit a draft PR early for feedback

We're happy to provide guidance and code review support!

---

**Questions?** Comment below or reach out in discussions.

**Related Issues:** #TBD (link to any related performance or architecture issues)
