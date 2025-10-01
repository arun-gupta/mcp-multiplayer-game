"""
MCP HTTP Server Wrapper
Exposes MCP Server via HTTP/SSE for Inspector and external clients
"""
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import uvicorn
import asyncio
from typing import Optional


class MCPHTTPServer:
    """HTTP wrapper for MCP Server to enable Inspector connectivity"""
    
    def __init__(self, mcp_server: Server, agent_id: str, port: int):
        self.mcp_server = mcp_server
        self.agent_id = agent_id
        self.port = port
        self.app = None
        self.server_task = None
        
    def create_app(self) -> Starlette:
        """Create Starlette app with MCP SSE transport"""
        
        async def handle_sse(request):
            """Handle SSE connections for MCP protocol"""
            async with SseServerTransport("/mcp") as transport:
                await self.mcp_server.run(
                    transport.read_stream,
                    transport.write_stream,
                    self.mcp_server.create_initialization_options()
                )
        
        async def handle_health(request):
            """Health check endpoint"""
            return JSONResponse({
                "status": "healthy",
                "agent_id": self.agent_id,
                "mcp_version": "1.0",
                "transport": "sse",
                "endpoints": {
                    "mcp": "/mcp",
                    "health": "/health"
                }
            })
        
        routes = [
            Route("/mcp", handle_sse, methods=["GET", "POST"]),
            Route("/health", handle_health, methods=["GET"])
        ]
        
        app = Starlette(debug=True, routes=routes)
        return app
    
    async def start(self):
        """Start HTTP server for MCP protocol"""
        self.app = self.create_app()
        
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        print(f"🌐 Starting MCP HTTP Server for {self.agent_id} on port {self.port}")
        print(f"   MCP Inspector URL: http://localhost:{self.port}/mcp")
        
        # Run server in background
        self.server_task = asyncio.create_task(server.serve())
        
        return self.server_task
    
    async def stop(self):
        """Stop HTTP server"""
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
        print(f"✅ MCP HTTP Server stopped for {self.agent_id}")


async def start_mcp_http_server(mcp_server: Server, agent_id: str, port: int) -> MCPHTTPServer:
    """Helper function to start MCP HTTP server"""
    http_server = MCPHTTPServer(mcp_server, agent_id, port)
    await http_server.start()
    return http_server

