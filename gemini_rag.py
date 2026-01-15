"""
Gemini-Powered RAG System
Fast, free, and powerful alternative to local Ollama models
Uses the stable google.generativeai SDK
"""

import os
import warnings
import google.generativeai as genai
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Filter warnings
warnings.filterwarnings("ignore")

class GeminiRAG:
    """RAG system using Gemini API for speed"""
    
    def __init__(self, api_key=None, persist_directory="./chroma_db"):
        """Initialize with Gemini API"""
        
        # Get API key
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Please provide GEMINI_API_KEY")
        
        # Configure the stable SDK
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash (Newest & Fastest)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Local embeddings and vector store (privacy preserved)
        print("[INFO] Loading local embeddings...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        
        print("[INFO] Gemini RAG System Ready!")
    
    def ask_question(self, question):
        """Ask a question using Gemini"""
        
        # Search local vector store (GOD MODE: Fetch 30 chunks because Gemini has huge context)
        relevant_docs = self.vector_store.similarity_search(question, k=30)
        
        if not relevant_docs:
            return "❌ No relevant documents found."
        
        # Build context
        context_list = []
        for doc in relevant_docs:
            source = os.path.basename(doc.metadata.get('source', 'Unknown'))
            context_list.append(f"--- SOURCE: {source} ---\n{doc.page_content}")
        
        context = "\n\n".join(context_list)
        
        # Single Gemini call (combines reasoning + formatting)
        prompt = f"""You are a World-Class Professor and Expert Tutor named 'Gemini Pro'. 
Your goal is to provide deep, comprehensive, and highly structured explanations based ONLY on the provided context.

CONTEXT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. **Deep Dive:** Do not just give a summary. Explain the *Why*, *How*, and *What* in depth.
2. **Structure:** Use the following format for every answer:
   - **🎯 Core Concept:** A simple 1-sentence definition.
   - **📖 Detailed Explanation:** The meat of the answer, using paragraphs and bold text.
   - **💡 Key Characteristics/Types:** Use bullet points.
   - **⚖️ Pros & Cons:** (If applicable)
   - **🧪 Real-World Analogy:** (Create a simple analogy to explain complex concepts)
3. **Tone:** Professional yet engaging (like a top-tier university lecturer).
4. **Formatting:** Use Headers (##), Bold (**text**), and Emojis (sparsely) to make it readable.
5. **Coverage:** Use ALL relevant information from the context. If the context covers 1-tier, 2-tier, and 3-tier, explain ALL of them.
6. **Honesty:** If the context is truly missing information, state clearly: "The provided text covers X and Y, but is missing Z."

ANSWER:"""

        try:
            # Call Gemini
            print("[AI] Thinking with Gemini 1.5 Flash...", end="\r")
            
            response = self.model.generate_content(prompt)
            
            print(" " * 50, end="\r")  # Clear the line
            
            return response.text
            
        except Exception as e:
            return f"[ERROR] Gemini API error: {str(e)}"
    
    def interactive_chat(self):
        """Interactive chat mode"""
        print("\n" + "="*60)
        print("GEMINI-POWERED STUDY ASSISTANT")
        print("="*60)
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("\n[YOU]: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if not question:
                    continue
                
                # Get answer
                answer = self.ask_question(question)
                print(f"\n[AI]:\n{answer}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] {str(e)}\n")


# Force UTF-8 encoding for stdout/stderr to handle emojis on Windows
import sys
import io

# Only apply if standard output is attached to a terminal/buffer
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

if __name__ == "__main__":
    
    # Get API key from environment or command line
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("\nGEMINI_API_KEY not found!")
        print("\nPlease set it:")
        print("  Windows: $env:GEMINI_API_KEY=\"your_key_here\"")
        print("  Linux/Mac: export GEMINI_API_KEY=your_key_here")
        print("\nOr get a free key from: https://aistudio.google.com/apikey\n")
        sys.exit(1)
    
    # Initialize and run
    rag = GeminiRAG(api_key=api_key)
    
    # Command line query or interactive
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n[QUERY]: {query}")
        response = rag.ask_question(query)
        # Print with emojis enabled!
        print(f"\n[AI]:\n{response}\n")
    else:
        rag.interactive_chat()
