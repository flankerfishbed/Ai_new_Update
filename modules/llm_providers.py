"""
LLM Provider Module

This module provides a factory pattern for different LLM providers (OpenAI, Anthropic, etc.).
Each provider returns clean, explainable output suitable for LLM prompt context.
"""

import openai
import anthropic
import requests
import json
from typing import Dict, Any, List
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    Ensures consistent interface across different AI services.
    """
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate response from the LLM provider.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with response and metadata
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            return {
                'success': True,
                'response': response.choices[0].message.content,
                'model': self.model_name,
                'provider': 'OpenAI',
                'usage': response.usage.dict() if response.usage else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'OpenAI'
            }


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider implementation."""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 4000),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'success': True,
                'response': response.content[0].text,
                'model': self.model_name,
                'provider': 'Anthropic',
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'Anthropic'
            }


class GroqProvider(LLMProvider):
    """Groq API provider implementation."""
    
    def __init__(self, api_key: str, model_name: str = "llama3-8b-8192"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.groq.com/openai/v1"
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', 4000)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result['choices'][0]['message']['content'],
                    'model': self.model_name,
                    'provider': 'Groq',
                    'usage': result.get('usage')
                }
            else:
                return {
                    'success': False,
                    'error': f"API error: {response.status_code} - {response.text}",
                    'provider': 'Groq'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'Groq'
            }


class MistralProvider(LLMProvider):
    """Mistral AI API provider implementation."""
    
    def __init__(self, api_key: str, model_name: str = "mistral-large-latest"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.mistral.ai/v1"
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', 4000)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result['choices'][0]['message']['content'],
                    'model': self.model_name,
                    'provider': 'Mistral',
                    'usage': result.get('usage')
                }
            else:
                return {
                    'success': False,
                    'error': f"API error: {response.status_code} - {response.text}",
                    'provider': 'Mistral'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': 'Mistral'
            }


class LLMProviderFactory:
    """
    Factory class for creating LLM provider instances.
    Provides a clean interface for selecting different AI providers.
    """
    
    def __init__(self):
        self.providers = {
            'OpenAI': OpenAIProvider,
            'Anthropic': AnthropicProvider,
            'Groq': GroqProvider,
            'Mistral': MistralProvider
        }
    
    def create_provider(self, provider_name: str, api_key: str, model_name: str) -> LLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_name: Name of the provider (OpenAI, Anthropic, etc.)
            api_key: API key for the provider
            model_name: Model name to use
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider_name not in self.providers:
            raise ValueError(f"Unsupported provider: {provider_name}. Supported providers: {list(self.providers.keys())}")
        
        provider_class = self.providers[provider_name]
        return provider_class(api_key, model_name)
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported providers."""
        return list(self.providers.keys())
    
    def get_available_models(self, provider_name: str) -> List[str]:
        """Get available models for a specific provider."""
        model_options = {
            "OpenAI": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "Anthropic": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
            "Groq": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"],
            "Mistral": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"]
        }
        
        return model_options.get(provider_name, []) 