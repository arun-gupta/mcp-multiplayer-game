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
            # For Ollama, we'll assume it's available if we can import it
            try:
                from langchain_community.llms import Ollama
                self.is_available = True
            except ImportError:
                self.is_available = False


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
        return {
            name: {
                "name": model.name,
                "provider": model.provider.value,
                "display_name": model.display_name,
                "description": model.description,
                "estimated_cost_per_1k_tokens": model.estimated_cost_per_1k_tokens,
                "max_tokens": model.max_tokens,
                "temperature": model.temperature,
                "is_available": model.is_available,
                "requires_api_key": model.requires_api_key
            }
            for name, model in self.models.items()
        }


# Global registry instance
model_registry = ModelRegistry() 