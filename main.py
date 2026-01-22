import os
import sys
import warnings

# 1. Faster Startup: Ignore unnecessary warnings
warnings.filterwarnings("ignore")

# if sys.platform == "win32":
#     import io
#     sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
        self.last_topic = ""  # Track the last topic discussed
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
        # Process in batches to avoid ChromaDB limits
        BATCH_SIZE = 5000  # Safe batch size under 5461 limit
        print(f"[INFO] Processing {len(chunks)} chunks in batches of {BATCH_SIZE}...")

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"[BATCH {batch_num}/{total_batches}] Adding {len(batch)} chunks...")
            self.vector_store.add_documents(batch)
            print(f"[BATCH {batch_num}/{total_batches}] ✅ Complete")

        print(f"[SUCCESS] All {len(chunks)} chunks indexed!")
        return True

    def load_single_document(self, file_path):
        """Index a single document safely with batching"""
        if not os.path.exists(file_path):
            return False
            
        print(f"[INFO] Indexing single file: {file_path}")
        documents = []
        try:
            if file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif file_path.endswith(".txt"):
                loader = TextLoader(file_path, encoding='utf-8')
                documents.extend(loader.load())
        except Exception as e:
            print(f"[ERROR] Loading file: {e}")
            return False
            
        if not documents:
            return False
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        
        BATCH_SIZE = 5000
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            self.vector_store.add_documents(batch)
            
        print(f"[SUCCESS] Indexed {len(chunks)} chunks from {file_path}")
        return True

    def ask_question(self, question):
        """Ask a question using the 2-step Reasoning (Llama 3) + Formatting (Phi-3) pipeline"""
        try:
            # ============================================================
            # ORCHESTRATION LAYER DELEGATION
            # ============================================================
            # Initialize router if not already done (Lazy Load)
            if not hasattr(self, 'router'):
                from query_router import QueryRouter
                self.router = QueryRouter(self.vector_store)

            # Delegate to Router
            response, handled = self.router.route_and_execute(question)
            
            # If router handled it BUT failed to find the specific page (returned a warning), 
            # fallback to the smart Llama 3 search which might find it via context.
            if handled and "⚠️" not in response:
                return response
            elif handled:
                print(f"[INFO] Router failed to find precise match ('{response.strip()}'). Falling back to Llama 3 Reasoning...")
            # ============================================================
            
            # DEFAULT FALLBACK: STANDARD CONVERSATIONAL RAG
            # Detect conversational keywords
            nav_keywords = ['yes', 'next', 'continue', 'tell me more', 'go on', 'more']
            is_nav = question.lower().strip().rstrip('.') in nav_keywords
            
            search_query = question
            if is_nav and self.last_topic:
                # If user says "next", search for the "next topic after [last_topic]"
                search_query = f"What is the next section or concept after {self.last_topic} in the documents?"
            
            # Search for more chunks (k=5) to get better context
            relevant_docs = self.vector_store.similarity_search(search_query, k=5)
            
            if not relevant_docs:
                return "❌ No relevant documents found. Please load documents first."
            
            # Combine context with source information
            context_list = []
            for i, doc in enumerate(relevant_docs):
                source_file = os.path.basename(doc.metadata.get('source', 'Unknown Document'))
                context_list.append(f"--- SOURCE: {source_file} ---\n{doc.page_content}")
            
            context = "\n\n".join(context_list)
            
            # ---------------------------------------------------------
            # STEP 1: REASONING ENGINE (Llama 3.1 8B)
            # ---------------------------------------------------------
            print("[AI] Thinking with Llama 3.1...", end="\r")
            reasoning_prompt = f"""You are a precise reasoning assistant. 
Your goal is to answer the user's question based ONLY on the provided context.

CONTEXT:
{context}

USER INPUT: {question}
PREVIOUS TOPIC: {self.last_topic}

INSTRUCTIONS:
1. Use only the provided context.
2. Explain step by step.
3. Be factual and structured.
4. If you can't find the answer, say "I cannot find this in your documents."
5. If the user asks for "next", find the logical next concept.

ANSWER:"""

            reasoning_response_obj = ollama.generate(
                model='llama3.1', 
                prompt=reasoning_prompt,
                options={'temperature': 0.1} # Low temp for facts
            )
            raw_answer = reasoning_response_obj['response']

            # ---------------------------------------------------------
            # STEP 2: FORMATTING ENGINE (Phi-3 Mini)
            # ---------------------------------------------------------
            print("[AI] Formatting with Phi-3...    ", end="\r")
            formatting_prompt = f"""Rewrite the following answer to make it extremely readable and engaging.
            
RULES:
- Use a friendly, ChatGPT-like tone.
- Use short paragraphs.
- Use bullet points where helpful.
- Add light emojis (1–2 per section, e.g. 📚, 💡, ✅).
- Do NOT add new information not present in the text below.
- Keep the meaning exactly the same.

ORIGINAL TEXT:
{raw_answer}

REWRITTEN ANSWER:"""

            formatting_response_obj = ollama.generate(
                model='phi3:mini', 
                prompt=formatting_prompt,
                options={'temperature': 0.3} # Slight creativity for style
            )
            final_response = formatting_response_obj['response']
            
            # Try to extract a topic name for next time from the RAW answer (it's usually more structured)
            if ":" in raw_answer[:50]:
                self.last_topic = raw_answer.split(":")[0].replace("**", "").strip()
            elif "next" in question.lower() or not self.last_topic:
                self.last_topic = raw_answer[:50].split('\n')[0].strip()
            
            return final_response
            
        except Exception as e:
            return f"[ERROR] {str(e)}"

    def interactive_chat(self):
        print("\n--- INTERACTIVE STUDY ASSISTANT STARTED ---")
        print("Type 'quit' to exit or 'reload' to update documents.")
        print("Tip: You can now say 'next' or 'yes' to move through the document!")
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
    try:
        if len(qa.vector_store.get()['ids']) == 0:
            qa.load_documents_from_folder()
    except:
        qa.load_documents_from_folder()
    
    
    # Check for command line arguments for direct query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n[QUERY]: {query}")
        response = qa.ask_question(query)
        print(f"\n[AI RESULT]:\n{response}")
    else:
        qa.interactive_chat()
