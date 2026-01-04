"""
MODE A: EXACT RECALL HANDLER
Integrates with main.py to provide lossless text retrieval
"""

def extract_page_number(query):
    """Extract page number from queries like 'page 14' or 'what is on page 20'"""
    import re
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


def is_mode_a_query(query):
    """Detect if user is requesting MODE A (Exact Recall)"""
    query_lower = query.lower().strip()
    
    # Explicit mode selection
    if query_lower.startswith('mode: a') or query_lower.startswith('mode:a'):
        return True
    
    # Page number queries
    if extract_page_number(query):
        return True
    
    # Exact recall keywords
    exact_keywords = [
        'exact text',
        'word for word',
        'verbatim',
        'lossless',
        'raw text',
        'what is written',
        'what does it say'
    ]
    
    return any(keyword in query_lower for keyword in exact_keywords)


def get_mode_a_system_prompt():
    """Return the MODE A system prompt"""
    return """
##################################################
# MODE A — EXACT RECALL (LOSSLESS)
##################################################

System Instructions:
- Return only the exact text under the specified page or heading.
- Preserve word order, paragraph breaks, and any formatting in the source.
- Do not summarize, paraphrase, or explain.
- Return all paragraphs belonging to the heading.
- If text is missing or unavailable, return "This is not stated in the book."

CRITICAL RULES:
1. NO SUMMARIES - Return the full text
2. NO EXPLANATIONS - Unless explicitly requested
3. NO ADDITIONS - Do not add context not in the source
4. PRESERVE STRUCTURE - Keep original paragraph breaks
5. VERIFY COMPLETENESS - Ensure all text from the page is included

Output Format:
================================================================================
📄 PAGE {number}
================================================================================

[EXACT TEXT FROM THE PAGE]

================================================================================
"""


def handle_mode_a_query(query, vector_store):
    """
    Handle MODE A queries with exact text retrieval
    
    Args:
        query: User's question
        vector_store: ChromaDB vector store instance
        
    Returns:
        tuple: (mode_a_response, is_mode_a)
    """
    
    if not is_mode_a_query(query):
        return None, False
    
    # Extract page number if present
    page_num = extract_page_number(query)
    
    if page_num:
        # Search for the specific page
        search_query = f"PAGE {page_num}"
        results = vector_store.similarity_search(search_query, k=5)
        
        # Filter and combine results from the target page
        page_content = []
        for doc in results:
            content = doc.page_content
            # Check if this chunk is from the target page
            if f"PAGE {page_num}" in content:
                page_content.append(content)
        
        if page_content:
            response = f"""
================================================================================
📄 MODE A: EXACT RECALL — PAGE {page_num}
================================================================================

{chr(10).join(page_content)}

================================================================================
[MODE A: Lossless extraction complete]
"""
            return response, True
        else:
            return f"⚠️ Page {page_num} not found in the indexed documents. Please verify the page number.", True
    
    # For other exact recall queries, use enhanced search
    results = vector_store.similarity_search(query, k=3)
    
    if results:
        response = f"""
================================================================================
📄 MODE A: EXACT RECALL
Query: {query}
================================================================================

{chr(10).join([doc.page_content for doc in results])}

================================================================================
[MODE A: Lossless extraction complete]
"""
        return response, True
    
    return "⚠️ No matching content found in the book.", True


# Integration instructions for main.py:
"""
Add this to your ask_question method in main.py:

from mode_a_handler import handle_mode_a_query, get_mode_a_system_prompt

# At the start of ask_question, before the normal RAG flow:
mode_a_response, is_mode_a = handle_mode_a_query(question, self.vector_store)
if is_mode_a:
    return mode_a_response

# If not MODE A, continue with normal RAG flow...
"""
