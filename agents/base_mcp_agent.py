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

# MCP Protocol imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, Prompt, PromptMessage
from .mcp_server import AgentMCPServer


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
        self.__dict__['mcp_server'] = Server(f"{agent_id}-mcp-server")  # ✨ Real MCP Server
        self.__dict__['mcp_standalone_server'] = None  # Standalone MCP server instance
        self.__dict__['mcp_clients'] = {}
        self.__dict__['is_running'] = False
        self.__dict__['tools_registry'] = {}  # Store tool metadata
        self.__dict__['resources_registry'] = {}  # Store resource metadata
        self.__dict__['prompts_registry'] = {}  # Store prompt templates
        
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
        """Start real MCP server with protocol support"""
        agent_id = self.__dict__.get('agent_id', 'unknown')
        mcp_port = self.__dict__.get('mcp_port', 0)
        mcp_server = self.__dict__.get('mcp_server')
        
        # Setup MCP protocol endpoints
        self.setup_mcp_endpoints()
        
        # Register MCP protocol handlers
        @mcp_server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools via MCP protocol"""
            tools = []
            tools_registry = self.__dict__.get('tools_registry', {})
            
            for tool_name, tool_info in tools_registry.items():
                tools.append(Tool(
                    name=tool_name,
                    description=tool_info.get('description', ''),
                    inputSchema=tool_info.get('inputSchema', {})
                ))
            
            print(f"[MCP] {agent_id}: Listed {len(tools)} tools via MCP protocol")
            return tools
        
        @mcp_server.list_resources()
        async def list_resources() -> list[Resource]:
            """List all available resources via MCP protocol"""
            resources = []
            resources_registry = self.__dict__.get('resources_registry', {})
            
            for resource_uri, resource_info in resources_registry.items():
                resources.append(Resource(
                    uri=resource_uri,
                    name=resource_info.get('name', ''),
                    description=resource_info.get('description', ''),
                    mimeType=resource_info.get('mimeType', 'text/plain')
                ))
            
            print(f"[MCP] {agent_id}: Listed {len(resources)} resources via MCP protocol")
            return resources
        
        @mcp_server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource"""
            resources_registry = self.__dict__.get('resources_registry', {})
            if uri not in resources_registry:
                raise ValueError(f"Resource '{uri}' not found")
            
            getter = resources_registry[uri]['getter']
            content = await getter()
            return content
        
        @mcp_server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            """List all available prompts via MCP protocol"""
            prompts = []
            prompts_registry = self.__dict__.get('prompts_registry', {})
            
            for prompt_name, prompt_info in prompts_registry.items():
                prompts.append(Prompt(
                    name=prompt_name,
                    description=prompt_info.get('description', ''),
                    arguments=prompt_info.get('arguments', [])
                ))
            
            print(f"[MCP] {agent_id}: Listed {len(prompts)} prompts via MCP protocol")
            return prompts
        
        @mcp_server.get_prompt()
        async def get_prompt(name: str, arguments: dict = None) -> PromptMessage:
            """Get a specific prompt with optional arguments"""
            prompts_registry = self.__dict__.get('prompts_registry', {})
            if name not in prompts_registry:
                raise ValueError(f"Prompt '{name}' not found")
            
            generator = prompts_registry[name]['generator']
            messages = await generator(arguments or {})
            return messages
        
        @mcp_server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Call a tool via MCP protocol"""
            print(f"[MCP] {agent_id}: Tool '{name}' called with args: {arguments}")
            
            tools_registry = self.__dict__.get('tools_registry', {})
            if name not in tools_registry:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Tool '{name}' not found"})
                )]
            
            handler = tools_registry[name]['handler']
            try:
                result = await handler(arguments)
                return [TextContent(
                    type="text",
                    text=json.dumps(result)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)})
                )]
        
        # MCP server is registered and ready
        # Note: HTTP/SSE endpoints will be exposed via main FastAPI app
        # to avoid multiple uvicorn instances in same event loop
        
        self.__dict__['is_running'] = True
        print(f"✅ MCP Server registered for {agent_id}")
        print(f"   Designated Port: {mcp_port}")
        print(f"   Tools Registered: {len(self.__dict__.get('tools_registry', {}))}")
        print(f"   🔍 MCP Inspector URL: http://localhost:8000/mcp/{agent_id}")
    
    def setup_mcp_endpoints(self):
        """Register MCP tools - both standard and agent-specific"""
        # Standard tools all agents should expose
        self.register_mcp_tool(
            "execute_task",
            self.mcp_execute_task,
            "Execute a CrewAI task via MCP protocol",
            {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "expected_output": {"type": "string"},
                    "context": {"type": "array"}
                },
                "required": ["description"]
            }
        )
        
        self.register_mcp_tool(
            "get_status",
            self.get_agent_status,
            "Get current agent status and information",
            {"type": "object", "properties": {}}
        )
        
        self.register_mcp_tool(
            "get_memory",
            self.get_agent_memory,
            "Get agent memory contents",
            {"type": "object", "properties": {}}
        )
        
        self.register_mcp_tool(
            "get_metrics",
            self.get_performance_metrics,
            "Get agent performance metrics",
            {"type": "object", "properties": {}}
        )
        
        # Agent-specific tools
        self.register_agent_specific_endpoints()
        
        # Register standard resources
        self.register_standard_resources()
        
        # Register standard prompts
        self.register_standard_prompts()
    
    @abstractmethod
    def register_agent_specific_endpoints(self):
        """Each agent registers its specific MCP tools"""
        pass
    
    def register_standard_resources(self):
        """Register standard resources all agents expose"""
        agent_id = self.__dict__.get('agent_id', 'unknown')
        
        # Agent status resource
        self.register_mcp_resource(
            f"agent://{agent_id}/status",
            f"{agent_id.title()} Agent Status",
            "Current status, model, and configuration",
            self.get_agent_status,
            "application/json"
        )
        
        # Agent metrics resource
        self.register_mcp_resource(
            f"agent://{agent_id}/metrics",
            f"{agent_id.title()} Performance Metrics",
            "Real-time performance metrics and statistics",
            self.get_performance_metrics,
            "application/json"
        )
        
        # Agent memory resource  
        self.register_mcp_resource(
            f"agent://{agent_id}/memory",
            f"{agent_id.title()} Agent Memory",
            "Agent memory and conversation history",
            self.get_agent_memory,
            "application/json"
        )
    
    def register_standard_prompts(self):
        """Register standard prompts all agents expose"""
        agent_id = self.__dict__.get('agent_id', 'unknown')
        
        # Task execution prompt
        async def generate_task_prompt(args: dict) -> PromptMessage:
            description = args.get('task_description', 'Execute a task')
            return PromptMessage(
                role="user",
                content=f"""You are the {agent_id} agent.
                
Task: {description}

Analyze the situation and provide your response based on your role:
- Role: {self.role}
- Goal: {self.goal}

Provide a structured response with your analysis and recommendations."""
            )
        
        self.register_mcp_prompt(
            "execute_task_prompt",
            f"Prompt template for executing tasks as {agent_id} agent",
            generate_task_prompt,
            [
                {
                    "name": "task_description",
                    "description": "Description of the task to execute",
                    "required": True
                }
            ]
        )
    
    def register_mcp_tool(self, name: str, handler, description: str, input_schema: dict):
        """Register a tool with the MCP server"""
        agent_id = self.__dict__.get('agent_id', 'unknown')
        tools_registry = self.__dict__.get('tools_registry', {})
        
        tools_registry[name] = {
            'handler': handler,
            'description': description,
            'inputSchema': input_schema
        }
        
        self.__dict__['tools_registry'] = tools_registry
        print(f"[MCP] Registered tool '{name}' for {agent_id}")
    
    # Alias for backward compatibility
    def register_handler(self, endpoint: str, handler):
        """Alias for register_mcp_tool (backward compatibility)"""
        self.register_mcp_tool(
            endpoint,
            handler,
            f"{endpoint.replace('_', ' ').title()}",
            {"type": "object", "properties": {}}
        )
    
    def register_mcp_resource(self, uri: str, name: str, description: str, 
                             getter: Callable, mime_type: str = "application/json"):
        """Register a resource with the MCP server"""
        agent_id = self.__dict__.get('agent_id', 'unknown')
        resources_registry = self.__dict__.get('resources_registry', {})
        
        resources_registry[uri] = {
            'name': name,
            'description': description,
            'getter': getter,
            'mimeType': mime_type
        }
        
        self.__dict__['resources_registry'] = resources_registry
        print(f"[MCP] Registered resource '{name}' ({uri}) for {agent_id}")
    
    def register_mcp_prompt(self, name: str, description: str, 
                           generator: Callable, arguments: list = None):
        """Register a prompt template with the MCP server"""
        agent_id = self.__dict__.get('agent_id', 'unknown')
        prompts_registry = self.__dict__.get('prompts_registry', {})
        
        prompts_registry[name] = {
            'description': description,
            'generator': generator,
            'arguments': arguments or []
        }
        
        self.__dict__['prompts_registry'] = prompts_registry
        print(f"[MCP] Registered prompt '{name}' for {agent_id}")
    
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
