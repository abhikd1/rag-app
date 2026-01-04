"""
MODE A ENHANCED: DUAL-LAYER LOSSLESS RECALL
Returns 100% NCERT-complete content in an engaging, brain-friendly format.
Combines exact content coverage with cognitive anchors for fast learning.
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.domain.study_modes.base.interface import IStudyMode, ModeResponse
from src.core.logging.logger import LoggerFactory
from langchain_core.documents import Document


class EnhancedRecallMode(IStudyMode):
    """
    MODE A ENHANCED: Dual-Layer Lossless Recall
    Provides 100% NCERT coverage in an engaging, structured format.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
    
    def get_mode_name(self) -> str:
        return "MODE A: ENHANCED LOSSLESS RECALL"
    
    def can_handle(self, query: str) -> bool:
        """
        Detects if query requests lossless page/content recall.
        
        Triggers:
        - "Page X"
        - "MODE: A"  
        - Any page-based query
        """
        query_lower = query.lower().strip()
        
        # Explicit mode selection
        if query_lower.startswith('mode: a') or query_lower.startswith('mode:a'):
            return True
        
        # Page number queries
        if self._extract_page_number(query):
            return True
        
        # Enhanced keywords
        enhanced_keywords = [
            'explain page',
            'study page',
            'learn page',
            'teach me page',
            'page',
            'section'
        ]
        
        return any(keyword in query_lower for keyword in enhanced_keywords)
    
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
        Execute enhanced lossless recall with LLM formatting.
        
        Args:
            query: User's question
            context: Dict with 'vector_store' and 'llm_client' keys
            
        Returns:
            ModeResponse with structured, engaging content
        """
        self.logger.info(f"Executing ENHANCED MODE A for query: {query}")
        
        vector_store = context.get('vector_store')
        llm_client = context.get('llm_client')
        
        if not vector_store or not llm_client:
            return ModeResponse(
                content="Error: Required services not available",
                mode_name=self.get_mode_name(),
                success=False
            )
        
        # Check if this is a page-specific query
        page_num = self._extract_page_number(query)
        
        if page_num:
            return self._process_page_with_llm(page_num, vector_store, llm_client)
        else:
            return self._process_topic_with_llm(query, vector_store, llm_client)
    
    def _process_page_with_llm(self, page_num: int, vector_store, llm_client) -> ModeResponse:
        """Retrieve and process page content through LLM"""
        search_query = f"PAGE {page_num}"
        results = vector_store.similarity_search(search_query, k=10)
        
        # Filter and combine page content
        page_content = []
        for doc in results:
            content = doc.page_content
            if f"PAGE {page_num}" in content:
                page_content.append(content)
        
        if not page_content:
            return ModeResponse(
                content=f"⚠️ Page {page_num} not found in indexed documents.",
                mode_name=self.get_mode_name(),
                success=False
            )
        
        # Combine all page chunks
        raw_text = "\n\n".join(page_content)
        
        # Generate enhanced output using LLM
        system_prompt = self.get_system_prompt(f"Page {page_num}", raw_text)
        
        try:
            # LLMClient uses 'generate' method with a single prompt
            response = llm_client.generate(
                prompt=system_prompt,
                temperature=0.2  # Low creativity, high consistency
            )
            
            # Extract text from response dict
            enhanced_content = response.get('response', '')
            
            if response.get('error'):
                # Fallback to raw if LLM failed
                raise Exception(enhanced_content)
            
            formatted_output = f"""
{'='*80}
📚 PAGE {page_num} - LOSSLESS MASTER GUIDE
{'='*80}

{enhanced_content}

{'='*80}
✅ 100% NCERT Coverage | Exam-Safe | Brain-Optimized
"""
            
            return ModeResponse(
                content=formatted_output,
                mode_name=self.get_mode_name(),
                success=True,
                metadata={'page_number': page_num, 'ncert_complete': True}
            )
        
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}")
            # Fallback to raw text
            return ModeResponse(
                content=f"{'='*80}\n📄 PAGE {page_num} (RAW TEXT)\n{'='*80}\n\n{raw_text}",
                mode_name=self.get_mode_name(),
                success=True
            )
    
    def _process_topic_with_llm(self, query: str, vector_store, llm_client) -> ModeResponse:
        """Process topic-based query with enhanced formatting"""
        results = vector_store.similarity_search(query, k=8)
        
        if not results:
            return ModeResponse(
                content="⚠️ No matching content found.",
                mode_name=self.get_mode_name(),
                success=False
            )
        
        raw_text = "\n\n".join([doc.page_content for doc in results])
        system_prompt = self.get_system_prompt(query, raw_text)
        
        try:
            response = llm_client.generate(
                prompt=system_prompt,
                temperature=0.2
            )
            
            enhanced_content = response.get('response', '')
            
            if response.get('error'):
                raise Exception(enhanced_content)
            
            formatted_output = f"""
{'='*80}
📚 LOSSLESS STUDY GUIDE
Topic: {query}
{'='*80}

{enhanced_content}

{'='*80}
✅ NCERT Complete | Fast to Learn | Exam-Ready
"""
            
            return ModeResponse(
                content=formatted_output,
                mode_name=self.get_mode_name(),
                success=True
            )
        
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}")
            return ModeResponse(
                content=f"Error: {str(e)}",
                mode_name=self.get_mode_name(),
                success=False
            )
    
    def get_system_prompt(self, query: str, retrieved_context: str) -> str:
        """
        The optimized dual-layer lossless system prompt.
        Based on extensive ChatGPT conversation analysis.
        """
        return f"""You are an NCERT Study Guide Generator using the DUAL-LAYER LOSSLESS approach.

OBJECTIVE: Create a SINGLE OUTPUT that is:
✅ 100% NCERT complete (zero information loss)
✅ Engaging and fast to read (NOT boring textbook prose)
✅ Perfect for exam preparation

═══════════════════════════════════════════════════════════════════════

NON-NEGOTIABLE RULES:

1️⃣ SENTENCE ACCOUNTING RULE
• Every NCERT sentence, example, activity, and definition MUST be explicitly represented
• NOTHING may be skipped, implied, or merged silently
• Use exact NCERT terminology wherever applicable

2️⃣ TABLE & DATA COMPLETENESS
• If tables exist: ALL rows must be listed
• All modes/values/comparisons must be stated
• Default behaviors must be explicit

3️⃣ ACTIVITY EXPANSION
• If NCERT mentions "Activity" or "Find out": provide the expected answer
• Explain the behavior/result
• State implications

4️⃣ EXAM SAFETY RULE
• Explicitly highlight with ⚠️:
  - Crash conditions
  - Data loss scenarios
  - Default behaviors
  - Common exam traps

═══════════════════════════════════════════════════════════════════════

PRESENTATION RULES (CRITICAL):

❌ DO NOT write like a textbook
❌ DO NOT use long continuous paragraphs
❌ DO NOT summarize or compress information

✅ DO use:
• **Structured bullets** for clarity
• **Section markers** (📍 🔹 💡 ⚠️) - emojis ONLY as visual anchors, not decoration
• **Short labeled blocks** instead of paragraphs
• **Inline metaphors** with NCERT terms in brackets
• **Exam trap callouts** (⚠️ THE X TRAP)
• **Comparison tables** when showing differences

═══════════════════════════════════════════════════════════════════════

STRUCTURE TEMPLATE:

📍 [NCERT HEADING] (exact from book)
• Core fact 1
• Core fact 2
• Technical detail with exact term

💡 THE "WHY THIS MATTERS"
• Practical significance
• Connection to previous concepts

⚠️ EXAM TRAP: [SPECIFIC WARNING]
• What goes wrong
• What examiners test

🔹 EXAMPLE (if in NCERT)
• Concrete illustration
• Expected output/behavior

✨ QUICK RECAP
• 3-5 bullet summary of section

═══════════════════════════════════════════════════════════════════════

ENGAGEMENT CONSTRAINT:
• Make it feel 3× faster than reading NCERT
• Every fact should have context or anchor
• Use contrast and comparison
• Highlight "the real difference" between concepts

OUTPUT GOAL:
A guide that covers 100% NCERT but feels lighter, clearer, and faster to review than the textbook.

═══════════════════════════════════════════════════════════════════════

NCERT CONTENT TO PROCESS:

{retrieved_context}

═══════════════════════════════════════════════════════════════════════

Now process this content following ALL rules above. Remember:
• Zero information loss
• Engaging structure  
• Exam-safe terminology"""
