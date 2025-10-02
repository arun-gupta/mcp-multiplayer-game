#!/usr/bin/env python3
"""
Standalone Executor Agent MCP Server
Runs as independent process on port 3003
"""
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.executor_local import ExecutorMCPAgent
from models.factory import ModelFactory

app = FastAPI(
    title="Executor Agent MCP Server",
    description="Standalone Executor Agent with MCP Protocol",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
executor_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize Executor agent"""
    global executor_agent
    print("🚀 Starting Executor Agent MCP Server...")

    # Get default model
    available_models = ModelFactory.get_default_models()
    model = available_models.get("executor", "gpt-5-mini")

    print(f"🔍 Initializing Executor Agent with model: {model}")
    executor_agent = ExecutorMCPAgent({"model": model})

    # Start MCP server
    await executor_agent.start_mcp_server()
    print(f"✅ Executor Agent ready on port 3003")
    print(f"   MCP endpoint: http://localhost:3003/mcp")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "executor",
        "port": 3003,
        "model": executor_agent.__dict__.get('current_model') if executor_agent else "unknown"
    }

@app.get("/mcp")
async def mcp_discovery():
    """MCP discovery endpoint - returns tools, resources, and prompts"""
    if executor_agent is None:
        raise HTTPException(status_code=503, detail="Executor agent not initialized")

    # Get registries
    tools_registry = executor_agent.__dict__.get('tools_registry', {})
    resources_registry = executor_agent.__dict__.get('resources_registry', {})
    prompts_registry = executor_agent.__dict__.get('prompts_registry', {})

    # Build response
    tools = [
        {
            "name": name,
            "description": info.get('description', ''),
            "inputSchema": info.get('inputSchema', {})
        }
        for name, info in tools_registry.items()
    ]

    resources = [
        {
            "uri": uri,
            "name": info.get('name', ''),
            "description": info.get('description', ''),
            "mimeType": info.get('mimeType', 'text/plain')
        }
        for uri, info in resources_registry.items()
    ]

    prompts = [
        {
            "name": name,
            "description": info.get('description', ''),
            "arguments": info.get('arguments', [])
        }
        for name, info in prompts_registry.items()
    ]

    return {
        "jsonrpc": "2.0",
        "result": {
            "serverInfo": {
                "name": "executor_agent",
                "version": "1.0.0",
                "transport": "http"
            },
            "capabilities": {
                "tools": {"supported": True, "count": len(tools)},
                "resources": {"supported": True, "count": len(resources)},
                "prompts": {"supported": True, "count": len(prompts)}
            },
            "tools": tools,
            "resources": resources,
            "prompts": prompts
        }
    }

@app.post("/mcp")
async def mcp_call(request: Request):
    """MCP protocol endpoint - handles tool calls, resource reads, etc."""
    if executor_agent is None:
        raise HTTPException(status_code=503, detail="Executor agent not initialized")

    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id", 1)

        if method == "tools/call":
            # Call a tool
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            tools_registry = executor_agent.__dict__.get('tools_registry', {})
            if tool_name not in tools_registry:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
                }

            handler = tools_registry[tool_name]['handler']
            result = await handler(arguments)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

        elif method == "resources/read":
            # Read a resource
            uri = params.get("uri")
            resources_registry = executor_agent.__dict__.get('resources_registry', {})

            if uri not in resources_registry:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Resource '{uri}' not found"}
                }

            getter = resources_registry[uri]['getter']
            content = await getter()

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": content
            }

        elif method == "tools/list":
            # List tools
            tools_registry = executor_agent.__dict__.get('tools_registry', {})
            tools = [
                {
                    "name": name,
                    "description": info.get('description', ''),
                    "inputSchema": info.get('inputSchema', {})
                }
                for name, info in tools_registry.items()
            ]

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method '{method}' not supported"}
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1) if 'body' in locals() else 1,
            "error": {"code": -32603, "message": str(e)}
        }

if __name__ == "__main__":
    print("=" * 60)
    print("Executor Agent MCP Server")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=3003, log_level="info")
