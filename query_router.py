import ollama
from mode_a_handler import handle_mode_a_query, is_mode_a_query
from mode_b_handler import handle_mode_b_query, is_mode_b_query
from mode_c_handler import handle_mode_c_query, is_mode_c_query
from mode_d_handler import handle_mode_d_query, is_mode_d_query
from mode_e_handler import handle_mode_e_query, is_mode_e_query

class QueryRouter:
    """
    Orchestration Layer: Decides which specialized handler should process the user's request.
    This decouples the Interface (main.py) from the Business Logic (Handlers).
    """
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.client = ollama

    def route_and_execute(self, query):
        """
        Analyzes the query and routes it to the correct handler.
        Returns: (response_string, handled_boolean)
        """
        
        # 1. Check Exact Recall (Highest Priority)
        if is_mode_a_query(query):
            print("[ROUTER] Routing to MODE A (Exact Recall)...")
            return handle_mode_a_query(query, self.vector_store)

        # 2. Check Stuck-Point Explanation
        if is_mode_b_query(query):
            print("[ROUTER] Routing to MODE B (Explanation)...")
            return handle_mode_b_query(query, self.vector_store, self.client)

        # 3. Check Concept Linking
        if is_mode_c_query(query):
            print("[ROUTER] Routing to MODE C (Concept Linking)...")
            return handle_mode_c_query(query, self.vector_store, self.client)

        # 4. Check Revision/Oral Mode
        if is_mode_d_query(query):
            print("[ROUTER] Routing to MODE D (Revision)...")
            return handle_mode_d_query(query, self.vector_store, self.client)

        # 5. Check Active Recall/Test
        if is_mode_e_query(query):
            print("[ROUTER] Routing to MODE E (Self-Test)...")
            return handle_mode_e_query(query, self.vector_store, self.client)

        # 6. Fallback (Standard RAG)
        # Returns None, False so main.py falls back to default chat behavior
        return None, False
