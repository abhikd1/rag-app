"""
MODE C: CONCEPT LINKING
Connects concepts across different parts of the book.
Shows relationships and dependencies between ideas.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.domain.study_modes.base.interface import IStudyMode, ModeResponse
from src.core.logging.logger import LoggerFactory


class ConceptLinker(IStudyMode):
    """
    MODE C: Concept Linking Implementation
    Finds and explains relationships between concepts across the book.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
    
    def get_mode_name(self) -> str:
        return "MODE C: CONCEPT LINKING"
    
    def can_handle(self, query: str) -> bool:
        """
        Detects if query requests concept linking.
        
        Triggers:
        - "How does X relate to Y"
        - "Connect this concept..."
        - "Relationship between..."
        - "MODE: C"
        - "Link this to..."
        """
        query_lower = query.lower().strip()
        
        # Explicit mode selection
        if query_lower.startswith('mode: c') or query_lower.startswith('mode:c'):
            return True
        
        # Linking keywords
        linking_keywords = [
            'relate to earlier',
            'connect this concept',
            'relationship between',
            'how does this connect',
            'link this to',
            'how is this related',
            'connection between',
            'relates to'
        ]
        
        return any(keyword in query_lower for keyword in linking_keywords)
    
    def execute(self, query: str, context: dict) -> ModeResponse:
        """
        Execute concept linking.
        
        Args:
            query: User's linking question
            context: Dict with 'vector_store' and 'llm_client'
            
        Returns:
            ModeResponse with concept relationships
        """
        self.logger.info(f"Executing MODE C for query: {query}")
        
        vector_store = context.get('vector_store')
        llm_client = context.get('llm_client')
        
        if not vector_store or not llm_client:
            return ModeResponse(
                content="Error: Required services not available",
                mode_name=self.get_mode_name(),
                success=False
            )
        
        # Clean the query
        clean_query = self._clean_query(query)
        
        # Retrieve multiple occurrences across the book (higher k)
        results = vector_store.similarity_search(clean_query, k=10)
        retrieved_context = "\n---\n".join([doc.page_content for doc in results])
        
        # Generate linking analysis
        prompt = self.get_system_prompt(clean_query, retrieved_context)
        response = llm_client.generate(prompt, temperature=0.0)
        
        formatted_content = f"""
{'='*80}
🔗 CONCEPT LINKING ANALYSIS
{'='*80}

{response.get('response', 'Error generating analysis')}

{'='*80}
[Concept linking complete]
"""
        
        return ModeResponse(
            content=formatted_content,
            mode_name=self.get_mode_name(),
            success=not response.get('error', False)
        )
    
    def _clean_query(self, query: str) -> str:
        """Remove mode prefix from query"""
        clean = query.lower()
        clean = clean.replace('mode: c', '').replace('mode:c', '')
        return clean.strip()
    
    def get_system_prompt(self, query: str, retrieved_context: str) -> str:
        """
        Generate system prompt for MODE C.
        
        Enforces:
        - Connect concepts within the book only
        - Name specific headings/pages
        - Explain relationships, not just list occurrences
        """
        return f"""
##################################################
# MODE C — CONCEPT LINKING
##################################################

System Instructions:
- Connect the concept in the query to other parts of the content provided below.
- Name headings or page numbers explicitly if available in the context.
- Do not invent external examples - use only what's in the book.
- Explain relationships (how A influences B, why they're connected).
- Show the progression or evolution of the concept across chapters.

CONTEXT FOUND IN BOOK:
{retrieved_context}

USER REQUEST:
{query}

EXPECTED OUTPUT FORMAT:
This concept connects to:

📍 [Section/Page]: 
   → Relationship explanation
   → Why this connection matters

📍 [Section/Page]:
   → Relationship explanation
   → Why this connection matters

🎯 SYNTHESIS:
(Overall pattern or progression of this concept across the book)

ANSWER:
"""
