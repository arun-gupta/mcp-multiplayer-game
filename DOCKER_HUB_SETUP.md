# Docker Hub Setup Guide

## 🔐 Required Permissions and Setup

### 1. Create Docker Hub Repository

1. **Go to Docker Hub**: https://hub.docker.com/
2. **Sign in** with your account
3. **Create Repository**:
   - Click "Create Repository"
   - Name: `mcp-multiplayer-game`
   - Visibility: Public or Private
   - Description: "Multi-Agent Game Simulation with MCP Protocol"

### 2. Create Docker Hub Access Token

1. **Go to Account Settings**: https://hub.docker.com/settings/security
2. **Create Access Token**:
   - Click "New Access Token"
   - Name: `github-actions-mcp-game`
   - Permissions: `Read & Write`
   - **Copy the token** (you won't see it again!)

### 3. Set GitHub Secrets

1. **Go to your GitHub repo**: Settings → Secrets and variables → Actions
2. **Add Repository Secrets**:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: The access token you created

### 4. Verify Permissions

The access token needs these permissions:
- ✅ `repository:read`
- ✅ `repository:write`
- ✅ `repository:delete` (for cache management)

## 🚀 Benefits of Docker Hub Push

### **Deployment Ready**
- **Pull anywhere**: `docker pull arun-gupta/mcp-multiplayer-game`
- **Cloud deployment**: Works on AWS, GCP, Azure, etc.
- **Easy sharing**: Others can run your app

### **Better Caching**
- **Layer caching**: Faster subsequent builds
- **Registry cache**: Shared across all builds
- **Dependency caching**: Pre-built layers

### **CI/CD Integration**
- **Automated deployment**: Push triggers deployments
- **Version tagging**: Automatic version management
- **Rollback capability**: Easy to revert to previous versions

## 🔧 Troubleshooting

### **"Repository does not exist"**
- Create the repository on Docker Hub first
- Check repository name matches exactly

### **"Insufficient scope"**
- Create new access token with `Read & Write` permissions
- Ensure token has repository access

### **"Authorization failed"**
- Check `DOCKERHUB_USERNAME` matches your Docker Hub username
- Verify `DOCKERHUB_TOKEN` is the access token (not password)

## 📊 Current Status

- ✅ **Build**: Working (AMD64 optimized)
- ✅ **Test**: All tests passing
- ⏳ **Push**: Requires Docker Hub setup
- ⏳ **Deploy**: Ready once push is working
