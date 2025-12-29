import os
import sys
import warnings

# 1. Faster Startup: Ignore unnecessary warnings
warnings.filterwarnings("ignore")

# 2. Fix Windows Terminal Encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama

class FreeDocumentQA:
    def __init__(self, persist_directory="./chroma_db"):
        print("[INFO] Loading 'Understanding' model... (Fast after first run)")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load or create the vector store
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        print("[INFO] RAG System Ready!")

    def load_documents_from_folder(self, folder_path="./documents"):
        """Focus ONLY on the documents folder"""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        print(f"[INFO] Scanning folder: {folder_path}")
        documents = []
        
        # Load PDF and TXT specifically using simple loaders to avoid indexing metadata files
        try:
            # We use glob patterns to find files
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if file.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())
                elif file.endswith(".txt"):
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents.extend(loader.load())
        except Exception as e:
            print(f"[ERROR] Loading files: {e}")
        
        if not documents:
            print("[ERROR] No files found in 'documents' folder. Add a PDF/TXT and type 'reload'.")
            return False
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        
        print(f"[INFO] Indexing {len(chunks)} sections from {len(documents)} document pages...")
        # Clear old and add new to avoid duplicates for the example
        self.vector_store.add_documents(chunks)
        return True

    def ask_question(self, question):
        try:
            # Search for more chunks (k=5) to get better context
            relevant_docs = self.vector_store.similarity_search(question, k=5)
            
            if not relevant_docs:
                return "❌ No relevant documents found. Please load documents first."
            
            # Combine context with source information
            context_list = []
            for i, doc in enumerate(relevant_docs):
                source_file = os.path.basename(doc.metadata.get('source', 'Unknown Document'))
                context_list.append(f"--- SOURCE: {source_file} ---\n{doc.page_content}")
            
            context = "\n\n".join(context_list)
            
            # Create a more structured prompt
            prompt = f"""You are a precise study assistant. Your goal is to answer questions based ONLY on the provided context.

CONTEXT FROM USER DOCUMENTS:
{context}

QUESTION: {question}

STRICT RED-LINE RULES:
1. Only use facts from the context above.
2. If the context contains multiple conflicting values, prioritize the one from '.txt' files.
3. If you can't find the answer, say "I cannot find this in your documents."
4. Mention the source file name in your answer (e.g., "According to [file.txt]...").

ANSWER:"""
            
            # Use the cloud model to save local memory
            response = ollama.generate(
                model='gpt-oss:120b-cloud', 
                prompt=prompt,
                options={'temperature': 0} # 0 temperature for maximum accuracy
            )
            
            return response['response']
            
        except Exception as e:
            return f"[ERROR] {str(e)}"

    def interactive_chat(self):
        print("\n--- STUDY ASSISTANT STARTED ---")
        print("Type 'quit' to exit or 'reload' to update documents.")
        while True:
            query = input("\n[YOU]: ").strip()
            if query.lower() in ['quit', 'exit']: break
            if query.lower() == 'reload': 
                self.load_documents_from_folder()
                continue
            if not query: continue
            
            print("[THINKING]...", end="\r")
            answer = self.ask_question(query)
            print(f"[AI]: {answer}")

if __name__ == "__main__":
    qa = FreeDocumentQA()
    # If the database is empty, load documents
    if len(qa.vector_store.get()['ids']) == 0:
        qa.load_documents_from_folder()
    
    qa.interactive_chat()
