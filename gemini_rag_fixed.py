"""
FIXED Gemini RAG - Forces vector search and uses retrieved content
"""
import os
from pathlib import Path
import google.generativeai as genai
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class GeminiRAGFixed:
    def __init__(self, api_key, persist_directory="./chroma_db"):
        """Initialize Gemini RAG with FORCED vector search"""
        
        print("\n" + "="*60)
        print("🚀 Initializing FIXED Gemini RAG")
        print("="*60)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        # Using the model specified by the user
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize embeddings
        print("📊 Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Load documents
        self.persist_directory = persist_directory
        self.load_documents()
        
        print("="*60 + "\n")
    
    def load_documents(self):
        """Load documents from folder"""
        docs_folder = Path("documents")
        
        if not docs_folder.exists():
            print("❌ Documents folder not found!")
            self.vectorstore = None
            return
        
        # Load only _RAW_TEXT.txt files (these are extracted PDFs)
        txt_files = list(docs_folder.glob("*_RAW_TEXT.txt"))
        
        if not txt_files:
            print("❌ No extracted text files found!")
            print("   Run: python mode_a_extractor.py documents/yourfile.pdf")
            self.vectorstore = None
            return
        
        print(f"📄 Found {len(txt_files)} extracted text files")
        for f in txt_files:
            print(f"   - {f.name}")
        
        # Load all text files
        documents = []
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Create document with metadata
                    from langchain_core.documents import Document
                    doc = Document(
                        page_content=content,
                        metadata={'source': txt_file.stem.replace('_RAW_TEXT', '')}
                    )
                    documents.append(doc)
                    print(f"✅ Loaded: {txt_file.name} ({len(content)} chars)")
            except Exception as e:
                print(f"❌ Error loading {txt_file.name}: {e}")
        
        if not documents:
            print("❌ No documents loaded!")
            self.vectorstore = None
            return
        
        # Split documents
        print(f"\n📊 Splitting {len(documents)} documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        print(f"✅ Created {len(splits)} chunks")
        
        # Create/load vector store
        print(f"\n💾 Creating vector store in {self.persist_directory}...")
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print(f"✅ Vector store ready with {len(splits)} chunks")
    
    def ask_question(self, question):
        """Ask question with FORCED vector search"""
        
        print(f"\n{'='*60}")
        print(f"❓ QUESTION: {question}")
        print(f"{'='*60}")
        
        # Check if vector store exists
        if not self.vectorstore:
            return "❌ ERROR: No documents loaded in vector database. Please upload and process PDFs first."
        
        # FORCE vector search
        print("🔍 Searching vector database...")
        try:
            # Retrieve relevant documents
            retrieved_docs = self.vectorstore.similarity_search(
                question,
                k=5  # Get top 5 most relevant chunks
            )
            
            if not retrieved_docs:
                return "❌ No relevant documents found in database. Please upload PDFs."
            
            print(f"✅ Found {len(retrieved_docs)} relevant chunks:")
            for i, doc in enumerate(retrieved_docs, 1):
                source = doc.metadata.get('source', 'unknown')
                preview = doc.page_content[:100].replace('\n', ' ')
                print(f"   {i}. From '{source}': {preview}...")
            
            # Build context from retrieved docs
            context = "\n\n---\n\n".join([
                f"Document: {doc.metadata.get('source', 'unknown')}\n\n{doc.page_content}"
                for doc in retrieved_docs
            ])
            
            print(f"\n📝 Context length: {len(context)} chars")
            
            # Create prompt that FORCES use of context
            prompt = f"""You are analyzing documents that have been uploaded and indexed.

RETRIEVED DOCUMENT CONTENT (you MUST use this):
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer ONLY using the content from the retrieved documents above
2. Do NOT say you cannot access files - you have the content right above
3. Be specific and cite which document the information comes from
4. If the retrieved content doesn't answer the question, say "The uploaded documents don't contain information about this topic"

ANSWER:"""

            print("\n🤖 Generating response with Gemini...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            print("✅ Response generated")
            print(f"{'='*60}\n")
            
            return response.text
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return f"❌ Error searching documents: {str(e)}"

# Test function
if __name__ == "__main__":
    # Test the fixed RAG
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Set GEMINI_API_KEY environment variable!")
        exit(1)
    
    rag = GeminiRAGFixed(api_key=api_key)
    
    # Test query
    response = rag.ask_question("What documents do you have? List them.")
    print("\n📄 RESPONSE:")
    print(response)
