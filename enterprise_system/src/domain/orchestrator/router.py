"""
Enterprise Query Router - The Orchestration Brain
Routes queries to appropriate study modes based on intent detection.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import List, Optional
from src.domain.study_modes.base.interface import IStudyMode, ModeResponse
from src.domain.study_modes.recall.enhanced_recall import EnhancedRecallMode  # NEW: Optimized Mode A
from src.domain.study_modes.recall.exact_recall import ExactRecallMode
from src.domain.study_modes.recall.active_recall import ActiveRecallTester
from src.domain.study_modes.explainer.stuck_point import StuckPointExplainer
from src.domain.study_modes.synthesizer.concept_linker import ConceptLinker
from src.domain.study_modes.tutor.oral_revision import OralRevisionTutor
from src.core.logging.logger import LoggerFactory
from src.core.security.validator import InputValidator


class EnterpriseQueryRouter:
    """
    Central orchestration system for routing queries to study modes.
    
    Architecture:
    1. Validates input
    2. Detects intent
    3. Routes to appropriate mode
    4. Returns standardized response
    """
    
    def __init__(self, vector_store, llm_client):
        self.logger = LoggerFactory.get_logger(__name__)
        self.vector_store = vector_store
        self.llm_client = llm_client
        
        # Initialize all study modes
        self.modes: List[IStudyMode] = [
            EnhancedRecallMode(),       # MODE A Enhanced - Dual-layer lossless (NEW)
            StuckPointExplainer(),      # MODE B
            ConceptLinker(),            # MODE C
            OralRevisionTutor(),        # MODE D
            ActiveRecallTester(),       # MODE E
        ]

        
        self.logger.info(f"Router initialized with {len(self.modes)} study modes")
    
    def route(self, query: str) -> ModeResponse:
        """
        Main routing method.
        
        Args:
            query: User's input question
            
        Returns:
            ModeResponse from the appropriate handler
        """
        # Step 1: Validate and sanitize input
        is_valid, sanitized_query, error = InputValidator.validate_and_sanitize(query)
        
        if not is_valid:
            self.logger.warning(f"Invalid query rejected: {error}")
            return ModeResponse(
                content=f"❌ Invalid input: {error}",
                mode_name="ROUTER",
                success=False
            )
        
        self.logger.info(f"Routing query: {sanitized_query[:100]}...")
        
        # Step 2: Try each mode in priority order
        for mode in self.modes:
            if mode.can_handle(sanitized_query):
                self.logger.info(f"Query matched: {mode.get_mode_name()}")
                
                # Prepare context
                context = {
                    'vector_store': self.vector_store,
                    'llm_client': self.llm_client
                }
                
                # Execute mode
                try:
                    response = mode.execute(sanitized_query, context)
                    self.logger.info(f"Mode execution {'succeeded' if response.success else 'failed'}")
                    return response
                    
                except Exception as e:
                    self.logger.error(f"Mode execution error: {e}", exc_info=True)
                    return ModeResponse(
                        content=f"❌ Error executing {mode.get_mode_name()}: {str(e)}",
                        mode_name=mode.get_mode_name(),
                        success=False
                    )
        
        # Step 3: No specialized mode matched - Default to Enhanced Mode A
        self.logger.info("No specialized mode matched - Defaulting to Enhanced Mode A (General Query)")
        
        # Use the first mode (EnhancedRecallMode) as default
        fallback_mode = self.modes[0] 
        
        try:
            # Prepare context
            context = {
                'vector_store': self.vector_store,
                'llm_client': self.llm_client
            }
            return fallback_mode.execute(sanitized_query, context)
            
        except Exception as e:
            self.logger.error(f"Fallback mode execution error: {e}", exc_info=True)
            return ModeResponse(
                content=f"❌ Error executing fallback mode: {str(e)}",
                mode_name="FALLBACK",
                success=False
            )
    
    def get_available_modes(self) -> List[str]:
        """Get list of all available mode names"""
        return [mode.get_mode_name() for mode in self.modes]
