"""
Base MCP Agent Class
Combines CrewAI Agent capabilities with MCP Server communication
"""
from crewai import Agent, Task
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime
from abc import ABC, abstractmethod
import psutil
import os


class BaseMCPAgent(Agent, ABC):
    """Base class combining CrewAI Agent with MCP Server capabilities"""
    
    def __init__(self, role: str, goal: str, backstory: str, 
                 mcp_port: int, agent_id: str, **kwargs):
        # Initialize CrewAI Agent with only valid CrewAI parameters
        Agent.__init__(
            self,
            role=role,
            goal=goal, 
            backstory=backstory,
            memory=True,
            verbose=True,
            **kwargs
        )
        
        # Set MCP-specific attributes after CrewAI initialization
        # Use __dict__ to bypass Pydantic validation issues
        self.__dict__['mcp_port'] = mcp_port
        self.__dict__['agent_id'] = agent_id
        self.__dict__['mcp_server'] = None
        self.__dict__['mcp_clients'] = {}
        self.__dict__['is_running'] = False
        
        # Performance metrics
        self.__dict__['request_count'] = 0
        self.__dict__['total_response_time'] = 0.0
        self.__dict__['avg_response_time'] = 0.0
        self.__dict__['min_response_time'] = float('inf')
        self.__dict__['max_response_time'] = 0.0
        
        # LLM-specific metrics
        self.__dict__['total_tokens'] = 0
        self.__dict__['api_call_count'] = 0
        self.__dict__['api_success_count'] = 0
        self.__dict__['api_error_count'] = 0
        self.__dict__['timeout_count'] = 0
        
        # Get the actual model name from the LLM
        model_name = getattr(self.llm, 'model', None) or getattr(self.llm, 'model_name', None) or str(self.llm.__class__.__name__)
        self.__dict__['current_model'] = str(model_name)
        self.__dict__['last_request_time'] = None
        self.__dict__['timestamp'] = datetime.now().isoformat()
        
    async def start_mcp_server(self):
        """Start MCP server and register endpoints"""
        # TODO: Implement actual MCP server initialization
        # For now, simulate with a simple HTTP server or use FastAPI
        self.setup_mcp_endpoints()
        self.__dict__['is_running'] = True
        agent_id = self.__dict__.get('agent_id', 'unknown')
        mcp_port = self.__dict__.get('mcp_port', 0)
        print(f"MCP Server started for {agent_id} on port {mcp_port}")
    
    def setup_mcp_endpoints(self):
        """Register MCP endpoints - to be implemented with actual MCP library"""
        # Standard endpoints all agents should expose
        self.register_handler("execute_task", self.mcp_execute_task)
        self.register_handler("get_status", self.get_agent_status)
        self.register_handler("get_memory", self.get_agent_memory)
        self.register_handler("switch_model", self.switch_llm_model)
        self.register_handler("get_metrics", self.get_performance_metrics)
        
        # Agent-specific endpoints
        self.register_agent_specific_endpoints()
    
    @abstractmethod
    def register_agent_specific_endpoints(self):
        """Each agent registers its specific MCP endpoints"""
        pass
    
    def register_handler(self, endpoint: str, handler):
        """Register MCP endpoint handler"""
        # TODO: Implement with actual MCP library
        agent_id = self.__dict__.get('agent_id', 'unknown')
        print(f"Registered {endpoint} for {agent_id}")
    
    def track_request(self, response_time: float = None, success: bool = True, tokens: int = 0):
        """Track a request for this agent with enhanced metrics"""
        agent_id = self.__dict__.get('agent_id', 'unknown')
        current_count = self.__dict__.get('request_count', 0)
        print(f"[METRICS] {agent_id}.track_request called! Current count: {current_count}")
        
        self.__dict__['request_count'] += 1
        self.__dict__['last_request_time'] = datetime.now().isoformat()
        self.__dict__['timestamp'] = datetime.now().isoformat()
        
        print(f"[METRICS] {agent_id} new count: {self.__dict__['request_count']}")
        
        # Track response time metrics
        if response_time is not None:
            self.__dict__['total_response_time'] += response_time
            self.__dict__['avg_response_time'] = (
                self.__dict__['total_response_time'] / 
                self.__dict__['request_count']
            )
            # Track min/max response times
            if response_time < self.__dict__['min_response_time']:
                self.__dict__['min_response_time'] = response_time
            if response_time > self.__dict__['max_response_time']:
                self.__dict__['max_response_time'] = response_time
            
            print(f"[METRICS] {agent_id} avg: {self.__dict__['avg_response_time']:.6f}s, min: {self.__dict__['min_response_time']:.6f}s, max: {self.__dict__['max_response_time']:.6f}s")
        else:
            print(f"[METRICS] {agent_id} WARNING: response_time is None!")
        
        # Track API success/failure
        self.__dict__['api_call_count'] += 1
        if success:
            self.__dict__['api_success_count'] += 1
        else:
            self.__dict__['api_error_count'] += 1
        
        # Track token usage
        if tokens > 0:
            self.__dict__['total_tokens'] += tokens
            print(f"[METRICS] {agent_id} total tokens: {self.__dict__['total_tokens']}")
    
    def track_timeout(self):
        """Track a timeout event"""
        self.__dict__['timeout_count'] = self.__dict__.get('timeout_count', 0) + 1
        agent_id = self.__dict__.get('agent_id', 'unknown')
        print(f"[METRICS] {agent_id} timeout count: {self.__dict__['timeout_count']}")
    
    
    async def mcp_execute_task(self, task_data: Dict) -> Dict:
        """Execute CrewAI task via MCP protocol"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create CrewAI Task from MCP data
            task = Task(
                description=task_data.get("description", ""),
                expected_output=task_data.get("expected_output", ""),
                context=task_data.get("context", [])
            )
            
            # Execute using CrewAI's execution engine
            result = await asyncio.to_thread(self.execute, task)
            
            # Track performance
            response_time = asyncio.get_event_loop().time() - start_time
            current_count = self.__dict__.get('request_count', 0)
            current_time = self.__dict__.get('total_response_time', 0.0)
            self.__dict__['request_count'] = current_count + 1
            self.__dict__['total_response_time'] = current_time + response_time
            
            agent_id = self.__dict__.get('agent_id', 'unknown')
            return {
                "success": True,
                "result": result,
                "agent_id": agent_id,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            agent_id = self.__dict__.get('agent_id', 'unknown')
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_agent_status(self) -> Dict:
        """Get current agent status"""
        agent_id = self.__dict__.get('agent_id', 'unknown')
        is_running = self.__dict__.get('is_running', False)
        current_model = self.__dict__.get('current_model', 'unknown')
        mcp_port = self.__dict__.get('mcp_port', 0)
        
        return {
            "agent_id": str(agent_id),
            "role": str(agent_id).title() + " Agent",  # Use agent_id as role instead of self.role
            "is_running": bool(is_running),
            "current_model": str(current_model),
            "mcp_port": int(mcp_port),
            "memory_size": int(self._get_memory_size())
        }
    
    async def get_agent_memory(self) -> Dict:
        """Expose agent memory via MCP"""
        # TODO: Implement proper memory serialization
        agent_id = self.__dict__.get('agent_id', 'unknown')
        return {
            "agent_id": agent_id,
            "memory_data": "Memory content here",  # Serialize actual memory
            "timestamp": datetime.now().isoformat()
        }
    
    async def switch_llm_model(self, model_config: Dict) -> Dict:
        """Hot-swap LLM model"""
        try:
            # TODO: Implement actual model switching logic
            old_model = self.__dict__.get('current_model', 'unknown')
            # self.llm = create_new_llm(model_config)
            new_model = model_config.get("model", "unknown")
            self.__dict__['current_model'] = new_model
            
            agent_id = self.__dict__.get('agent_id', 'unknown')
            return {
                "success": True,
                "old_model": old_model,
                "new_model": new_model,
                "agent_id": agent_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_performance_metrics(self) -> Dict:
        """Get agent performance metrics with enhanced A/B testing data"""
        total_time = self.__dict__.get('total_response_time', 0.0)
        request_count = self.__dict__.get('request_count', 0)
        avg_response_time = (total_time / request_count if request_count > 0 else 0.0)
        
        agent_id = self.__dict__.get('agent_id', 'unknown')
        current_model = self.__dict__.get('current_model', 'unknown')
        
        # Get min/max response times
        min_time = self.__dict__.get('min_response_time', 0.0)
        max_time = self.__dict__.get('max_response_time', 0.0)
        
        # Handle infinity case for min_time
        if min_time == float('inf'):
            min_time = 0.0
        
        # Calculate API success rate
        api_call_count = self.__dict__.get('api_call_count', 0)
        api_success_count = self.__dict__.get('api_success_count', 0)
        success_rate = (api_success_count / api_call_count * 100 if api_call_count > 0 else 100.0)
        
        # Calculate tokens per request
        total_tokens = self.__dict__.get('total_tokens', 0)
        tokens_per_request = (total_tokens / request_count if request_count > 0 else 0)
        
        return {
            "agent_id": agent_id,
            "current_model": current_model,
            
            # Performance metrics
            "request_count": request_count,
            "avg_response_time": round(avg_response_time, 6),
            "min_response_time": round(min_time, 6),
            "max_response_time": round(max_time, 6),
            "total_processing_time": round(total_time, 6),
            
            # LLM-specific metrics
            "total_tokens": total_tokens,
            "tokens_per_request": round(tokens_per_request, 1),
            "api_call_count": api_call_count,
            "api_success_rate": round(success_rate, 1),
            "api_error_count": self.__dict__.get('api_error_count', 0),
            "timeout_count": self.__dict__.get('timeout_count', 0),
            
            # Memory (process-level)
            "memory_usage": self.get_memory_usage(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_memory_size(self) -> int:
        """Get memory size safely"""
        try:
            if hasattr(self, 'memory') and self.memory and hasattr(self.memory, 'storage'):
                return len(self.memory.storage)
            return 0
        except Exception:
            return 0
    
    def get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        try:
            process = psutil.Process(os.getpid())
            return round(process.memory_info().rss / 1024 / 1024, 2)
        except Exception:
            return 0.0
    
    async def call_agent(self, agent_endpoint: str, method: str, data: Dict) -> Dict:
        """Call another agent via MCP protocol"""
        # TODO: Implement actual MCP client call
        agent_id = self.__dict__.get('agent_id', 'unknown')
        print(f"{agent_id} calling {agent_endpoint}/{method} with data: {data}")
        return {"mock": "response"}
