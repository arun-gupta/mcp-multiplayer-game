from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import os


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class ModelConfig:
    """Configuration for an LLM model"""
    name: str
    provider: ModelProvider
    model_id: str
    display_name: str
    description: str
    estimated_cost_per_1k_tokens: float
    max_tokens: int
    temperature: float
    is_available: bool = True
    requires_api_key: bool = True
    
    def __post_init__(self):
        # Check if model is actually available
        if self.provider == ModelProvider.OPENAI:
            self.is_available = bool(os.getenv("OPENAI_API_KEY"))
        elif self.provider == ModelProvider.ANTHROPIC:
            self.is_available = bool(os.getenv("ANTHROPIC_API_KEY"))
        elif self.provider == ModelProvider.OLLAMA:
            # For Ollama, check if the specific model is installed
            self.is_available = self._check_ollama_model_availability()
    
    def _check_ollama_model_status(self) -> str:
        """Check Ollama model lifecycle status: 'available', 'downloaded', 'need_download'"""
        try:
            import subprocess
            import json
            
            # First check if Ollama is running
            if not self._check_ollama_running():
                return "need_download"  # Can't check if Ollama isn't running
            
            # Check if model is installed
            installed = self._check_ollama_model_installed()
            if not installed:
                return "need_download"
            
            # Check if model is running
            running = self._check_ollama_model_running()
            if running:
                return "available"
            else:
                return "downloaded"
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return "need_download"
    
    def _check_ollama_model_availability(self) -> bool:
        """Check if a specific Ollama model is available and running"""
        return self._check_ollama_model_status() == "available"
    
    def _check_ollama_model_installed(self) -> bool:
        """Check if a specific Ollama model is installed"""
        try:
            import subprocess
            import json
            
            # Run 'ollama list' to get installed models
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse the plain text output
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header line
                    if line.strip():
                        parts = line.split()
                        if parts:
                            model_name = parts[0]
                            if self.model_id == model_name:
                                return True
                return False
            else:
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _check_ollama_model_running(self) -> bool:
        """Check if a specific Ollama model is currently running"""
        try:
            import subprocess
            import json
            
            # Run 'ollama ps' to get running models
            result = subprocess.run(['ollama', 'ps'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header line
                    if line.strip():
                        parts = line.split()
                        if parts:
                            model_name = parts[0]
                            if self.model_id == model_name:
                                return True
                return False
            else:
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _check_ollama_running(self) -> bool:
        """Fallback check to see if Ollama is running"""
        try:
            import subprocess
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False


class ModelRegistry:
    """Registry for managing different LLM models"""
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize with default model configurations"""
        default_models = [
            # OpenAI Models
            ModelConfig(
                name="gpt-4",
                provider=ModelProvider.OPENAI,
                model_id="gpt-4",
                display_name="GPT-4",
                description="Most capable GPT model, excellent reasoning and analysis",
                estimated_cost_per_1k_tokens=0.03,
                max_tokens=4096,
                temperature=0.1
            ),
            ModelConfig(
                name="gpt-4-turbo",
                provider=ModelProvider.OPENAI,
                model_id="gpt-4-turbo-preview",
                display_name="GPT-4 Turbo",
                description="Faster and more cost-effective than GPT-4",
                estimated_cost_per_1k_tokens=0.01,
                max_tokens=4096,
                temperature=0.1
            ),
            ModelConfig(
                name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                model_id="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                description="Fast and cost-effective for simpler tasks",
                estimated_cost_per_1k_tokens=0.002,
                max_tokens=4096,
                temperature=0.1
            ),
            
            # Anthropic Models
            ModelConfig(
                name="claude-3-sonnet",
                provider=ModelProvider.ANTHROPIC,
                model_id="claude-3-sonnet-20240229",
                display_name="Claude 3 Sonnet",
                description="Balanced performance and cost, excellent for strategy",
                estimated_cost_per_1k_tokens=0.015,
                max_tokens=4096,
                temperature=0.1
            ),
            ModelConfig(
                name="claude-3-haiku",
                provider=ModelProvider.ANTHROPIC,
                model_id="claude-3-haiku-20240307",
                display_name="Claude 3 Haiku",
                description="Fastest and most cost-effective Claude model",
                estimated_cost_per_1k_tokens=0.00025,
                max_tokens=4096,
                temperature=0.1
            ),
            
            # Ollama Models
            ModelConfig(
                name="llama2-7b",
                provider=ModelProvider.OLLAMA,
                model_id="llama2:7b",
                display_name="Llama2 7B",
                description="Local model, free but slower",
                estimated_cost_per_1k_tokens=0.0,
                max_tokens=4096,
                temperature=0.1,
                requires_api_key=False
            ),
            ModelConfig(
                name="llama2-13b",
                provider=ModelProvider.OLLAMA,
                model_id="llama2:13b",
                display_name="Llama2 13B",
                description="Larger local model, better quality",
                estimated_cost_per_1k_tokens=0.0,
                max_tokens=4096,
                temperature=0.1,
                requires_api_key=False
            ),
            ModelConfig(
                name="mistral-7b",
                provider=ModelProvider.OLLAMA,
                model_id="mistral:7b",
                display_name="Mistral 7B",
                description="High-quality local model",
                estimated_cost_per_1k_tokens=0.0,
                max_tokens=4096,
                temperature=0.1,
                requires_api_key=False
            ),
            ModelConfig(
                name="mistral-latest",
                provider=ModelProvider.OLLAMA,
                model_id="mistral:latest",
                display_name="Mistral Latest",
                description="Latest Mistral model, high quality",
                estimated_cost_per_1k_tokens=0.0,
                max_tokens=4096,
                temperature=0.1,
                requires_api_key=False
            ),
            ModelConfig(
                name="llama3-latest",
                provider=ModelProvider.OLLAMA,
                model_id="llama3:latest",
                display_name="Llama3 Latest",
                description="Latest Llama3 model, excellent performance",
                estimated_cost_per_1k_tokens=0.0,
                max_tokens=4096,
                temperature=0.1,
                requires_api_key=False
            ),
        ]
        
        for model in default_models:
            self.register_model(model)
    
    def register_model(self, model: ModelConfig):
        """Register a new model"""
        self.models[model.name] = model
    
    def get_model(self, name: str) -> Optional[ModelConfig]:
        """Get a model by name"""
        return self.models.get(name)
    
    def get_available_models(self) -> List[ModelConfig]:
        """Get all available models"""
        return [model for model in self.models.values() if model.is_available]
    
    def get_models_by_provider(self, provider: ModelProvider) -> List[ModelConfig]:
        """Get all models for a specific provider"""
        return [model for model in self.models.values() 
                if model.provider == provider and model.is_available]
    
    def get_model_info(self) -> Dict[str, Dict]:
        """Get information about all models for API response"""
        model_info = {}
        for name, model in self.models.items():
            # For Ollama models, check lifecycle status dynamically
            if model.provider == ModelProvider.OLLAMA:
                lifecycle_status = model._check_ollama_model_status()
                is_available = lifecycle_status == "available"
            else:
                lifecycle_status = "available" if model.is_available else "unavailable"
                is_available = model.is_available
            
            model_info[name] = {
                "name": model.name,
                "provider": model.provider.value,
                "display_name": model.display_name,
                "description": model.description,
                "estimated_cost_per_1k_tokens": model.estimated_cost_per_1k_tokens,
                "max_tokens": model.max_tokens,
                "temperature": model.temperature,
                "is_available": is_available,
                "lifecycle_status": lifecycle_status,
                "requires_api_key": model.requires_api_key,
                "unavailable_reason": self._get_unavailable_reason(model, is_available)
            }
        return model_info
    
    def _check_ollama_model_availability(self, model_id: str) -> bool:
        """Check if a specific Ollama model is available and running"""
        try:
            import subprocess
            
            # First check if Ollama is running
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False
            
            # Check if model is installed
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse the output line by line
                lines = result.stdout.strip().split('\n')
                installed_models = []
                
                # Skip the header line and parse model names
                for line in lines[1:]:  # Skip the "NAME ID SIZE MODIFIED" header
                    if line.strip():
                        # Extract the model name (first column)
                        parts = line.split()
                        if parts:
                            model_name = parts[0]
                            installed_models.append(model_name)
                
                # Check if this specific model is installed
                if model_id not in installed_models:
                    return False
                
                # Now check if the model is currently running
                result = subprocess.run(['ollama', 'ps'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    running_models = []
                    
                    # Skip the header line and parse running model names
                    for line in lines[1:]:  # Skip the "NAME ID SIZE PROCESSOR UNTIL" header
                        if line.strip():
                            parts = line.split()
                            if parts:
                                model_name = parts[0]
                                running_models.append(model_name)
                    
                    # Model is available if it's both installed AND running
                    return model_id in running_models
                else:
                    return False
            else:
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _get_unavailable_reason(self, model, is_available: bool) -> str:
        """Get the reason why a model is unavailable"""
        if is_available:
            return ""
        
        if model.provider == ModelProvider.OPENAI:
            return "OpenAI API key not found in environment variables"
        elif model.provider == ModelProvider.ANTHROPIC:
            return "Anthropic API key not found in environment variables"
        elif model.provider == ModelProvider.OLLAMA:
            # Get lifecycle status for better hints
            lifecycle_status = model._check_ollama_model_status()
            
            if lifecycle_status == "need_download":
                return f"Download with: ollama pull {model.model_id}"
            elif lifecycle_status == "downloaded":
                return f"Start with: ollama run {model.model_id}"
            else:
                return "Ollama is not accessible"
        else:
            return "Unknown error"


# Global registry instance
model_registry = ModelRegistry() 