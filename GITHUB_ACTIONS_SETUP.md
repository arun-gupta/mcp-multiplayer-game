# 🚀 GitHub Actions Setup Guide

This guide explains how to set up automatic Docker builds and pushes to Docker Hub using GitHub Actions.

## 📋 Prerequisites

1. **Docker Hub Account**
   - Create account at [Docker Hub](https://hub.docker.com/)
   - Note your username

2. **Docker Hub Access Token**
   - Go to Docker Hub → Account Settings → Security
   - Click "New Access Token"
   - Give it a name (e.g., "GitHub Actions")
   - Copy the token (you'll need it for GitHub secrets)

3. **GitHub Repository**
   - Your repository should be on GitHub
   - You need admin access to add secrets

## 🔧 Setup Steps

### **1. Create Docker Hub Repository**

1. Go to [Docker Hub](https://hub.docker.com/)
2. Click "Create Repository"
3. Name it: `mcp-multiplayer-game`
4. Make it public or private (your choice)
5. Note the full name: `your-username/mcp-multiplayer-game`

### **2. Add GitHub Secrets**

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

#### **DOCKERHUB_USERNAME**
- **Name**: `DOCKERHUB_USERNAME`
- **Value**: Your Docker Hub username

#### **DOCKERHUB_TOKEN**
- **Name**: `DOCKERHUB_TOKEN`
- **Value**: Your Docker Hub access token

### **3. Update Workflow Configuration**

Edit `.github/workflows/docker-test-build.yml`:

```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: your-username/mcp-multiplayer-game  # Change this!
```

Replace `your-username` with your actual Docker Hub username.

## 🎯 How It Works

### **Triggers**
- **Push to main**: Builds and pushes new image
- **Pull Request**: Builds image for testing (doesn't push)
- **Tags (v*)**: Creates versioned releases

### **Workflow Steps**
1. **Test**: Runs `test_installation.py`
2. **Build**: Creates Docker image with metadata
3. **Push**: Uploads to Docker Hub (main branch only)
4. **Deploy**: Sends notification

### **Image Tags**
- `main`: Latest from main branch
- `v1.0.0`: Version tags
- `main-sha-abc123`: Commit-specific tags

## 🚀 Usage

### **Automatic Builds**
Every push to main will:
1. Run tests
2. Build Docker image
3. Push to Docker Hub
4. Send notification

### **Manual Trigger**
You can also trigger manually:
1. Go to **Actions** tab
2. Select "Test, Build and Push Docker Image"
3. Click **Run workflow**

### **Version Releases**
To create a versioned release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

This will create a tagged Docker image: `your-username/mcp-multiplayer-game:v1.0.0`

## 📊 Monitoring

### **Check Status**
- Go to **Actions** tab in GitHub
- View workflow runs and logs
- See build status and any errors

### **Docker Hub**
- Check your Docker Hub repository
- See all pushed images and tags
- Monitor image pulls and usage

## 🔧 Troubleshooting

### **Common Issues**

1. **"Authentication failed"**
   - Check `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets
   - Verify Docker Hub access token is valid

2. **"Repository not found"**
   - Ensure Docker Hub repository exists
   - Check `IMAGE_NAME` in workflow file

3. **"Build failed"**
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt
   - Review build logs in Actions tab

4. **"Test failed"**
   - Fix issues in `test_installation.py`
   - Ensure all dependencies are available

### **Debug Mode**
To debug workflow issues:
1. Go to Actions tab
2. Click on failed workflow
3. Click on failed job
4. Review step logs

## 📈 Advanced Configuration

### **Multi-Platform Builds**
The workflow builds for:
- `linux/amd64` (Intel/AMD)
- `linux/arm64` (Apple Silicon, ARM)

### **Caching**
- Uses GitHub Actions cache for faster builds
- Caches Docker layers between runs

### **Security**
- Only pushes on main branch (not PRs)
- Uses Docker Hub access tokens (not passwords)
- Minimal permissions required

## 🎯 Next Steps

After setup:

1. **Test the workflow**:
   ```bash
   git push origin main
   ```

2. **Check Docker Hub**:
   - Verify image was pushed
   - Test pulling the image

3. **Update documentation**:
   - Add Docker Hub image links to README
   - Update deployment instructions

4. **Monitor usage**:
   - Track image pulls
   - Monitor build times
   - Check for any issues

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Docker Buildx](https://docs.docker.com/buildx/)
- [GitHub Actions for Docker](https://docs.docker.com/ci-cd/github-actions/)

---

**Happy Building! 🐳**
