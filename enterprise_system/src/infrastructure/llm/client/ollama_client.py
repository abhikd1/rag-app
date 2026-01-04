"""
LLM Client abstraction layer.
Wraps Ollama with a clean interface, making it easy to swap for OpenAI, Anthropic, etc.
"""

from typing import Optional, Dict, Any
import ollama
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.core.config.settings import config
from src.core.logging.logger import LoggerFactory


class LLMClient:
    """
    Abstraction over LLM operations.
    Currently uses Ollama but can be swapped for any LLM provider.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
        self.model_name = config.llm.model_name
        self.default_temperature = config.llm.temperature
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion from the LLM.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing 'response' and other metadata
        """
        if temperature is None:
            temperature = self.default_temperature
        
        options = {
            'temperature': temperature,
            **kwargs
        }
        
        if max_tokens:
            options['num_predict'] = max_tokens
        
        try:
            self.logger.debug(f"Generating completion (temp={temperature})")
            
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options=options
            )
            
            self.logger.debug(f"Generation complete ({len(response.get('response', ''))} chars)")
            return response
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return {
                'response': f"Error: Failed to generate response - {str(e)}",
                'error': True
            }
    
    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate with automatic retry on failure.
        
        Args:
            prompt: The input prompt
            max_retries: Maximum number of retry attempts
            **kwargs: Additional parameters for generate()
            
        Returns:
            Dictionary containing 'response' and other metadata
        """
        for attempt in range(max_retries):
            try:
                response = self.generate(prompt, **kwargs)
                if not response.get('error'):
                    return response
                
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} error: {e}")
                if attempt == max_retries - 1:
                    return {
                        'response': f"Error: All {max_retries} attempts failed",
                        'error': True
                    }
        
        return {
            'response': "Error: Maximum retries exceeded",
            'error': True
        }
