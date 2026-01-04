"""
MODE B: STUCK-POINT EXPLANATION HANDLER
Provides minimal, context-driven explanations for specific confusing parts.
"""

def is_mode_b_query(query):
    """Detect if user is requesting MODE B (Stuck-Point Explanation)"""
    query_lower = query.lower().strip()
    
    # Explicit mode selection
    if query_lower.startswith('mode: b') or query_lower.startswith('mode:b'):
        return True
    
    # Confusion keywords
    confusion_keywords = [
        'i am confused about',
        'i don\'t understand',
        'explain this part',
        'what does this mean',
        'can you clarify',
        'stuck on'
    ]
    
    return any(keyword in query_lower for keyword in confusion_keywords)


def get_mode_b_system_prompt(context, confusion_query):
    """Return the MODE B system prompt with injected context"""
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

CONTEXT FROM THE BOOK:
{context}

USER'S CONFUSION:
{confusion_query}

EXPECTED OUTPUT FORMAT:
💡 EXPLANATION:
(Short, surgical explanation of the concept)

📖 BOOK RELEVANCE:
(Why this matters in the context of the book)

🔗 CONNECTION:
(How this connects back to the specific paragraph)
"""

def handle_mode_b_query(query, vector_store, ollama_client):
    """
    Handle MODE B queries by finding relevant context and generating a surgical explanation.
    """
    if not is_mode_b_query(query):
        return None, False

    # Clean the query (remove "MODE: B" prefix)
    clean_query = query.replace('MODE: B', '').replace('mode: b', '').replace('MODE:B', '').replace('mode:b', '').strip()
    
    # Search for the context related to the confusion
    relevant_docs = vector_store.similarity_search(clean_query, k=3)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = get_mode_b_system_prompt(context, clean_query)
    
    # Call the model for the explanation
    response = ollama_client.generate(
        model='gpt-oss:120b-cloud',
        prompt=prompt,
        options={'temperature': 0}
    )
    
    response_text = response['response']
    
    formatted_response = f"""
================================================================================
🧩 MODE B: STUCK-POINT EXPLANATION
================================================================================

{response_text}

================================================================================
[MODE B: Surgical explanation complete]
"""
    return formatted_response, True
