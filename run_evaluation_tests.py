"""
RAG System Evaluation Test Runner

This script automatically runs all test scenarios from the Master Evaluation Prompt
and saves outputs for external evaluation.

Usage:
    python run_evaluation_tests.py

Output:
    Creates evaluation_outputs/ directory with test results
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import FreeDocumentQA


class EvaluationTestRunner:
    """Runs comprehensive evaluation tests on the RAG system"""
    
    def __init__(self):
        self.output_dir = Path("evaluation_outputs")
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        
        # Initialize the RAG system
        print("\n[INFO] Initializing RAG system for evaluation...")
        self.qa = FreeDocumentQA()
        
        # Load documents if needed
        try:
            if len(self.qa.vector_store.get()['ids']) == 0:
                print("[INFO] Loading documents...")
                self.qa.load_documents_from_folder()
        except:
            print("[INFO] Loading documents...")
            self.qa.load_documents_from_folder()
        
        print("[INFO] RAG system ready for testing.\n")
        
    def run_test(self, category: str, test_name: str, query: str):
        """Run a single test and capture output"""
        print(f"\n{'='*60}")
        print(f"🧪 Running: {category} - {test_name}")
        print(f"📝 Query: {query}")
        print(f"{'='*60}\n")
        
        try:
            # Run the query
            result = self.qa.ask_question(query)
            
            # Save result
            test_result = {
                "category": category,
                "test_name": test_name,
                "query": query,
                "output": result,
                "status": "✅ Completed"
            }
            
            self.results.append(test_result)
            
            print(f"\n✅ Test completed: {test_name}\n")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(error_msg)
            
            test_result = {
                "category": category,
                "test_name": test_name,
                "query": query,
                "output": error_msg,
                "status": "❌ Failed"
            }
            
            self.results.append(test_result)
            return None
    
    def save_results(self):
        """Save all test results to file"""
        output_file = self.output_dir / f"evaluation_{self.timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# RAG System Evaluation Results\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Tests:** {len(self.results)}\n\n")
            
            # Summary
            passed = sum(1 for r in self.results if r['status'].startswith('✅'))
            failed = len(self.results) - passed
            f.write(f"**Summary:** {passed} passed, {failed} failed\n\n")
            f.write("---\n\n")
            
            # Detailed results
            for i, result in enumerate(self.results, 1):
                f.write(f"## Test {i}: {result['category']} - {result['test_name']}\n\n")
                f.write(f"**Status:** {result['status']}\n\n")
                f.write(f"**Query:**\n```\n{result['query']}\n```\n\n")
                f.write(f"**Output:**\n```\n{result['output']}\n```\n\n")
                f.write("---\n\n")
        
        print(f"\n✅ Results saved to: {output_file}")
        return output_file
    
    def run_all_tests(self):
        """Run all evaluation tests from Master Prompt"""
        
        print("\n" + "="*60)
        print("🚀 Starting RAG System Evaluation")
        print("="*60 + "\n")
        
        # 1️⃣ INDEXING TESTS
        self.run_test(
            "1. Indexing",
            "Full Index Generation",
            "Create the full index of this book"
        )
        
        self.run_test(
            "1. Indexing",
            "Chapter-Specific Index",
            "Show only Chapter 3 headings"
        )
        
        self.run_test(
            "1. Indexing",
            "Subtopic Index",
            "List subtopics under 2.1"
        )
        
        # 2️⃣ READING FLOW TESTS
        self.run_test(
            "2. Reading Flow",
            "Start Reading",
            "Start reading Chapter 1"
        )
        
        self.run_test(
            "2. Reading Flow",
            "Continue Reading",
            "Continue"
        )
        
        self.run_test(
            "2. Reading Flow",
            "Pause and Summarize",
            "Pause here and summarize"
        )
        
        # 3️⃣ TRANSCRIPT MODE TESTS (if applicable)
        self.run_test(
            "3. Transcript Mode",
            "Time Range 0-10min",
            "Explain 0-10 minutes"
        )
        
        self.run_test(
            "3. Transcript Mode",
            "Time Range 10-20min",
            "Summarize 10-20 minutes"
        )
        
        self.run_test(
            "3. Transcript Mode",
            "Specific Time Range",
            "What was explained between 32:10 and 35:40?"
        )
        
        # 4️⃣ ZERO-LOSS TESTS
        self.run_test(
            "4. Zero-Loss",
            "Coverage Check",
            "Have we covered everything from Chapter 2?"
        )
        
        self.run_test(
            "4. Zero-Loss",
            "Unread Concepts",
            "What concepts are left unread?"
        )
        
        self.run_test(
            "4. Zero-Loss",
            "Study Progress",
            "List what I haven't studied yet"
        )
        
        # 5️⃣ MATH/LOGIC TESTS
        self.run_test(
            "5. Math/Logic",
            "Solve Example",
            "Solve Example 4.2 using the book method"
        )
        
        self.run_test(
            "5. Math/Logic",
            "Verify Calculation",
            "Verify this calculation"
        )
        
        self.run_test(
            "5. Math/Logic",
            "Error Analysis",
            "Where did I go wrong?"
        )
        
        # 6️⃣ REASONING TESTS
        self.run_test(
            "6. Reasoning",
            "Cross-Chapter Analysis",
            "Why does Chapter 5 contradict Chapter 2?"
        )
        
        self.run_test(
            "6. Reasoning",
            "Search Query",
            "Search all mentions of entropy"
        )
        
        self.run_test(
            "6. Reasoning",
            "Viva Preparation",
            "Explain like I'm revising for viva"
        )
        
        # 🧪 SYSTEM-LEVEL TESTS
        self.run_test(
            "7. System Tests",
            "Pipeline Integrity",
            "Show me the raw reasoning output before formatting"
        )
        
        self.run_test(
            "7. System Tests",
            "Model Separation",
            "Explain this once without formatting, then format it"
        )
        
        self.run_test(
            "7. System Tests",
            "Zero-Loss Audit",
            "List all concepts in this chapter and mark which are fully covered"
        )
        
        self.run_test(
            "7. System Tests",
            "Boredom Resistance",
            "Rewrite this section to be engaging without losing a single fact"
        )
        
        self.run_test(
            "7. System Tests",
            "Continuation Control",
            "Do not continue unless I explicitly say yes"
        )
        
        # Save all results
        output_file = self.save_results()
        
        print("\n" + "="*60)
        print("🎉 Evaluation Complete!")
        print("="*60)
        print(f"\n📄 Results saved to: {output_file}")
        print("\n📋 Next Steps:")
        print("1. Open the results file")
        print("2. Copy the entire content")
        print("3. Paste into Claude/GPT-4 along with MASTER_EVALUATION_PROMPT.md")
        print("4. Request evaluation and recommendations")
        print("\n")


def main():
    """Main entry point"""
    runner = EvaluationTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
