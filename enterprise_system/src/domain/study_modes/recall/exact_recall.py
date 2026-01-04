"""
MODE A: EXACT RECALL
Returns word-for-word text from specific pages or sections.
No summaries, no explanations - pure lossless retrieval.
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.domain.study_modes.base.interface import IStudyMode, ModeResponse
from src.core.logging.logger import LoggerFactory
from langchain_core.documents import Document


class ExactRecallMode(IStudyMode):
    """
    MODE A: Exact Recall Implementation
    Provides lossless, word-for-word text retrieval.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
    
    def get_mode_name(self) -> str:
        return "MODE A: EXACT RECALL"
    
    def can_handle(self, query: str) -> bool:
        """
        Detects if query requests exact recall.
        
        Triggers:
        - "Page X"
        - "What is written on..."
        - "MODE: A"
        - "exact text"
        - "verbatim"
        """
        query_lower = query.lower().strip()
        
        # Explicit mode selection
        if query_lower.startswith('mode: a') or query_lower.startswith('mode:a'):
            return True
        
        # Page number queries
        if self._extract_page_number(query):
            return True
        
        # Exact recall keywords
        exact_keywords = [
            'exact text',
            'word for word',
            'verbatim',
            'lossless',
            'raw text',
            'what is written',
            'what does it say',
            'show me the text'
        ]
        
        return any(keyword in query_lower for keyword in exact_keywords)
    
    def _extract_page_number(self, query: str) -> int:
        """Extract page number from query"""
        patterns = [
            r'page\s+(\d+)',
            r'pg\s+(\d+)',
            r'p\.?\s*(\d+)',
        ]
        
        query_lower = query.lower()
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return int(match.group(1))
        return None
    
    def execute(self, query: str, context: dict) -> ModeResponse:
        """
        Execute exact recall retrieval.
        
        Args:
            query: User's question
            context: Dict with 'vector_store' key
            
        Returns:
            ModeResponse with exact text
        """
        self.logger.info(f"Executing MODE A for query: {query}")
        
        vector_store = context.get('vector_store')
        if not vector_store:
            return ModeResponse(
                content="Error: Vector store not available",
                mode_name=self.get_mode_name(),
                success=False
            )
        
        # Check if this is a page-specific query
        page_num = self._extract_page_number(query)
        
        if page_num:
            return self._retrieve_page(page_num, vector_store)
        else:
            return self._retrieve_exact_text(query, vector_store)
    
    def _retrieve_page(self, page_num: int, vector_store) -> ModeResponse:
        """Retrieve exact text from a specific page"""
        search_query = f"PAGE {page_num}"
        results = vector_store.similarity_search(search_query, k=5)
        
        # Filter results to only include the target page
        page_content = []
        for doc in results:
            content = doc.page_content
            if f"PAGE {page_num}" in content:
                page_content.append(content)
        
        if page_content:
            formatted_content = f"""
{'='*80}
📄 PAGE {page_num}
{'='*80}

{chr(10).join(page_content)}

{'='*80}
[Lossless extraction complete]
"""
            return ModeResponse(
                content=formatted_content,
                mode_name=self.get_mode_name(),
                success=True,
                metadata={'page_number': page_num}
            )
        else:
            return ModeResponse(
                content=f"⚠️ Page {page_num} not found in indexed documents.",
                mode_name=self.get_mode_name(),
                success=False
            )
    
    def _retrieve_exact_text(self, query: str, vector_store) -> ModeResponse:
        """Retrieve exact text matching the query"""
        results = vector_store.similarity_search(query, k=3)
        
        if results:
            formatted_content = f"""
{'='*80}
📄 EXACT TEXT RETRIEVAL
Query: {query}
{'='*80}

{chr(10).join([doc.page_content for doc in results])}

{'='*80}
[Lossless extraction complete]
"""
            return ModeResponse(
                content=formatted_content,
                mode_name=self.get_mode_name(),
                success=True
            )
        else:
            return ModeResponse(
                content="⚠️ No matching content found.",
                mode_name=self.get_mode_name(),
                success=False
            )
    
    def get_system_prompt(self, query: str, retrieved_context: str) -> str:
        """
        MODE A doesn't use LLM - it returns raw text.
        This method is here for interface compliance.
        """
        return ""
