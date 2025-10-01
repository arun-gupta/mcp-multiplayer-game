"""
Real MCP Server Implementation
Standalone MCP server for each CrewAI agent with SSE transport
"""
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from starlette.requests import Request
import uvicorn
import asyncio
import json
from typing import Callable, Dict, Any


class AgentMCPServer:
    """Real MCP Server for a CrewAI agent with SSE transport"""
    
    def __init__(self, agent, agent_id: str, port: int):
        self.agent = agent
        self.agent_id = agent_id
        self.port = port
        self.server = Server(f"{agent_id}-mcp-server")
        self.app = None
        self._setup_server()
    
    def _setup_server(self):
        """Setup MCP server with tools from agent"""
        
        # Get tools registry from agent
        tools_registry = self.agent.__dict__.get('tools_registry', {})
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all tools exposed by this agent"""
            tools = []
            for tool_name, tool_info in tools_registry.items():
                tools.append(Tool(
                    name=tool_name,
                    description=tool_info.get('description', ''),
                    inputSchema=tool_info.get('inputSchema', {})
                ))
            print(f"[MCP] {self.agent_id}: Listed {len(tools)} tools")
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a tool"""
            print(f"[MCP] {self.agent_id}: Calling tool '{name}' with args: {arguments}")
            
            if name not in tools_registry:
                error_msg = json.dumps({"error": f"Tool '{name}' not found"})
                return [TextContent(type="text", text=error_msg)]
            
            handler = tools_registry[name]['handler']
            
            try:
                # Check if handler needs arguments
                import inspect
                sig = inspect.signature(handler)
                
                # Call handler appropriately
                if len(sig.parameters) > 0:
                    result = await handler(arguments)
                else:
                    result = await handler()
                
                # Convert result to JSON string
                result_text = json.dumps(result, default=str)
                return [TextContent(type="text", text=result_text)]
            
            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                print(f"[MCP] {self.agent_id}: Tool execution error: {e}")
                return [TextContent(type="text", text=error_msg)]
    
    def create_starlette_app(self) -> Starlette:
        """Create Starlette app with SSE endpoint for MCP Inspector"""
        
        async def handle_sse(request: Request) -> Response:
            """Handle SSE connections for MCP protocol"""
            from sse_starlette import EventSourceResponse
            
            async def event_generator():
                # Create SSE transport
                async with SseServerTransport("/messages") as transport:
                    # Run MCP server with this transport
                    await self.server.run(
                        transport.read_stream,
                        transport.write_stream,
                        self.server.create_initialization_options()
                    )
            
            return EventSourceResponse(event_generator())
        
        async def handle_messages(request: Request) -> Response:
            """Handle MCP messages endpoint"""
            body = await request.json()
            
            # Process MCP request
            method = body.get("method")
            params = body.get("params", {})
            request_id = body.get("id", 1)
            
            if method == "initialize":
                # MCP initialization handshake
                return Response(
                    content=json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": f"{self.agent_id}-mcp-server",
                                "version": "1.0.0"
                            }
                        }
                    }),
                    media_type="application/json"
                )
            
            elif method == "tools/list":
                # List tools
                tools_registry = self.agent.__dict__.get('tools_registry', {})
                tools = []
                for tool_name, tool_info in tools_registry.items():
                    tools.append({
                        "name": tool_name,
                        "description": tool_info.get('description', ''),
                        "inputSchema": tool_info.get('inputSchema', {})
                    })
                
                return Response(
                    content=json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"tools": tools}
                    }),
                    media_type="application/json"
                )
            
            elif method == "tools/call":
                # Call a tool
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                tools_registry = self.agent.__dict__.get('tools_registry', {})
                if tool_name not in tools_registry:
                    return Response(
                        content=json.dumps({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Tool '{tool_name}' not found"
                            }
                        }),
                        media_type="application/json"
                    )
                
                handler = tools_registry[tool_name]['handler']
                
                try:
                    # Check if handler needs arguments
                    import inspect
                    sig = inspect.signature(handler)
                    
                    if len(sig.parameters) > 0:
                        result = await handler(arguments)
                    else:
                        result = await handler()
                    
                    return Response(
                        content=json.dumps({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result, default=str)
                                    }
                                ]
                            }
                        }),
                        media_type="application/json"
                    )
                
                except Exception as e:
                    return Response(
                        content=json.dumps({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32603,
                                "message": str(e)
                            }
                        }),
                        media_type="application/json"
                    )
            
            else:
                return Response(
                    content=json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method '{method}' not supported"
                        }
                    }),
                    media_type="application/json"
                )
        
        async def health_check(request: Request) -> Response:
            """Health check endpoint"""
            return Response(
                content=json.dumps({
                    "status": "healthy",
                    "agent_id": self.agent_id,
                    "mcp_version": "2024-11-05",
                    "tools_count": len(self.agent.__dict__.get('tools_registry', {}))
                }),
                media_type="application/json"
            )
        
        routes = [
            Route("/sse", handle_sse, methods=["GET"]),
            Route("/messages", handle_messages, methods=["POST"]),
            Route("/health", health_check, methods=["GET"]),
        ]
        
        app = Starlette(debug=True, routes=routes)
        return app
    
    async def start(self):
        """Start the MCP server"""
        self.app = self.create_starlette_app()
        
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="warning"  # Reduce noise
        )
        
        server = uvicorn.Server(config)
        
        print(f"🚀 Starting real MCP Server for {self.agent_id}")
        print(f"   Port: {self.port}")
        print(f"   SSE Endpoint: http://localhost:{self.port}/sse")
        print(f"   Messages Endpoint: http://localhost:{self.port}/messages")
        print(f"   MCP Inspector URL: http://localhost:{self.port}")
        
        # Run server as background task
        asyncio.create_task(server.serve())
        
        # Give server time to start
        await asyncio.sleep(1)
        
        print(f"✅ MCP Server running for {self.agent_id}")

