#!/bin/bash

echo "🔍 Docker Hub Setup Verification"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Check Docker Hub repository${NC}"
echo "Repository: arungupta/mcp-multiplayer-game"
echo "URL: https://hub.docker.com/r/arungupta/mcp-multiplayer-game"
echo ""

echo -e "${YELLOW}Step 2: Verify Docker Hub credentials${NC}"
echo "1. Go to: https://hub.docker.com/settings/security"
echo "2. Create access token with 'Read & Write' permissions"
echo "3. Copy the token (you won't see it again!)"
echo ""

echo -e "${YELLOW}Step 3: Set GitHub Secrets${NC}"
echo "1. Go to: https://github.com/arun-gupta/mcp-multiplayer-game/settings/secrets/actions"
echo "2. Add repository secrets:"
echo "   - DOCKERHUB_USERNAME: arungupta"
echo "   - DOCKERHUB_TOKEN: [your access token]"
echo ""

echo -e "${YELLOW}Step 4: Test locally (optional)${NC}"
echo "If you want to test locally:"
echo "1. docker login -u arungupta"
echo "2. docker pull hello-world"
echo "3. docker push arungupta/mcp-multiplayer-game:test"
echo ""

echo -e "${GREEN}✅ Setup Checklist:${NC}"
echo "□ Docker Hub repository exists"
echo "□ Access token created with 'Read & Write' permissions"
echo "□ GitHub secret DOCKERHUB_USERNAME = arungupta"
echo "□ GitHub secret DOCKERHUB_TOKEN = [access token]"
echo "□ Repository is accessible to your account"
echo ""

echo -e "${YELLOW}🔧 Common Issues:${NC}"
echo "• 401 Unauthorized: Check username/token"
echo "• Repository not found: Create repository first"
echo "• Insufficient scope: Token needs 'Read & Write' permissions"
echo "• Access denied: Repository doesn't exist or wrong permissions"
