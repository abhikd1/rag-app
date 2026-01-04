"""
Automated Test Script for Enterprise Study System
Tests all 5 modes with sample queries.
"""

import sys
import os

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from domain.orchestrator.router import EnterpriseQueryRouter
from infrastructure.database.vector_store.client import VectorStoreClient
from infrastructure.llm.client.ollama_client import LLMClient
from core.logging.logger import LoggerFactory

def print_separator():
    print("\n" + "="*80 + "\n")

def test_mode_a():
    """Test MODE A: Exact Recall"""
    print("🧪 TESTING MODE A: EXACT RECALL")
    print_separator()
    
    queries = [
        "Page 14",
        "What is written on page 20?",
        "MODE: A Show me page 13"
    ]
    
    return queries

def test_mode_b():
    """Test MODE B: Stuck-Point Explanation"""
    print("🧪 TESTING MODE B: STUCK-POINT EXPLANATION")
    print_separator()
    
    queries = [
        "I am confused about the thought vector",
        "I don't understand what attention mechanism means",
        "MODE: B Explain cold fusion"
    ]
    
    return queries

def test_mode_c():
    """Test MODE C: Concept Linking"""
    print("🧪 TESTING MODE C: CONCEPT LINKING")
    print_separator()
    
    queries = [
        "How does the attention mechanism relate to transformers?",
        "Connect GPT-2 to GPT-3",
        "MODE: C Link prompt engineering to LLM training"
    ]
    
    return queries

def test_mode_d():
    """Test MODE D: Oral Revision"""
    print("🧪 TESTING MODE D: ORAL REVISION")
    print_separator()
    
    queries = [
        "Revise Chapter 1",
        "Read the history of GPT models to me",
        "MODE: D Go through the transformer architecture"
    ]
    
    return queries

def test_mode_e():
    """Test MODE E: Active Recall"""
    print("🧪 TESTING MODE E: ACTIVE RECALL")
    print_separator()
    
    queries = [
        "Test me on Chapter 1",
        "Quiz me on transformers",
        "MODE: E Ask me about GPT models"
    ]
    
    return queries

def run_tests():
    """Run all tests"""
    logger = LoggerFactory.get_logger(__name__)
    
    print("🚀 INITIALIZING ENTERPRISE STUDY SYSTEM FOR TESTING...")
    print_separator()
    
    try:
        # Initialize components
        vector_store = VectorStoreClient()
        llm_client = LLMClient()
        router = EnterpriseQueryRouter(vector_store, llm_client)
        
        print("✅ System initialized successfully!")
        print_separator()
        
        # Collect all test queries
        all_tests = [
            ("MODE A", test_mode_a()),
            ("MODE B", test_mode_b()),
            ("MODE C", test_mode_c()),
            ("MODE D", test_mode_d()),
            ("MODE E", test_mode_e()),
        ]
        
        # Run tests
        for mode_name, queries in all_tests:
            print(f"\n{'='*80}")
            print(f"🧪 TESTING {mode_name}")
            print(f"{'='*80}\n")
            
            for i, query in enumerate(queries, 1):
                print(f"\n📝 Test {i}: {query}")
                print("-" * 80)
                
                try:
                    response = router.route(query)
                    
                    if response:
                        print(f"✅ Success: {response.mode_name}")
                        print(f"\n{response.content[:500]}...")  # Show first 500 chars
                    else:
                        print("⚠️ No mode matched (fallback would trigger)")
                        
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    logger.error(f"Test failed for query: {query}", exc_info=True)
                
                print("-" * 80)
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS COMPLETE!")
        print("="*80)
        print("\n📊 Check the logs in ./logs/ for detailed information")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        logger.error("Test suite failed", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
