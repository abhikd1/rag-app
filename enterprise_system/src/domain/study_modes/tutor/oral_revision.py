"""
MODE D: REVISION / ORAL MODE
Generates voice-friendly, sequential revision scripts.
Assumes user has studied before - this is for reinforcement.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.domain.study_modes.base.interface import IStudyMode, ModeResponse
from src.core.logging.logger import LoggerFactory


class OralRevisionTutor(IStudyMode):
    """
    MODE D: Oral Revision Implementation
    Creates smooth, sequential scripts for voice-friendly revision.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
    
    def get_mode_name(self) -> str:
        return "MODE D: REVISION / ORAL MODE"
    
    def can_handle(self, query: str) -> bool:
        """
        Detects if query requests oral revision.
        
        Triggers:
        - "Revise chapter..."
        - "Read this to me"
        - "Oral revision"
        - "MODE: D"
        - "Teach me like I know it"
        """
        query_lower = query.lower().strip()
        
        # Explicit mode selection
        if query_lower.startswith('mode: d') or query_lower.startswith('mode:d'):
            return True
        
        # Revision keywords
        revision_keywords = [
            'revise chapter',
            'revise page',
            'oral revision',
            'read this to me',
            'teach me like i know it',
            'revision mode',
            'review chapter',
            'go through chapter'
        ]
        
        return any(keyword in query_lower for keyword in revision_keywords)
    
    def execute(self, query: str, context: dict) -> ModeResponse:
        """
        Execute oral revision generation.
        
        Args:
            query: User's revision request
            context: Dict with 'vector_store' and 'llm_client'
            
        Returns:
            ModeResponse with voice-friendly revision script
        """
        self.logger.info(f"Executing MODE D for query: {query}")
        
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
        
        # Retrieve content for revision
        results = vector_store.similarity_search(clean_query, k=6)
        retrieved_context = "\n\n".join([doc.page_content for doc in results])
        
        # Generate revision script
        prompt = self.get_system_prompt(clean_query, retrieved_context)
        response = llm_client.generate(prompt, temperature=0.2)  # Slightly higher for natural flow
        
        formatted_content = f"""
{'='*80}
🗣️ ORAL REVISION SCRIPT
{'='*80}

{response.get('response', 'Error generating script')}

{'='*80}
[Revision script complete - Ready to read aloud]
"""
        
        return ModeResponse(
            content=formatted_content,
            mode_name=self.get_mode_name(),
            success=not response.get('error', False)
        )
    
    def _clean_query(self, query: str) -> str:
        """Remove mode prefix from query"""
        clean = query.lower()
        clean = clean.replace('mode: d', '').replace('mode:d', '')
        clean = clean.replace('revise', '').replace('review', '')
        return clean.strip()
    
    def get_system_prompt(self, query: str, retrieved_context: str) -> str:
        """
        Generate system prompt for MODE D.
        
        Enforces:
        - Sequential, voice-friendly narration
        - Assumes prior knowledge (revision, not first-time learning)
        - Natural transitions between concepts
        """
        return f"""
##################################################
# MODE D — REVISION / ORAL MODE (VOICE-FRIENDLY)
##################################################

System Instructions:
- Speak sequentially through the content below.
- Assume the user has studied this before (this is REVISION).
- Tone: Calm, human-paced, professional tutor.
- Use transition words like "Next," "Moving on to," "Recall that..."
- Do not use complex bullet points; use conversational lists.
- Explain concepts as if you're having a one-on-one tutoring session.
- Pause naturally between sections (use paragraph breaks).

CONTENT TO REVISE:
{retrieved_context}

USER REQUEST:
{query}

EXPECTED OUTPUT:
(A smooth, sequential script ready to be read aloud)

Example structure:
"Let's begin our revision of [topic]. First, recall that [concept A]... 
Moving on to [concept B], you'll remember that... 
Next, we have [concept C]..."

REVISION SCRIPT:
"""
