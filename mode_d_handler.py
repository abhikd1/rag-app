"""
MODE D: REVISION / ORAL MODE HANDLER
Generates voice-friendly, sequential explanations for revision.
"""

def is_mode_d_query(query):
    query_lower = query.lower().strip()
    if query_lower.startswith('mode: d') or query_lower.startswith('mode:d'):
        return True
    
    keywords = [
        'revise chapter',
        'revise page',
        'oral revision',
        'read this to me',
        'teach me like i know it',
        'revision mode'
    ]
    return any(k in query_lower for k in keywords)

def get_mode_d_system_prompt(content):
    return f"""
##################################################
# MODE D — REVISION / ORAL MODE (VOICE-FRIENDLY)
##################################################

System Instructions:
- Speak sequentially through the content.
- Assume the user has studied this before (this is revision).
- Tone: Calm, human-paced, professional tutor.
- Use transition words like "Next," "Moving on to," "Recall that..."
- Do not use complex bullet points; use conversational lists.

CONTENT TO REVISE:
{content}

EXPECTED OUTPUT:
(A script ready to be read aloud)
"""

def handle_mode_d_query(query, vector_store, ollama_client):
    if not is_mode_d_query(query):
        return None, False

    clean_query = query.lower().replace('mode: d', '').replace('mode:d', '').strip()
    
    # 1. Try to identify specific chapter/page to revise
    # If the user says "Revise Chapter 2", we search specifically for "Chapter 2"
    results = vector_store.similarity_search(clean_query, k=6)
    
    # Combine content, preserving order if possible (though vector search is ranked by relevance)
    # For revision, we want a cohesive narrative.
    content = "\n\n".join([doc.page_content for doc in results])
    
    prompt = get_mode_d_system_prompt(content)
    
    response = ollama_client.generate(
        model='gpt-oss:120b-cloud',
        prompt=prompt,
        options={'temperature': 0.2} # Slightly higher temp for more natural flow
    )
    
    return f"""
================================================================================
🗣️ MODE D: ORAL REVISION SCRIPT
================================================================================

{response['response']}

================================================================================
""" , True
