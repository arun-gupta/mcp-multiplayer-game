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
        
        # Register MCP tools
        await self._register_tools()
        print("✅ Scout Agent initialized")
        
    async def _register_tools(self):
        """Register MCP tools for the scout agent"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            tools = []
            for name, tool_info in self.agent.__dict__.get('tools_registry', {}).items():
                tools.append(Tool(
                    name=name,
                    description=tool_info.get('description', ''),
                    inputSchema=tool_info.get('inputSchema', {})
                ))
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Call a tool"""
            try:
                tools_registry = self.agent.__dict__.get('tools_registry', {})
                if name not in tools_registry:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": f"Tool '{name}' not found"})
                    )]
                
                handler = tools_registry[name]['handler']
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
    
    def create_app(self) -> Starlette:
        """Create Starlette app with MCP SSE transport"""
        
        async def handle_sse(request):
            """Handle SSE connections for MCP protocol"""
            async with SseServerTransport("/mcp") as transport:
                await self.server.run(
                    transport.read_stream,
                    transport.write_stream,
                    self.server.create_initialization_options()
                )
        
        async def handle_health(request):
            """Health check endpoint"""
            return JSONResponse({
                "status": "healthy",
                "agent_id": "scout",
                "mcp_version": "1.0",
                "transport": "sse",
                "tools_count": len(self.agent.__dict__.get('tools_registry', {}))
            })
        
        routes = [
            Route("/mcp", handle_sse, methods=["GET", "POST"]),
            Route("/health", handle_health, methods=["GET"])
        ]
        
        app = Starlette(debug=True, routes=routes)
        return app
    
    async def start(self):
        """Start the MCP server"""
        await self.initialize_agent()
        self.app = self.create_app()
        
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="warning"
        )
        
        server = uvicorn.Server(config)
        
        print(f"🚀 Starting Scout MCP Server on port {self.port}")
        print(f"   MCP Endpoint: http://localhost:{self.port}/mcp")
        print(f"   Health Check: http://localhost:{self.port}/health")
        
        await server.serve()

async def main():
    """Main entry point"""
    server = SimplifiedScoutServer(port=3001)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
