"""
MODE E: ACTIVE RECALL / SELF-TEST
Generates tiered questions to test user's knowledge.
Questions are based strictly on book content.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.domain.study_modes.base.interface import IStudyMode, ModeResponse
from src.core.logging.logger import LoggerFactory


class ActiveRecallTester(IStudyMode):
    """
    MODE E: Active Recall Implementation
    Generates exam-style questions with increasing difficulty.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
    
    def get_mode_name(self) -> str:
        return "MODE E: ACTIVE RECALL / SELF-TEST"
    
    def can_handle(self, query: str) -> bool:
        """
        Detects if query requests self-testing.
        
        Triggers:
        - "Test me on..."
        - "Quiz me"
        - "Ask me questions"
        - "MODE: E"
        - "Generate a quiz"
        """
        query_lower = query.lower().strip()
        
        # Explicit mode selection
        if query_lower.startswith('mode: e') or query_lower.startswith('mode:e'):
            return True
        
        # Testing keywords
        testing_keywords = [
            'test me on',
            'quiz me',
            'ask me questions',
            'generate a quiz',
            'active recall',
            'start a test',
            'exam questions',
            'practice questions'
        ]
        
        return any(keyword in query_lower for keyword in testing_keywords)
    
    def execute(self, query: str, context: dict) -> ModeResponse:
        """
        Execute active recall test generation.
        
        Args:
            query: User's test request
            context: Dict with 'vector_store' and 'llm_client'
            
        Returns:
            ModeResponse with tiered questions
        """
        self.logger.info(f"Executing MODE E for query: {query}")
        
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
        
        # Retrieve content to test on
        results = vector_store.similarity_search(clean_query, k=5)
        retrieved_context = "\n\n".join([doc.page_content for doc in results])
        
        # Generate questions
        prompt = self.get_system_prompt(clean_query, retrieved_context)
        response = llm_client.generate(prompt, temperature=0.3)  # Slightly higher for variety
        
        formatted_content = f"""
{'='*80}
🧠 ACTIVE RECALL TEST
{'='*80}

{response.get('response', 'Error generating questions')}

{'='*80}
[Test generated - Type your answers and I will grade them!]
"""
        
        return ModeResponse(
            content=formatted_content,
            mode_name=self.get_mode_name(),
            success=not response.get('error', False),
            metadata={'test_topic': clean_query}
        )
    
    def _clean_query(self, query: str) -> str:
        """Remove mode prefix from query"""
        clean = query.lower()
        clean = clean.replace('mode: e', '').replace('mode:e', '')
        clean = clean.replace('test me on', '').replace('quiz me on', '')
        clean = clean.replace('ask me questions about', '')
        return clean.strip()
    
    def get_system_prompt(self, query: str, retrieved_context: str) -> str:
        """
        Generate system prompt for MODE E.
        
        Enforces:
        - 3 tiered questions (Basic, Intermediate, Advanced)
        - Questions based strictly on provided content
        - No answers provided initially
        """
        return f"""
##################################################
# MODE E — ACTIVE RECALL / SELF-TEST
##################################################

System Instructions:
- Create 3 distinct questions based on the text provided below.
- Level 1 (Basic): Simple definition or fact recall.
- Level 2 (Intermediate): Understanding connections or explanations.
- Level 3 (Advanced): Application, synthesis, or complex scenario.
- Do NOT provide the answers immediately. Ask the user to answer first.
- Only base questions on the provided text - no external knowledge.
- Make questions specific and testable.

CONTENT SOURCE:
{retrieved_context}

TOPIC TO TEST:
{query}

EXPECTED OUTPUT FORMAT:
📝 **Active Recall Test: [Topic]**

**Q1 (Basic - Definition/Fact):** 
[Question that tests basic recall]

**Q2 (Intermediate - Understanding):** 
[Question that tests comprehension and connections]

**Q3 (Advanced - Application):** 
[Question that requires synthesis or application]

---
*Type your answers below, and I will grade them!*

GENERATE QUESTIONS:
"""
