"""
Configuration loader for MCP Multiplayer Game
Loads settings from config.json
"""
import json
import os
from typing import Dict, Any


class Config:
    """Configuration loader and manager"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from config.json"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        
        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
            print(f"✅ Configuration loaded from {config_path}")
        except FileNotFoundError:
            print(f"⚠️ Config file not found at {config_path}, using defaults")
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config.json: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config.json is missing"""
        return {
            "mcp": {
                "ports": {
                    "scout": 3001,
                    "strategist": 3002,
                    "executor": 3003
                },
                "host": "localhost",
                "protocol": "http"
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000
            },
            "streamlit": {
                "host": "0.0.0.0",
                "port": 8501
            },
            "models": {
                "default": "gpt-5-mini",
                "fallback": ["gpt-4", "claude-3-sonnet", "llama3.2:3b"]
            },
            "performance": {
                "mcp_coordination_timeout": 15,
                "agent_execution_timeout": 8,
                "enable_metrics": True
            }
        }
    
    def get(self, *keys, default=None) -> Any:
        """
        Get configuration value by nested keys
        
        Example:
            config.get('mcp', 'ports', 'scout')  # Returns 3001
            config.get('api', 'port')             # Returns 8000
        """
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def get_mcp_port(self, agent_name: str) -> int:
        """Get MCP port for a specific agent"""
        return self.get('mcp', 'ports', agent_name, default=3000)
    
    def get_mcp_host(self) -> str:
        """Get MCP host"""
        return self.get('mcp', 'host', default='localhost')
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.get('api', default={'host': '0.0.0.0', 'port': 8000})
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Get Streamlit configuration"""
        return self.get('streamlit', default={'host': '0.0.0.0', 'port': 8501})
    
    def get_default_model(self) -> str:
        """Get default model name"""
        return self.get('models', 'default', default='gpt-5-mini')
    
    def get_fallback_models(self) -> list:
        """Get fallback model list"""
        return self.get('models', 'fallback', default=['gpt-4', 'claude-3-sonnet', 'llama3.2:3b'])
    
    def get_mcp_coordination_timeout(self) -> int:
        """Get MCP coordination timeout"""
        return self.get('performance', 'mcp_coordination_timeout', default=15)
    
    def get_agent_execution_timeout(self) -> int:
        """Get agent execution timeout"""
        return self.get('performance', 'agent_execution_timeout', default=8)
    
    def is_metrics_enabled(self) -> bool:
        """Check if metrics are enabled"""
        return self.get('performance', 'enable_metrics', default=True)
    
    def reload(self):
        """Reload configuration from file"""
        self._config = None
        self._load_config()


# Singleton instance
config = Config()
