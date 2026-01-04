"""
Abstract Base Class for all Study Modes.
This enforces a contract that every mode must implement.
Following SOLID principles - Interface Segregation.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class ModeResponse:
    """Standardized response object from any study mode"""
    content: str
    mode_name: str
    success: bool
    metadata: Optional[dict] = None


class IStudyMode(ABC):
    """
    Interface that all study modes must implement.
    This ensures consistency across the system.
    """
    
    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """
        Determines if this mode can handle the given query.
        
        Args:
            query: User's input question
            
        Returns:
            True if this mode should handle the query, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, query: str, context: dict) -> ModeResponse:
        """
        Executes the mode's core logic.
        
        Args:
            query: User's input question
            context: Dictionary containing vector_store, llm_client, etc.
            
        Returns:
            ModeResponse object with the result
        """
        pass
    
    @abstractmethod
    def get_mode_name(self) -> str:
        """Returns the name of this mode (e.g., 'MODE A: EXACT RECALL')"""
        pass
    
    @abstractmethod
    def get_system_prompt(self, query: str, retrieved_context: str) -> str:
        """
        Generates the system prompt for the LLM.
        
        Args:
            query: User's question
            retrieved_context: Text retrieved from vector store
            
        Returns:
            Formatted system prompt string
        """
        pass
