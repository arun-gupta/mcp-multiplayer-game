from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
from .registry import ModelConfig, ModelProvider, model_registry


class ModelFactory:
    """Factory for creating LLM instances from model configurations"""
    
    @staticmethod
    def create_llm(model_name: str) -> Optional[object]:
        """Create an LLM instance from a model name"""
        model_config = model_registry.get_model(model_name)
        if not model_config or not model_config.is_available:
            return None
        
        return ModelFactory._create_llm_from_config(model_config)
    
    @staticmethod
    def create_llm_from_config(model_config: ModelConfig) -> Optional[object]:
        """Create an LLM instance from a model configuration"""
        return ModelFactory._create_llm_from_config(model_config)
    
    @staticmethod
    def _create_llm_from_config(model_config: ModelConfig) -> Optional[object]:
        """Internal method to create LLM from config"""
        try:
            if model_config.provider == ModelProvider.OPENAI:
                return ChatOpenAI(
                    model=model_config.model_id,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens
                )
            
            elif model_config.provider == ModelProvider.ANTHROPIC:
                return ChatAnthropic(
                    model=model_config.model_id,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens
                )
            
            elif model_config.provider == ModelProvider.OLLAMA:
                return Ollama(
                    model=model_config.model_id,
                    temperature=model_config.temperature
                )
            
            else:
                print(f"Unknown provider: {model_config.provider}")
                return None
                
        except Exception as e:
            print(f"Error creating LLM for {model_config.name}: {e}")
            return None
    
    @staticmethod
    def get_default_models() -> dict:
        """Dynamically assign available models to agents"""
        # Get all available models
        available_models = model_registry.get_available_models()
        
        # Separate models by provider type
        cloud_models = [model for model in available_models if model.provider in [ModelProvider.OPENAI, ModelProvider.ANTHROPIC]]
        local_models = [model for model in available_models if model.provider == ModelProvider.OLLAMA]
        
        # Assign models based on availability and preferences
        assignments = {}
        
        # Scout: Prefer cloud models for reliability, fallback to local
        if cloud_models:
            # Prefer GPT-4 if available, otherwise first available cloud model
            scout_model = next((model.name for model in cloud_models if "gpt-4" in model.name), cloud_models[0].name)
        elif local_models:
            scout_model = local_models[0].name
        else:
            scout_model = "gpt-4"  # Fallback if no models available
        
        # Strategist: Prefer Claude for strategy, fallback to other cloud, then local
        if any("claude" in model.name for model in cloud_models):
            strategist_model = next(model.name for model in cloud_models if "claude" in model.name)
        elif cloud_models:
            strategist_model = cloud_models[0].name
        elif local_models:
            strategist_model = local_models[0].name
        else:
            strategist_model = "claude-3-sonnet"  # Fallback
        
        # Executor: Prefer local models for execution, fallback to cloud
        if local_models:
            executor_model = local_models[0].name
        elif cloud_models:
            executor_model = cloud_models[0].name
        else:
            executor_model = "mistral-latest"  # Fallback
        
        assignments = {
            "scout": scout_model,
            "strategist": strategist_model,
            "executor": executor_model
        }
        
        return assignments
    
    @staticmethod
    def validate_model_availability(model_name: str) -> bool:
        """Check if a model is available"""
        model_config = model_registry.get_model(model_name)
        return model_config is not None and model_config.is_available 