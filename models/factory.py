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
        """Get default model assignments for agents"""
        return {
            "scout": "gpt-4",
            "strategist": "claude-3-sonnet", 
            "executor": "llama2-7b"
        }
    
    @staticmethod
    def validate_model_availability(model_name: str) -> bool:
        """Check if a model is available"""
        model_config = model_registry.get_model(model_name)
        return model_config is not None and model_config.is_available 