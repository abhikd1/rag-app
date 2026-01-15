"""
MODE C: CONCEPT LINKING HANDLER
Connects a requested concept to other parts of the SAME book.
"""

def is_mode_c_query(query):
    query_lower = query.lower().strip()
    if query_lower.startswith('mode: c') or query_lower.startswith('mode:c'):
        return True
    
    keywords = [
        'relate to earlier',
        'connect this concept',
        'relationship between',
        'how does this connect',
        'link this to'
    ]
    return any(k in query_lower for k in keywords)

def get_mode_c_system_prompt(concept, context):
    return f"""
##################################################
# MODE C — CONCEPT LINKING
##################################################

System Instructions:
- Connect the concept "{concept}" to other parts of the content provided below.
- Name headings or page numbers explicitly if available in the context.
- Do not invent external examples.
- Explain only relationships (how A influences B).

CONTEXT FOUND IN BOOK:
{context}

USER REQUEST:
How does "{concept}" relate to other parts of the book?

EXPECTED OUTPUT:
This concept connects to:
- [Section/Page]: Explanation of relationship
- [Section/Page]: Explanation of relationship
"""

def handle_mode_c_query(query, vector_store, ollama_client):
    if not is_mode_c_query(query):
        return None, False

    clean_query = query.lower().replace('mode: c', '').replace('mode:c', '').strip()
    
    # We want to find multiple occurrences across the book, so we increase k
    results = vector_store.similarity_search(clean_query, k=10)
    context = "\n---\n".join([doc.page_content for doc in results])
    
    prompt = get_mode_c_system_prompt(clean_query, context)
    
    response = ollama_client.generate(
        model='gpt-oss:120b-cloud',
        prompt=prompt,
        options={'temperature': 0}
    )
    
    return f"""
================================================================================
🔗 MODE C: CONCEPT LINKING
================================================================================

{response['response']}

================================================================================
""" , True
