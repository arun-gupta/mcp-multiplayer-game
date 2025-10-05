#!/usr/bin/env python3
"""
Shared LLM Connection Module
Provides a single LLM connection instance shared across all agents
to reduce initialization overhead and improve resource utilization
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import Ollama


class SharedLLMConnection:
    """
    Shared LLM connection across all agents

    This class ensures that all agents use the same LLM instance,
    reducing initialization overhead and connection pooling costs.
    """

    def __init__(self, model_name: str = "llama3.2:1b"):
        """
        Initialize shared LLM connection

        Args:
            model_name: Name of the LLM model to use (e.g., "gpt-5-mini", "claude-3-5-haiku", "llama3.2:1b")
        """
        self.model_name = model_name
        self.llm = None
        self.connection_count = 0
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize shared LLM connection based on model name"""
        try:
            if "gpt" in self.model_name.lower():
                # OpenAI models
                self.llm = ChatOpenAI(model=self.model_name, timeout=30.0)
                print(f"✅ Shared LLM connection initialized: OpenAI {self.model_name}")
            elif "claude" in self.model_name.lower():
                # Anthropic models
                self.llm = ChatAnthropic(model=self.model_name, timeout=30.0)
                print(f"✅ Shared LLM connection initialized: Anthropic {self.model_name}")
            else:
                # Local models via Ollama
                self.llm = Ollama(model=self.model_name, timeout=30.0)
                print(f"✅ Shared LLM connection initialized: Ollama {self.model_name}")
        except Exception as e:
            print(f"❌ Failed to initialize shared LLM: {e}")
            # Fallback to Ollama with smallest model
            try:
                self.llm = Ollama(model="llama3.2:1b", timeout=30.0)
                self.model_name = "llama3.2:1b"
                print(f"✅ Fallback to Ollama llama3.2:1b")
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                raise RuntimeError(f"Unable to initialize any LLM connection: {fallback_error}")

    def get_connection(self):
        """
        Get shared LLM connection

        Returns:
            The shared LLM instance
        """
        self.connection_count += 1
        return self.llm

    def release_connection(self):
        """
        Release LLM connection (decrements usage counter)

        Note: This doesn't actually close the connection, just tracks usage
        """
        self.connection_count = max(0, self.connection_count - 1)

    def get_stats(self) -> dict:
        """
        Get connection statistics

        Returns:
            Dictionary with model name and connection count
        """
        return {
            "model_name": self.model_name,
            "connection_count": self.connection_count,
            "connection_type": self._get_connection_type()
        }

    def _get_connection_type(self) -> str:
        """Get the type of LLM connection"""
        if isinstance(self.llm, ChatOpenAI):
            return "OpenAI"
        elif isinstance(self.llm, ChatAnthropic):
            return "Anthropic"
        elif isinstance(self.llm, Ollama):
            return "Ollama"
        else:
            return "Unknown"
