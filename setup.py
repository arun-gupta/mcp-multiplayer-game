#!/usr/bin/env python3
"""
Setup script for Multi-Agent Game Simulation
Helps users install dependencies and configure the environment
"""
import os
import sys
import subprocess
import platform

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed yet, that's okay
    pass


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Ollama is not installed or not in PATH")
    print("Please install Ollama from: https://ollama.ai/")
    return False


def install_ollama_models():
    """Install required Ollama models"""
    models = ["mistral", "llama2:7b"]
    
    for model in models:
        if not run_command(f"ollama pull {model}", f"Installing {model} model"):
            print(f"⚠️  Failed to install {model}. You can install it manually with: ollama pull {model}")
    
    return True


def create_virtual_environment():
    """Create a virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")


def install_python_dependencies():
    """Install Python dependencies"""
    # Determine the correct pip command for the virtual environment
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies")


def check_environment_variables():
    """Check and guide user on environment variables"""
    print("\n🔧 Environment Variables Setup")
    print("=" * 50)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("❌ OPENAI_API_KEY is not set")
        print("Please set your OpenAI API key:")
        if platform.system() == "Windows":
            print("set OPENAI_API_KEY=your-api-key-here")
        else:
            print("export OPENAI_API_KEY=your-api-key-here")
        print("\nYou can get an API key from: https://platform.openai.com/api-keys")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY is set")
    else:
        print("❌ ANTHROPIC_API_KEY is not set")
        print("Please set your Anthropic API key:")
        if platform.system() == "Windows":
            print("set ANTHROPIC_API_KEY=your-api-key-here")
        else:
            print("export ANTHROPIC_API_KEY=your-api-key-here")
        print("\nYou can get an API key from: https://console.anthropic.com/")


def main():
    """Main setup function"""
    print("🎮 Multi-Agent Game Simulation Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama():
        print("\n⚠️  Ollama is required for local models. Please install it first.")
        print("Visit: https://ollama.ai/")
        response = input("Continue with setup anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Install Ollama models (if Ollama is available)
    if check_ollama():
        install_ollama_models()
    
    # Check environment variables
    check_environment_variables()
    
    print("\n🎉 Setup completed!")
    print("=" * 50)
    print("To start the application:")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Set your API keys:")
    if platform.system() == "Windows":
        print("   set OPENAI_API_KEY=your-openai-api-key-here")
        print("   set ANTHROPIC_API_KEY=your-anthropic-api-key-here")
    else:
        print("   export OPENAI_API_KEY=your-openai-api-key-here")
        print("   export ANTHROPIC_API_KEY=your-anthropic-api-key-here")
    print("3. Run the application:")
    print("   python main.py")
    print("4. Open your browser to: http://localhost:8000")
    
    print("\n📚 For more information, see README.md")


if __name__ == "__main__":
    main() 