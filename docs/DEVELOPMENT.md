# 🛠️ Development Guide

## Development Workflow

1. **Start Development** - Launch MCP agents and coordinator
2. **Iterative Testing** - Make changes, rebuild, reconnect Inspector
3. **Edge Case Testing** - Test invalid inputs, concurrent operations
4. **Production Monitoring** - Use MCP endpoints for monitoring

## Development Setup

### Prerequisites

- Python 3.11+
- Virtual environment (venv)
- Git

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/arun-gupta/mcp-multiplayer-game.git
cd mcp-multiplayer-game

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Development Dependencies

```bash
# Install development dependencies
pip install -r requirements.txt

# Install additional development tools
pip install pytest black flake8 mypy
```

### Ollama Optimization for Development

For the best development experience with instant AI responses:

```bash
# Keep models loaded in memory for instant responses
OLLAMA_KEEP_ALIVE=-1 ollama run llama3.2:1b
```

**Benefits for development:**
- ⚡ **Instant testing** - No model loading delays during development
- 🚀 **Faster iteration** - Quick feedback when testing agent changes
- 🎮 **Seamless debugging** - Models stay loaded while debugging MCP flows

## Project Structure

```
mcp-multiplayer-game/
├── main.py                 # FastAPI application
├── streamlit_app.py        # Streamlit dashboard
├── run_app.py             # Unified launcher script
├── requirements.txt       # Python dependencies
├── README.md             # Main documentation
├── docs/                  # Documentation
│   ├── QUICKSTART.md     # Detailed setup guide
│   ├── README_STREAMLIT.md # Streamlit UI guide
│   ├── DOCKER_README.md  # Docker deployment guide
│   ├── GITHUB_ACTIONS_SETUP.md # CI/CD setup guide
│   ├── ARCHITECTURE.md   # Architecture documentation
│   ├── DEVELOPMENT.md    # This file
│   ├── FEATURES.md       # Features documentation
│   ├── API.md           # API documentation
│   └── USER_GUIDE.md    # User guide
├── schemas/              # MCP-style communication schemas
│   ├── observation.py    # Scout observations
│   ├── plan.py          # Strategist plans
│   └── action_result.py # Executor results
├── agents/              # CrewAI agent implementations
│   ├── base_mcp_agent.py # Base MCP Agent class
│   ├── scout.py        # Scout agent
│   ├── strategist.py   # Strategist agent
│   └── executor.py     # Executor agent
└── game/               # Game logic and state
    ├── mcp_coordinator.py # MCP Game Coordinator
    └── state.py       # Tic Tac Toe game state management
```

## Development Commands

### Running the Application

```bash
# Start both backend and frontend
python run_app.py

# Or start separately
python main.py          # Backend API (port 8000)
streamlit run streamlit_app.py  # Frontend (port 8501)

# Or use the quickstart script
./quickstart.sh
```

### Testing

```bash
# Run MCP system tests
python test_mcp_hybrid.py

# Run specific tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=agents tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Run all quality checks
black . && flake8 . && mypy .
```

## MCP Development

### Adding New Agents

1. **Create Agent Class**:
```python
from agents.base_mcp_agent import BaseMCPAgent

class NewAgent(BaseMCPAgent):
    def __init__(self, model_config: Dict):
        super().__init__(
            role="New Agent",
            goal="Agent goal",
            backstory="Agent backstory",
            mcp_port=3004,  # Next available port
            agent_id="new_agent",
            llm=self.create_llm(model_config)
        )
    
    def register_agent_specific_endpoints(self):
        self.register_handler("new_tool", self.new_tool)
    
    async def new_tool(self, data: Dict) -> Dict:
        # Implement tool logic
        return {"result": "success"}
```

2. **Register in Coordinator**:
```python
# In game/mcp_coordinator.py
self.agents["new_agent"] = "MockMCPClient(new_agent://localhost:3004)"
```

3. **Add to Main Application**:
```python
# In main.py
from agents.new_agent import NewAgent

# Initialize agent
new_agent = NewAgent({"model": "gpt-4"})
await new_agent.start_mcp_server()
```

### Adding New MCP Tools

1. **Register Handler**:
```python
def register_agent_specific_endpoints(self):
    self.register_handler("new_tool", self.new_tool)
```

2. **Implement Tool**:
```python
async def new_tool(self, data: Dict) -> Dict:
    try:
        # Tool implementation
        result = await self.process_data(data)
        return {
            "success": True,
            "result": result,
            "agent_id": self.agent_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "agent_id": self.agent_id
        }
```

### MCP Inspector Integration

```bash
# Connect to individual agents for debugging
npx @modelcontextprotocol/inspector node agents/scout.py
npx @modelcontextprotocol/inspector node agents/strategist.py
npx @modelcontextprotocol/inspector node agents/executor.py
```

## Debugging

### Common Issues

1. **Import Errors** - Ensure all dependencies are installed
2. **Port Conflicts** - Check if ports 3001-3003 are available
3. **Model Errors** - Verify API keys for LLM providers
4. **MCP Communication** - Check agent status endpoints

### Debug Commands

```bash
# Check agent status
curl http://localhost:8000/agents/status

# Check health
curl http://localhost:8000/health

# View MCP logs
curl http://localhost:8000/mcp-logs

# Test the MCP hybrid system
python test_mcp_hybrid.py
```

### Logging

```python
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use in your code
logger.info("Agent started successfully")
logger.error(f"Error: {str(e)}")
```

## Performance Optimization

### Agent Performance

- **Memory Management**: Monitor agent memory usage
- **Response Times**: Track agent response times
- **Concurrent Requests**: Handle multiple requests efficiently

### MCP Protocol Optimization

- **Connection Pooling**: Reuse MCP connections
- **Batch Operations**: Group multiple operations
- **Caching**: Cache frequently accessed data

## Deployment

### Local Deployment

```bash
# Start all services
./quickstart.sh

# Or manually
python main.py &
python run_streamlit.py
```

### Production Deployment

```bash
# Using Docker
docker-compose up -d

# Using systemd
sudo systemctl start mcp-game
```

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Add unit tests for new features

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Testing Requirements

- All new features must have tests
- Maintain test coverage above 80%
- Test both success and error cases
- Test MCP protocol communication

## Troubleshooting

### Agent Communication Issues

```bash
# Check if agents are running
curl http://localhost:8000/agents/status

# Check MCP logs
curl http://localhost:8000/mcp-logs

# Test individual agent
python -c "from agents.scout import ScoutMCPAgent; print('Scout agent imports successfully')"
```

### Performance Issues

```bash
# Monitor system resources
htop

# Check port usage
lsof -i :3001-3003

# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

### Memory Issues

```bash
# Check memory usage
ps aux | grep python

# Monitor agent memory
curl http://localhost:8000/agents/scout/metrics
```

## Next Steps

1. **Implement Real MCP Protocol** - Replace mock implementation with actual MCP library
2. **MCP Inspector Integration** - Connect to MCP Inspector for debugging
3. **Distributed Deployment** - Deploy agents on different machines
4. **Advanced Monitoring** - Enhanced metrics and monitoring
5. **Unit Tests** - Comprehensive testing of MCP endpoints
6. **Documentation** - Complete API documentation
