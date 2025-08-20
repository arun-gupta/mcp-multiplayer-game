#!/bin/bash

echo "🔍 Docker Hub Authentication Debug Script"
echo "=========================================="

# Check if we're in GitHub Actions
if [ -n "$GITHUB_ACTIONS" ]; then
    echo "✅ Running in GitHub Actions"
    
    # Check if secrets are available (they won't be visible, but we can check if they exist)
    if [ -n "$DOCKERHUB_USERNAME" ]; then
        echo "✅ DOCKERHUB_USERNAME is set"
        echo "   Username: ${DOCKERHUB_USERNAME:0:3}***"
    else
        echo "❌ DOCKERHUB_USERNAME is NOT set"
    fi
    
    if [ -n "$DOCKERHUB_TOKEN" ]; then
        echo "✅ DOCKERHUB_TOKEN is set"
        echo "   Token: ${DOCKERHUB_TOKEN:0:10}***"
    else
        echo "❌ DOCKERHUB_TOKEN is NOT set"
    fi
    
    echo ""
    echo "📋 GitHub Secrets Status:"
    echo "   - Go to: https://github.com/arun-gupta/mcp-multiplayer-game/settings/secrets/actions"
    echo "   - Check if DOCKERHUB_USERNAME and DOCKERHUB_TOKEN are configured"
    
else
    echo "ℹ️  Running locally - GitHub secrets not available"
fi

echo ""
echo "🔧 Common Issues and Solutions:"
echo "==============================="
echo ""
echo "1. ❌ 'Repository does not exist'"
echo "   Solution: Create repository on Docker Hub first"
echo "   URL: https://hub.docker.com/repositories"
echo ""
echo "2. ❌ 'Insufficient scope'"
echo "   Solution: Create new access token with 'Read & Write' permissions"
echo "   URL: https://hub.docker.com/settings/security"
echo ""
echo "3. ❌ '401 Unauthorized'"
echo "   Solution: Check username/token in GitHub secrets"
echo "   - Username should match your Docker Hub username exactly"
echo "   - Token should be an access token (not password)"
echo ""
echo "4. ❌ 'Access denied'"
echo "   Solution: Ensure repository exists and you have write access"
echo ""
echo "📝 Setup Checklist:"
echo "=================="
echo "□ Docker Hub repository exists: arungupta/mcp-multiplayer-game"
echo "□ Access token created with 'Read & Write' permissions"
echo "□ GitHub secret DOCKERHUB_USERNAME = your Docker Hub username"
echo "□ GitHub secret DOCKERHUB_TOKEN = your access token (not password)"
echo "□ Repository visibility allows your account access"
