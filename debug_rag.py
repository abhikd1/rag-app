"""
Debug script to see what's in ChromaDB and test queries
"""
import os
import sys
from pathlib import Path

# Add core path
sys.path.append(os.getcwd())

# Set API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyDrb-4g0a68X2Ly7LhP7_Ip0ubeJdkxBwQ'

from gemini_rag import GeminiRAG

def debug_system():
    print("\n" + "="*70)
    print("🔍 RAG SYSTEM DEBUG")
    print("="*70)
    
    # Check documents folder
    docs_dir = Path('documents')
    if docs_dir.exists():
        files = list(docs_dir.glob('*.pdf'))
        print(f"\n📁 Documents folder: {len(files)} PDFs")
        for f in files[:5]:
            print(f"   - {f.name}")
    else:
        print("\n❌ Documents folder doesn't exist!")
    
    # Check extracted text files
    raw_files = list(docs_dir.glob('*_RAW_TEXT.txt')) if docs_dir.exists() else []
    print(f"\n📄 Extracted text files: {len(raw_files)}")
    for f in raw_files[:5]:
        print(f"   - {f.name}")
    
    # Check ChromaDB
    chroma_path = Path('chroma_db')
    if chroma_path.exists():
        print(f"\n💾 ChromaDB exists: YES")
        # Count files in ChromaDB
        chroma_files = list(chroma_path.rglob('*'))
        print(f"   Files in ChromaDB: {len(chroma_files)}")
    else:
        print(f"\n💾 ChromaDB exists: NO ❌")
    
    # Try to initialize RAG
    print("\n🤖 Initializing RAG...")
    try:
        rag = GeminiRAG(api_key=os.environ['GEMINI_API_KEY'])
        print("✅ RAG initialized")
        
        # Try a test query
        print("\n🔍 Testing query...")
        response = rag.ask_question("What documents do you have access to?")
        print(f"\n📝 Response length: {len(response)} chars")
        print(f"\n📝 First 200 chars of response:")
        print(response[:200])
        
        # Check if it's actually searching
        if "cannot" in response.lower() or "don't have access" in response.lower() or "not find" in response.lower():
            print("\n❌ RAG is NOT searching vector database!")
            print("   It's giving generic LLM responses")
        else:
            print("\n✅ RAG seems to be working")
        
    except Exception as e:
        print(f"❌ RAG initialization failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    debug_system()
