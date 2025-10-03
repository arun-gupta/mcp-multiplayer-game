#!/usr/bin/env python3
"""
Simplified Scout Agent MCP Server
Focuses on MCP protocol only, using MCPServerAdapter
"""
import asyncio
import sys
import os
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.scout_local import ScoutMCPAgent
from models.factory import ModelFactory

class SimplifiedScoutServer:
    """Simplified Scout MCP Server using standard MCP protocol"""
    
    def __init__(self, port=3001):
        self.port = port
        self.agent = None
        self.server = Server("scout-mcp-server")
        self.app = None
        
    async def initialize_agent(self):
        """Initialize the scout agent"""
        print("🔍 Initializing Scout Agent...")
        
        # Get default model
        available_models = ModelFactory.get_default_models()
        model = available_models.get("scout", "gpt-5-mini")
        
        print(f"   Model: {model}")
        self.agent = ScoutMCPAgent({"model": model})
        
        # Start MCP server to register tools
        await self.agent.start_mcp_server()
        
        # Register MCP tools
        await self._register_tools()
        print("✅ Scout Agent initialized")
        
    async def _register_tools(self):
        """Register MCP tools with the server"""
        if not self.agent:
            return
            
        # Get tools from agent
        tools_registry = self.agent.__dict__.get('tools_registry', {})
        print(f"[DEBUG] Scout tools registry: {tools_registry}")
        
        for tool_name, tool_info in tools_registry.items():
            @self.server.list_tools()
            async def list_tools() -> list[Tool]:
                tools = []
                if self.agent:
                    tools_registry = self.agent.__dict__.get('tools_registry', {})
                    for name, tool_info in tools_registry.items():
                        tools.append(Tool(
                            name=name,
                            description=tool_info.get('description', ''),
                            inputSchema=tool_info.get('schema', {})
                        ))
                return tools
            
            @self.server.call_tool()
            async def call_tool(name: str, arguments: dict) -> list[TextContent]:
                if self.agent and name in self.agent.__dict__.get('tools_registry', {}):
                    try:
                        handler = self.agent.__dict__['tools_registry'][name]['handler']
                        result = await handler(arguments)
                        return [TextContent(type="text", text=str(result))]
                    except Exception as e:
                        return [TextContent(
                            type="text", 
                            text=json.dumps({"error": str(e)})
                        )]
                else:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": f"Tool '{name}' not found"})
                    )]
    
    def create_app(self) -> Starlette:
        """Create Starlette app with MCP SSE transport"""
        
        # Create SSE transport and connect it to the MCP server
        sse_transport = SseServerTransport("/messages")
        
        # Connect the SSE transport to the MCP server
        async def handle_sse(request):
            """Handle SSE connection requests"""
            async with sse_transport.connect_sse(request.scope, request.receive, request.send) as (read_stream, write_stream):
                # Run the MCP server with the SSE streams
                await self.server.run(read_stream, write_stream)
        
        async def handle_messages(request):
            """Handle MCP message requests"""
            return await sse_transport.handle_post_message(request.scope, request.receive, request.send)
        
        async def handle_health(request):
            """Health check endpoint"""
            return JSONResponse({
                "status": "healthy",
                "agent_id": "scout",
                "mcp_version": "1.0",
                "transport": "sse",
                "tools_count": len(self.agent.__dict__.get('tools_registry', {})) if self.agent else 0
            })
        
        routes = [
            Route("/", handle_sse, methods=["GET"]),
            Route("/messages", handle_messages, methods=["POST"]),
            Route("/health", handle_health, methods=["GET"])
        ]
        
        app = Starlette(debug=True, routes=routes)
        return app
    
    async def run(self):
        """Run the MCP server"""
        print(f"🚀 Starting Scout MCP Server on port {self.port}")
        print(f"   MCP Endpoint: http://localhost:{self.port}/")
        print(f"   Health Check: http://localhost:{self.port}/health")
        
        # Initialize agent
        await self.initialize_agent()
        
        # Create app
        self.app = self.create_app()
        
        # Run server
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

async def main():
    """Main entry point"""
    server = SimplifiedScoutServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())