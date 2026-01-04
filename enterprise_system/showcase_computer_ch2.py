"""
Mode Showcase Script for Computer Science Chapter 2.
Illustrates what each mode can do with the new content.
"""

from src.domain.orchestrator.router import EnterpriseQueryRouter
from src.infrastructure.database.vector_store.client import VectorStoreClient
from src.infrastructure.llm.client.ollama_client import LLMClient
from src.core.config.settings import config
import sys
import io

# Fix encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def showcase():
    print("="*80)
    print("🚀 COMPUTER SCIENCE CHAPTER 2 (FILE HANDLING) - MODE SHOWCASE")
    print("="*80)
    
    vector_store = VectorStoreClient()
    llm_client = LLMClient()
    router = EnterpriseQueryRouter(vector_store, llm_client)
    
    test_queries = [
        ("MODE A: Page 2", "Exact Recall of Page 2 (Definition of File)"),
        ("I don't understand the difference between text and binary files", "Mode B: Surgical Explanation"),
        ("How does the open() function relate to file access modes in Python?", "Mode C: Concept Linking"),
        ("Summarize the steps to write to a file for oral revision", "Mode D: Oral Revision Script"),
        ("Test me on file handling in Python", "Mode E: Active Recall Quiz")
    ]
    
    for query, label in test_queries:
        print(f"\n\n🔹 TESTING: {label}")
        print("-" * 50)
        response = router.route(query)
        print(response.content)
        print("-" * 50)

if __name__ == "__main__":
    showcase()
