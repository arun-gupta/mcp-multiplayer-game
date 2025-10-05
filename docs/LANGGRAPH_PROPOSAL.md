# 🔄 LangGraph Integration Proposal

## Overview

This document outlines the proposed migration from manual agent coordination to LangGraph workflow orchestration.

## Current vs Proposed Architecture

### **Current: Manual Coordination**

```
┌─────────────────────────────────────────────────────────┐
│                      main.py                            │
│  Manual Sequential Coordination (Imperative)            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │  scout_result = await scout() │
           └───────────────┬───────────────┘
                           │
                    (manual dict passing)
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │  strategist_result = await          │
         │    strategist(scout_result)         │
         └──────────────┬──────────────────────┘
                        │
                 (manual dict passing)
                        │
                        ▼
       ┌────────────────────────────────────────┐
       │  executor_result = await               │
       │    executor(strategist_result)         │
       └────────────────────────────────────────┘

Problems:
❌ Manual state management (dict manipulation)
❌ No conditional routing
❌ Sequential only (no parallelization)
❌ No workflow visualization
❌ No checkpointing
```

### **Proposed: LangGraph Workflow**

```
┌─────────────────────────────────────────────────────────┐
│                   LangGraph Workflow                    │
│           (Declarative State Graph)                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────┐
                    │  START   │
                    └────┬─────┘
                         │
                         ▼
                  ┌─────────────┐
                  │    Scout    │
                  │   analyze   │
                  └──────┬──────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Conditional Router  │
              │  (route_after_scout) │
              └──────────┬───────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌─────────┐    ┌──────────┐   ┌─────────┐
    │ WIN NOW │    │  BLOCK   │   │ STRATEGY│
    │ (skip)  │    │  (skip)  │   │ (normal)│
    └────┬────┘    └────┬─────┘   └────┬────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
                        ▼
                  ┌──────────┐
                  │Strategist│ (conditional)
                  │ strategy │
                  └────┬─────┘
                       │
                       ▼
                 ┌──────────┐
                 │ Executor │
                 │ execute  │
                 └────┬─────┘
                      │
                      ▼
                  ┌──────┐
                  │ END  │
                  └──────┘

Benefits:
✅ Automatic state management (StateGraph)
✅ Conditional routing (skip strategist when obvious)
✅ Parallel execution possible (threats + opportunities)
✅ Built-in visualization
✅ Checkpointing support
✅ Better observability (LangSmith integration)
```

## State Schema

```python
class GameState(TypedDict):
    """Shared state managed by LangGraph"""

    # Input state
    board: List[List[str]]
    current_player: str
    move_count: int

    # Scout outputs (automatically added to state)
    threats: List[Dict[str, int]]
    opportunities: List[Dict[str, int]]
    strategic_moves: List[Dict[str, int]]
    scout_analysis: str

    # Strategist outputs (automatically added to state)
    strategy: str
    recommended_move: Dict[str, int]
    priority: str  # "WIN", "BLOCK", "STRATEGIC"
    strategy_reasoning: str

    # Executor outputs (automatically added to state)
    executed_move: Dict[str, int]
    execution_status: str
    game_over: bool
    winner: Optional[str]
```

## Workflow Execution Example

### **Scenario 1: Immediate Win Opportunity**

```
Input: Board with winning move available

┌──────┐
│START │
└──┬───┘
   │
   ▼
┌────────────┐
│   Scout    │ → Detects opportunity: [[1,1]]
└──────┬─────┘
       │
       ▼
┌─────────────────┐
│ route_after_    │ → Returns "immediate_action"
│ scout()         │
└──────┬──────────┘
       │
       ▼
┌────────────┐
│  Executor  │ → Executes winning move
│  (SKIP     │
│ Strategist)│
└──────┬─────┘
       │
       ▼
    ┌─────┐
    │ END │
    └─────┘

Performance: ~33% faster (skips Strategist)
```

### **Scenario 2: Opponent Threat Detected**

```
Input: Board with opponent about to win

┌──────┐
│START │
└──┬───┘
   │
   ▼
┌────────────┐
│   Scout    │ → Detects threat: [[2,0]]
└──────┬─────┘
       │
       ▼
┌─────────────────┐
│ route_after_    │ → Returns "immediate_action"
│ scout()         │
└──────┬──────────┘
       │
       ▼
┌────────────┐
│  Executor  │ → Blocks opponent
│  (SKIP     │
│ Strategist)│
└──────┬─────┘
       │
       ▼
    ┌─────┐
    │ END │
    └─────┘

Performance: ~33% faster (skips Strategist)
```

### **Scenario 3: Strategic Positioning**

```
Input: Early game, no immediate threats/opportunities

┌──────┐
│START │
└──┬───┘
   │
   ▼
┌────────────┐
│   Scout    │ → No threats/opportunities
└──────┬─────┘
       │
       ▼
┌─────────────────┐
│ route_after_    │ → Returns "strategic"
│ scout()         │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ Strategist  │ → Analyzes best position
└──────┬──────┘
       │
       ▼
┌────────────┐
│  Executor  │ → Executes strategic move
└──────┬─────┘
       │
       ▼
    ┌─────┐
    │ END │
    └─────┘

Performance: Same as current (full pipeline)
```

## Advanced Features (Future)

### **1. Parallel Execution**

```
         ┌──────────┐
         │  Scout   │
         └────┬─────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
┌─────────┐        ┌─────────────┐
│ Threat  │        │Opportunity  │  (Parallel)
│Detection│        │Detection    │
└────┬────┘        └──────┬──────┘
     │                    │
     └──────────┬─────────┘
                │
                ▼
          ┌──────────┐
          │  Merge   │
          └────┬─────┘
               │
               ▼
         ┌──────────┐
         │Strategist│
         └──────────┘
```

### **2. Iterative Refinement**

```
         ┌──────────┐
         │Strategist│
         └────┬─────┘
              │
              ▼
         ┌──────────┐
         │Validator │
         └────┬─────┘
              │
         ┌────┴─────┐
         │          │
    Valid│          │Invalid
         │          │
         ▼          ▼
    ┌────────┐  ┌──────────┐
    │Execute │  │Strategist│ (Loop back)
    └────────┘  └──────────┘
```

### **3. Multi-Strategy Evaluation**

```
         ┌──────────┐
         │  Scout   │
         └────┬─────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐┌────────┐┌────────┐
│Strategy││Strategy││Strategy│ (Parallel)
│   A    ││   B    ││   C    │
└───┬────┘└───┬────┘└───┬────┘
    │         │         │
    └─────────┼─────────┘
              │
              ▼
         ┌──────────┐
         │   Best   │
         │  Picker  │
         └────┬─────┘
              │
              ▼
         ┌──────────┐
         │ Executor │
         └──────────┘
```

## Implementation Checklist

### **Phase 1: Core Workflow ⭐**
- [ ] Install langgraph
- [ ] Define GameState TypedDict
- [ ] Create scout_agent_node
- [ ] Create strategist_agent_node
- [ ] Create executor_agent_node
- [ ] Implement route_after_scout
- [ ] Build StateGraph
- [ ] Test basic workflow

### **Phase 2: Integration**
- [ ] Create LangGraphCoordinator
- [ ] Add --langgraph flag to main.py
- [ ] Update /game/ai-move endpoint
- [ ] Add workflow visualization
- [ ] Update Streamlit UI

### **Phase 3: Advanced (Optional)**
- [ ] Parallel threat/opportunity detection
- [ ] Checkpointing for game state
- [ ] LangSmith tracing integration
- [ ] Multi-strategy evaluation
- [ ] Iterative refinement loops

## Performance Comparison

| Scenario | Current (Manual) | LangGraph (Basic) | LangGraph (Optimized) |
|----------|-----------------|-------------------|----------------------|
| **Immediate Win** | 3 LLM calls | 3 LLM calls | 2 LLM calls (33% faster) |
| **Block Threat** | 3 LLM calls | 3 LLM calls | 2 LLM calls (33% faster) |
| **Strategic** | 3 LLM calls | 3 LLM calls | 3 LLM calls (same) |
| **Parallel** | N/A | N/A | 2 LLM calls (parallel) |
| **Multi-Strategy** | N/A | N/A | 5 LLM calls (3 parallel) |

**Expected Average Improvement:** 10-15% faster in typical games (mix of scenarios)

## Code Size Comparison

| Component | Current (Manual) | LangGraph |
|-----------|-----------------|-----------|
| Coordination Logic | ~150 lines | ~100 lines |
| State Management | Manual dicts | Automatic |
| Error Handling | Per-call | Per-node |
| Visualization | None | Built-in |
| Checkpointing | None | Built-in |

## Migration Strategy

### **Option 1: Gradual (Recommended)**
1. Add LangGraph mode alongside existing modes
2. Test parity with manual coordination
3. Gather performance metrics
4. Eventually deprecate manual mode

### **Option 2: Direct Replacement**
1. Replace manual coordination with LangGraph
2. Keep same API interface
3. Single breaking change

**Recommendation:** Option 1 (Gradual) - Lower risk, allows A/B testing

## Success Metrics

- [ ] **Functionality:** All game scenarios work correctly
- [ ] **Performance:** Equal or better latency vs manual coordination
- [ ] **Code Quality:** Reduced lines of code, better maintainability
- [ ] **Observability:** Workflow visualization available
- [ ] **Scalability:** Support for advanced features (parallel, loops)

## Questions & Discussion

1. **Should we support checkpointing?**
   - Yes for game state persistence, but adds complexity

2. **Parallel execution worth it for Tic-Tac-Toe?**
   - Probably not significant gains, but good for demonstration

3. **Keep manual mode after migration?**
   - Yes initially for comparison, deprecate later

4. **LangSmith integration?**
   - Optional, but valuable for debugging workflows

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Multi-Agent Tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [Conditional Routing Guide](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [State Management Best Practices](https://langchain-ai.github.io/langgraph/how-tos/state-model/)

---

**Status:** 📋 Proposal - Ready for Implementation

**Created:** 2025-01-XX

**Last Updated:** 2025-01-XX
