# 🐳 Docker Deployment Guide

This guide explains how to deploy the MCP Multiplayer Game using Docker with secure API key management.

## 📋 Prerequisites

- Docker installed on your system
- OpenAI API key
- Anthropic API key
- (Optional) Ollama for local models

## 🔑 API Key Management Strategies

### **Handling Existing .env Files**

If you've been developing locally, you likely already have a `.env` file with your API keys. The Docker setup will automatically use this existing file:

```bash
# Check if .env exists
ls -la .env

# If it exists, Docker will use it automatically
# If not, create it from template
cp .env.example .env
```

### **Method 1: Environment File (Recommended)**

1. **Create `.env` file:**
```bash
cp .env.example .env
```

2. **Edit `.env` with your API keys:**
```bash
# OpenAI API Key (Required for Scout Agent)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Anthropic API Key (Required for Strategist Agent)
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here

# Optional settings
PORT=8000
ENVIRONMENT=production
```

3. **Run with Docker:**
```bash
# Using our convenience script
./docker-run.sh

# Or manually
docker run -d \
    --name mcp-game \
    --env-file .env \
    -p 8000:8000 \
    -p 8501:8501 \
    mcp-multiplayer-game
```

### **Method 2: Docker Compose**

```bash
# Set environment variables
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"

# Run with compose
docker-compose up -d
```

### **Method 3: Direct Environment Variables**

```bash
docker run -d \
    --name mcp-game \
    -e OPENAI_API_KEY="sk-your-key" \
    -e ANTHROPIC_API_KEY="sk-ant-your-key" \
    -p 8000:8000 \
    -p 8501:8501 \
    mcp-multiplayer-game
```

### **Method 4: Docker Secrets (Production)**

For production environments, use Docker secrets:

```bash
# Create secrets
echo "sk-your-openai-key" | docker secret create openai_api_key -
echo "sk-ant-your-anthropic-key" | docker secret create anthropic_api_key -

# Run with secrets
docker run -d \
    --name mcp-game \
    --secret openai_api_key \
    --secret anthropic_api_key \
    -p 8000:8000 \
    -p 8501:8501 \
    mcp-multiplayer-game
```

## 🚀 Quick Start

### **1. Clone and Setup**
```bash
git clone https://github.com/arun-gupta/mcp-multiplayer-game.git
cd mcp-multiplayer-game
```

**Note**: If you've been developing locally, you may already have a `.env` file with your API keys. The Docker setup will use this existing file automatically.

### **2. Set API Keys**
```bash
# Check if .env already exists (from local development)
if [ ! -f .env ]; then
    # Create environment file from template
    cp .env.example .env
    echo "📝 Created .env file from template"
else
    echo "✅ .env file already exists"
fi

# Edit with your keys
nano .env  # or use your preferred editor
```

### **3. Build and Run**
```bash
# Option A: Use convenience script (handles existing .env files)
./docker-run.sh

# Option B: Manual build and run
docker build -t mcp-multiplayer-game .
docker run -d --name mcp-game --env-file .env -p 8000:8000 -p 8501:8501 mcp-multiplayer-game
```

### **4. Access the Application**
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Docker Compose with Ollama

For local models support, use the full compose setup:

```bash
# Run with Ollama for local models
docker-compose --profile local-models up -d

# Pull Ollama models
docker exec -it mcp-multiplayer-game_ollama_1 ollama pull llama2:7b
docker exec -it mcp-multiplayer-game_ollama_1 ollama pull mistral:latest
```

## 🛡️ Security Best Practices

### **1. Never Commit API Keys**
- `.env` files are in `.gitignore`
- Use `.env.example` for templates
- Use Docker secrets in production

### **2. Use Non-Root User**
- Dockerfile creates `app` user
- Application runs as non-root

### **3. Health Checks**
- Container includes health checks
- Monitors application status

### **4. Resource Limits**
```bash
docker run -d \
    --name mcp-game \
    --env-file .env \
    --memory="2g" \
    --cpus="1.0" \
    -p 8000:8000 \
    -p 8501:8501 \
    mcp-multiplayer-game
```

## 📊 Monitoring and Logs

### **View Logs**
```bash
# Follow logs
docker logs -f mcp-game

# Last 100 lines
docker logs --tail 100 mcp-game
```

### **Container Status**
```bash
# Check if running
docker ps --filter "name=mcp-game"

# Container stats
docker stats mcp-game
```

### **Health Check**
```bash
# Manual health check
curl http://localhost:8000/health
```

## 🔄 Container Management

### **Stop and Remove**
```bash
# Stop container
docker stop mcp-game

# Remove container
docker rm mcp-game

# Stop and remove in one command
docker rm -f mcp-game
```

### **Update Application**
```bash
# Stop current container
docker stop mcp-game
docker rm mcp-game

# Rebuild and run
docker build -t mcp-multiplayer-game .
./docker-run.sh
```

### **Backup and Restore**
```bash
# Backup container
docker export mcp-game > mcp-game-backup.tar

# Restore container
docker import mcp-game-backup.tar mcp-multiplayer-game:backup
```

## 🌐 Production Deployment

### **Using Docker Swarm**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml mcp-game
```

### **Using Kubernetes**
```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-game
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-game
  template:
    metadata:
      labels:
        app: mcp-game
    spec:
      containers:
      - name: mcp-game
        image: mcp-multiplayer-game:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic
        ports:
        - containerPort: 8000
        - containerPort: 8501
```

## 🐛 Troubleshooting

### **Common Issues**

1. **"API key not found"**
   - Check `.env` file exists and has correct keys
   - Verify keys are not placeholder values
   - If you have an existing `.env` file from local development, it will be used automatically

2. **"Port already in use"**
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :8501
   
   # Kill existing processes
   docker rm -f mcp-game
   ```

3. **"Container won't start"**
   ```bash
   # Check logs
   docker logs mcp-game
   
   # Run interactively for debugging
   docker run -it --env-file .env mcp-multiplayer-game bash
   ```

4. **"Health check failing"**
   - Wait for application to fully start (30-60 seconds)
   - Check if all dependencies are available

### **Debug Mode**
```bash
# Run interactively
docker run -it --env-file .env -p 8000:8000 -p 8501:8501 mcp-multiplayer-game bash

# Inside container
python main.py
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Secrets](https://docs.docker.com/engine/swarm/secrets/)
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Anthropic API Keys](https://console.anthropic.com/)

## 🤝 Contributing

When contributing to Docker setup:

1. Test with different API key methods
2. Update `.dockerignore` if adding new files
3. Ensure security best practices
4. Update this documentation
