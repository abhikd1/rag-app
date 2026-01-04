"""
MODE E: ACTIVE RECALL / SELF-TEST HANDLER
Generates exam-style questions based on book content to test the user's knowledge.
"""

def is_mode_e_query(query):
    query_lower = query.lower().strip()
    if query_lower.startswith('mode: e') or query_lower.startswith('mode:e'):
        return True
    
    keywords = [
        'test me on',
        'quiz me',
        'ask me questions',
        'generate a quiz',
        'active recall',
        'start a test'
    ]
    return any(k in query_lower for k in keywords)

def get_mode_e_system_prompt(content):
    return f"""
##################################################
# MODE E — ACTIVE RECALL / SELF-TEST
##################################################

System Instructions:
- Create 3 distinct questions based on the text provided below.
- Level 1: Basic Definition/Fact.
- Level 2: Connection/Understanding.
- Level 3: Application/Complex Scenario.
- Do NOT provide the answers immediately. Ask the user to answer first.
- Only base questions on the provided text.

CONTENT SOURCE:
{content}

EXPECTED OUTPUT:
📝 **Active Recall Test**

**Q1 (Basic):** [Question]
**Q2 (Intermediate):** [Question]
**Q3 (Advanced):** [Question]

*Type your answers below, and I will grade them!*
"""

def handle_mode_e_query(query, vector_store, ollama_client):
    if not is_mode_e_query(query):
        return None, False

    clean_query = query.lower().replace('mode: e', '').replace('mode:e', '').strip()
    
    # Search for the context to test on (e.g., "Test me on Chapter 1")
    results = vector_store.similarity_search(clean_query, k=5)
    content = "\n\n".join([doc.page_content for doc in results])
    
    prompt = get_mode_e_system_prompt(content)
    
    response = ollama_client.generate(
        model='gpt-oss:120b-cloud',
        prompt=prompt,
        options={'temperature': 0.3} 
    )
    
    return f"""
================================================================================
🧠 MODE E: ACTIVE RECALL TEST
================================================================================

{response['response']}

================================================================================
""" , True
