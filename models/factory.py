from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatLiteLLM
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
                # For newer models, don't use max_tokens or temperature parameters
                if 'gpt-5' in model_config.model_id or 'gpt-4o' in model_config.model_id:
                    return ChatOpenAI(
                        model=model_config.model_id
                    )
                else:
                    return ChatOpenAI(
                        model=model_config.model_id,
                        temperature=model_config.temperature,
                        max_completion_tokens=model_config.max_tokens
                    )
            
            elif model_config.provider == ModelProvider.ANTHROPIC:
                # For LiteLLM, use the proper format
                return ChatLiteLLM(
                    model=f"anthropic/{model_config.model_id}",
                    temperature=model_config.temperature,
                    max_completion_tokens=model_config.max_tokens
                )
            
            elif model_config.provider == ModelProvider.OLLAMA:
                # Use ChatLiteLLM with ollama/ prefix for CrewAI compatibility
                return ChatLiteLLM(
                    model=f"ollama/{model_config.model_id}",
                    temperature=model_config.temperature,
                    api_base="http://localhost:11434"
                )
            
            else:
                print(f"Unknown provider: {model_config.provider}")
                return None
                
        except Exception as e:
            print(f"Error creating LLM for {model_config.name}: {e}")
            return None
    
    @staticmethod
    def get_default_models() -> dict:
        """Dynamically assign only truly available models to agents"""
        # Get all models and check their actual availability
        all_models = list(model_registry.models.values())
        
        # Filter for truly available models (running for Ollama, API keys for cloud)
        truly_available_models = []
        for model in all_models:
            if model.provider in [ModelProvider.OPENAI, ModelProvider.ANTHROPIC]:
                # Cloud models are available if API keys are set
                if model.is_available:
                    truly_available_models.append(model)
            elif model.provider == ModelProvider.OLLAMA:
                # Ollama models are available only if running
                if model._check_ollama_model_status() == "available":
                    truly_available_models.append(model)
        
        # Separate by provider type
        cloud_models = [model for model in truly_available_models if model.provider in [ModelProvider.OPENAI, ModelProvider.ANTHROPIC]]
        local_models = [model for model in truly_available_models if model.provider == ModelProvider.OLLAMA]
        
        # Assign models based on availability and preferences
        assignments = {}
        
        # Priority: GPT-5 Mini > Claude 4.5 Sonnet > Claude 3.5 Haiku > Claude 3.5 Sonnet > Claude 3 > Llama 3.2 > others
        # Scout: Prefer GPT-5 Mini (reliable and fast), fallback to Claude models
        if any("gpt-5-mini" in model.name for model in cloud_models):
            scout_model = "gpt-5-mini"  # Prefer GPT-5 Mini for reliability
        elif any("claude-4.5-sonnet" in model.name for model in cloud_models):
            scout_model = "claude-4.5-sonnet"  # Fallback to Claude 4.5 Sonnet
        elif any("claude-3.5-haiku" in model.name for model in cloud_models):
            scout_model = "claude-3.5-haiku"  # Fallback to Claude 3.5 Haiku
        elif any("claude-3.5-sonnet" in model.name for model in cloud_models):
            scout_model = "claude-3.5-sonnet"  # Fallback to Claude 3.5 Sonnet
        elif any("claude-3-sonnet" in model.name for model in cloud_models):
            scout_model = "claude-3-sonnet"  # Fallback to Claude 3
        elif any("gpt-5-mini" in model.name for model in cloud_models):
            scout_model = "gpt-5-mini"  # Then GPT-5 Mini
        elif any("gpt-5" in model.name for model in cloud_models):
            scout_model = next(model.name for model in cloud_models if "gpt-5" in model.name)
        elif any("llama3.2-1b" in model.name.lower() for model in local_models):
            scout_model = "llama3.2-1b"  # Prefer 1B for speed
        elif any("llama3.2" in model.name.lower() for model in local_models):
            scout_model = next(model.name for model in local_models if "llama3.2" in model.name.lower())
        elif cloud_models:
            scout_model = cloud_models[0].name
        elif local_models:
            scout_model = local_models[0].name
        else:
            scout_model = "gpt-5-mini"  # Fallback if no models available

        # Strategist: Prefer GPT-5 Mini (reliable), fallback to Claude models
        if any("gpt-5-mini" in model.name for model in cloud_models):
            strategist_model = "gpt-5-mini"  # Prefer GPT-5 Mini for reliability
        elif any("claude-4.5-sonnet" in model.name for model in cloud_models):
            strategist_model = "claude-4.5-sonnet"  # Fallback to Claude 4.5 Sonnet
        elif any("claude-3.5-haiku" in model.name for model in cloud_models):
            strategist_model = "claude-3.5-haiku"  # Fallback to Claude 3.5 Haiku
        elif any("claude-3.5-sonnet" in model.name for model in cloud_models):
            strategist_model = "claude-3.5-sonnet"  # Fallback to Claude 3.5 Sonnet
        elif any("claude-3-sonnet" in model.name for model in cloud_models):
            strategist_model = "claude-3-sonnet"  # Fallback to Claude 3
        elif any("gpt-5-mini" in model.name for model in cloud_models):
            strategist_model = "gpt-5-mini"  # Then GPT-5 Mini
        elif any("gpt-5" in model.name for model in cloud_models):
            strategist_model = next(model.name for model in cloud_models if "gpt-5" in model.name)
        elif any("llama3.2-1b" in model.name.lower() for model in local_models):
            strategist_model = "llama3.2-1b"  # Prefer 1B for speed
        elif any("llama3.2" in model.name.lower() for model in local_models):
            strategist_model = next(model.name for model in local_models if "llama3.2" in model.name.lower())
        elif cloud_models:
            strategist_model = cloud_models[0].name
        elif local_models:
            strategist_model = local_models[0].name
        else:
            strategist_model = "gpt-5-mini"  # Fallback

        # Executor: Prefer GPT-5 Mini (reliable), fallback to Claude models
        if any("gpt-5-mini" in model.name for model in cloud_models):
            executor_model = "gpt-5-mini"  # Prefer GPT-5 Mini for reliability
        elif any("claude-4.5-sonnet" in model.name for model in cloud_models):
            executor_model = "claude-4.5-sonnet"  # Fallback to Claude 4.5 Sonnet
        elif any("claude-3.5-haiku" in model.name for model in cloud_models):
            executor_model = "claude-3.5-haiku"  # Fallback to Claude 3.5 Haiku
        elif any("claude-3.5-sonnet" in model.name for model in cloud_models):
            executor_model = "claude-3.5-sonnet"  # Fallback to Claude 3.5 Sonnet
        elif any("claude-3-sonnet" in model.name for model in cloud_models):
            executor_model = "claude-3-sonnet"  # Fallback to Claude 3
        elif any("gpt-5-mini" in model.name for model in cloud_models):
            executor_model = "gpt-5-mini"  # Then GPT-5 Mini
        elif any("gpt-5" in model.name for model in cloud_models):
            executor_model = next(model.name for model in cloud_models if "gpt-5" in model.name)
        elif any("llama3.2-1b" in model.name.lower() for model in local_models):
            executor_model = "llama3.2-1b"  # Prefer 1B for speed
        elif any("llama3.2" in model.name.lower() for model in local_models):
            executor_model = next(model.name for model in local_models if "llama3.2" in model.name.lower())
        elif cloud_models:
            executor_model = cloud_models[0].name
        elif local_models:
            executor_model = local_models[0].name
        else:
            executor_model = "gpt-5-mini"  # Fallback to cloud model
        
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
        if model_config is None:
            return False
        
        # For Ollama models, check dynamic availability (running status)
        if model_config.provider == ModelProvider.OLLAMA:
            return model_config._check_ollama_model_status() == "available"
        else:
            # For cloud models, use the static availability check
            return model_config.is_available
    
    @staticmethod
    def create_llm_for_agent(agent_id: str, model_name: str) -> Optional[object]:
        """Create an LLM instance for a specific agent"""
        return ModelFactory.create_llm(model_name) 