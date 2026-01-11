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
        
        # Session Memory
        self.last_query: Optional[str] = None
        self.last_mode: Optional[IStudyMode] = None
        
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
        Main routing method with session memory support.
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
        
        # --- CONTINUATION LOGIC ---
        continuation_keywords = {'yes', 'yep', 'continue', 'next', 'ok', 'go on', 'more'}
        if sanitized_query.lower().strip() in continuation_keywords and self.last_mode:
            self.logger.info(f"Continuation detected for mode: {self.last_mode.get_mode_name()}")
            
            # Case 1: Page Increment
            import re
            page_match = re.search(r'page\s+(\d+)', self.last_query.lower())
            if page_match:
                next_page = int(page_match.group(1)) + 1
                sanitized_query = f"Explain page {next_page}"
            
            # Case 2: Time Segment Increment (Transcript Summary)
            else:
                # Optimized regex for any variation: 10:00 to 20:00, 10:00-20:00, 10:00 — 20:00
                time_match = re.search(r'(\d{1,2}:\d{2})\s*(?:to|—|-|—)\s*(\d{1,2}:\d{2})', self.last_query)
                if time_match:
                    start_str, end_str = time_match.group(1), time_match.group(2)
                    
                    def time_to_sec(t):
                        m, s = map(int, t.split(':'))
                        return m * 60 + s
                    
                    def sec_to_time(s):
                        m = s // 60
                        sec = s % 60
                        return f"{m:02}:{sec:02}"
                    
                    start_sec, end_sec = time_to_sec(start_str), time_to_sec(end_str)
                    duration = end_sec - start_sec
                    if duration <= 0: duration = 600 # Default 10 min
                    
                    new_start = end_sec
                    new_end = end_sec + duration
                    sanitized_query = f"Summarize segment {sec_to_time(new_start)} to {sec_to_time(new_end)} of the transcript"
                else:
                    # FIXED: Don't create infinite loop - just pass through
                    self.logger.warning(f"No time pattern found in continuation. Using original query.")
                    # Don't modify the query if we can't find a pattern
        # ---------------------------

        self.logger.info(f"Routing query: {sanitized_query[:100]}...")
        
        # Step 2: Try each mode in priority order
        for mode in self.modes:
            if mode.can_handle(sanitized_query):
                self.logger.info(f"Query matched: {mode.get_mode_name()}")
                
                # Update Session Memory
                self.last_query = sanitized_query
                self.last_mode = mode
                
                # Prepare context
                context = {
                    'vector_store': self.vector_store,
                    'llm_client': self.llm_client
                }
                
                # Execute mode
                try:
                    response = mode.execute(sanitized_query, context)
                    return response
                except Exception as e:
                    self.logger.error(f"Mode execution error: {e}", exc_info=True)
                    return ModeResponse(
                        content=f"❌ Error: {str(e)}",
                        mode_name=mode.get_mode_name(),
                        success=False
                    )
        
        # Step 3: Fallback 
        fallback_mode = self.modes[0] 
        self.last_query = sanitized_query
        self.last_mode = fallback_mode
        
        try:
            context = {'vector_store': self.vector_store, 'llm_client': self.llm_client}
            return fallback_mode.execute(sanitized_query, context)
        except Exception as e:
            return ModeResponse(content=f"❌ Error: {str(e)}", mode_name="FALLBACK", success=False)
    
    def get_available_modes(self) -> List[str]:
        """Get list of all available mode names"""
        return [mode.get_mode_name() for mode in self.modes]
