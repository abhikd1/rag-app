"""
MODE B: STUCK-POINT EXPLANATION
Provides surgical, focused explanations for specific confusing parts.
Uses book context only - no external knowledge.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.domain.study_modes.base.interface import IStudyMode, ModeResponse
from src.core.logging.logger import LoggerFactory


class StuckPointExplainer(IStudyMode):
    """
    MODE B: Stuck-Point Explanation Implementation
    Explains only the specific part the user is confused about.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
    
    def get_mode_name(self) -> str:
        return "MODE B: STUCK-POINT EXPLANATION"
    
    def can_handle(self, query: str) -> bool:
        """
        Detects if query requests explanation of a confusing part.
        
        Triggers:
        - "I am confused about..."
        - "I don't understand..."
        - "Explain this part..."
        - "MODE: B"
        - "What does this mean..."
        """
        query_lower = query.lower().strip()
        
        # Explicit mode selection
        if query_lower.startswith('mode: b') or query_lower.startswith('mode:b'):
            return True
        
        # Confusion keywords
        confusion_keywords = [
            'i am confused about',
            'i don\'t understand',
            'i dont understand',
            'explain this part',
            'what does this mean',
            'can you clarify',
            'stuck on',
            'confused by',
            'unclear about'
        ]
        
        return any(keyword in query_lower for keyword in confusion_keywords)
    
    def execute(self, query: str, context: dict) -> ModeResponse:
        """
        Execute stuck-point explanation.
        
        Args:
            query: User's confusion
            context: Dict with 'vector_store' and 'llm_client'
            
        Returns:
            ModeResponse with surgical explanation
        """
        self.logger.info(f"Executing MODE B for query: {query}")
        
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
        
        # Retrieve relevant context
        results = vector_store.similarity_search(clean_query, k=3)
        retrieved_context = "\n\n".join([doc.page_content for doc in results])
        
        # Generate explanation
        prompt = self.get_system_prompt(clean_query, retrieved_context)
        response = llm_client.generate(prompt, temperature=0.0)
        
        formatted_content = f"""
{'='*80}
🧩 STUCK-POINT EXPLANATION
{'='*80}

{response.get('response', 'Error generating explanation')}

{'='*80}
[Surgical explanation complete]
"""
        
        return ModeResponse(
            content=formatted_content,
            mode_name=self.get_mode_name(),
            success=not response.get('error', False)
        )
    
    def _clean_query(self, query: str) -> str:
        """Remove mode prefix from query"""
        clean = query.lower()
        clean = clean.replace('mode: b', '').replace('mode:b', '')
        clean = clean.replace('i am confused about', '')
        clean = clean.replace('i don\'t understand', '')
        clean = clean.replace('explain this part:', '')
        return clean.strip()
    
    def get_system_prompt(self, query: str, retrieved_context: str) -> str:
        """
        Generate system prompt for MODE B.
        
        Enforces:
        - Explain ONLY the confusing part
        - Use book context only
        - Connect back to original text
        """
        return f"""
##################################################
# MODE B — STUCK-POINT EXPLANATION
##################################################

System Instructions:
- Explain ONLY the part of the text the user is confused about.
- Use prior concepts from the provided book context if necessary.
- Do not re-explain the entire section.
- After explaining, briefly connect back to the original paragraph.
- Keep explanations minimal, focused, and context-driven.
- DO NOT use external knowledge - only what's in the context below.

CONTEXT FROM THE BOOK:
{retrieved_context}

USER'S CONFUSION:
{query}

EXPECTED OUTPUT FORMAT:
💡 EXPLANATION:
(Short, surgical explanation of the concept)

📖 BOOK RELEVANCE:
(Why this matters in the context of the book)

🔗 CONNECTION:
(How this connects back to the specific paragraph)

ANSWER:
"""
