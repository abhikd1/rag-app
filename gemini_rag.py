"""
Gemini RAG with Fixed Imports and Enhanced Page Chunking (2026)
NUCLEAR FIX: Uses direct file reading for page/section queries to ensure 100% accuracy.
"""
import os
import sys
import json
import re
import shutil
from pathlib import Path

# NEW: Use langchain_huggingface to avoid deprecation warnings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

# FIXED: Use new Google GenAI package
try:
    import google.genai as genai  # NEW package
    USE_NEW_GENAI = True
except ImportError:
    import google.generativeai as genai  # OLD fallback
    USE_NEW_GENAI = False

# FIXED: Use new LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from chatgpt_prompt_template import (
    get_page_explanation_prompt,
    get_general_question_prompt,
    get_concept_explanation_prompt
)

class GeminiRAG:
    def __init__(self, api_key=None, persist_directory="./chroma_db"):
        """Initialize Gemini RAG"""
        
        print("\n" + "="*60)
        print("🚀 Initializing Gemini RAG (2026 Enhanced)")
        print("="*60)
        
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Please provide GEMINI_API_KEY")

        # Configure Gemini with new or old API
        if USE_NEW_GENAI:
            self.client = genai.Client(api_key=api_key)
            self.model_name = 'gemini-2.0-flash-exp'
            self.is_new_api = True
            print("✅ Using NEW google.genai API")
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.is_new_api = False
            print("⚠️ Using OLD google.generativeai API (deprecated)")
        
        # Initialize embeddings with optimal settings
        print("📊 Loading embeddings model (langchain-huggingface)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )
        
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.current_file = None 
        self.page_index = {}
        
        # Load existing ChromaDB if it looks like it's already indexed
        if Path(self.persist_directory).exists():
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print(f"✅ Loaded existing ChromaDB ({self.vectorstore._collection.count()} chunks)")
            except:
                print("⚠️ Could not load existing ChromaDB")

        print("✅ RAG ready")
        print("="*60 + "\n")

    def load_specific_file(self, pdf_name):
        """Load ONLY one specific PDF file with enhanced page-based chunking"""
        
        print(f"\n{'='*60}")
        print(f"📂 Loading ONLY: {pdf_name}")
        print(f"{'='*60}")
        
        docs_folder = Path("documents")
        base_name = Path(pdf_name).stem
        
        raw_file = docs_folder / f"{base_name}_RAW_TEXT.txt"
        page_index_file = docs_folder / f"{base_name}_PAGE_INDEX.json"
        
        if not raw_file.exists():
            print(f"❌ Not extracted: {raw_file}")
            return False
        
        # Load page index
        if page_index_file.exists():
            with open(page_index_file, 'r', encoding='utf-8') as f:
                self.page_index = json.load(f)
            print(f"✅ Page index Loaded: {len(self.page_index)} pages")
        
        # Load content
        content = raw_file.read_text(encoding='utf-8')
        print(f"✅ Loaded: {len(content)} characters")
        
        # Enhanced Page-Based Chunking
        page_pattern = r'=== PAGE (\d+) ==='
        # Split by page marker, keep delimiters to get page numbers
        parts = re.split(page_pattern, content)
        
        all_chunks = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # parts[0] is usually empty or header. 
        # parts[1] is page_num, parts[2] is content, etc.
        for i in range(1, len(parts), 2):
            page_num = int(parts[i])
            page_content = parts[i+1].strip()
            
            if page_content:
                # Split this specific page into chunks
                page_chunks = text_splitter.split_text(page_content)
                for chunk_idx, chunk in enumerate(page_chunks):
                    # Decorate the chunk with the page marker again for search
                    decorated_chunk = f"=== PAGE {page_num} ===\n\n{chunk}"
                    all_chunks.append(Document(
                        page_content=decorated_chunk,
                        metadata={
                            "source": pdf_name,
                            "file": pdf_name,
                            "page": page_num,
                            "chunk": chunk_idx
                        }
                    ))
        
        print(f"📊 Created {len(all_chunks)} chunks from {len(parts)//2} pages")
        
        # Delete old vector store
        if Path(self.persist_directory).exists():
            try:
                shutil.rmtree(self.persist_directory)
                print("🗑️ Deleted old vector database")
            except: pass
        
        # Create NEW vector store
        self.vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        self.current_file = pdf_name
        print(f"✅ Vector store ready with ONLY {pdf_name}")
        print(f"{'='*60}\n")
        
        return True

    def _get_full_page_from_raw_file(self, page_num):
        """NUCLEAR FIX: Read FULL page content directly from disk for 100% accuracy"""
        try:
            if not self.current_file: return None
            base_name = Path(self.current_file).stem
            raw_file = f"documents/{base_name}_RAW_TEXT.txt"
            
            if not Path(raw_file).exists(): return None
            
            with open(raw_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find page markers
            page_start = f"=== PAGE {page_num} ==="
            page_end = f"=== PAGE {page_num + 1} ==="
            
            start_idx = content.find(page_start)
            if start_idx == -1: return None
            
            end_idx = content.find(page_end)
            
            if end_idx == -1:
                page_content = content[start_idx:]
            else:
                page_content = content[start_idx:end_idx]
            
            # Cleanup
            page_content = page_content.replace(page_start, '').strip()
            page_content = re.sub(r'={3,}', '', page_content).strip()
            
            return page_content
            
        except Exception as e:
            print(f"Error reading page {page_num}: {e}")
            return None

    def _find_pages_with_section(self, section_num):
        """Find all pages that contain a specific section number"""
        try:
            if not self.current_file: return []
            base_name = Path(self.current_file).stem
            raw_file = f"documents/{base_name}_RAW_TEXT.txt"
            
            if not Path(raw_file).exists(): return []
            
            with open(raw_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pages_found = []
            page_markers = list(re.finditer(r'=== PAGE (\d+) ===', content))
            
            for i, marker in enumerate(page_markers):
                page_num = int(marker.group(1))
                start_idx = marker.end()
                end_idx = page_markers[i+1].start() if i+1 < len(page_markers) else len(content)
                
                page_content = content[start_idx:end_idx]
                
                # Check for section number with boundary
                if re.search(rf'\b{re.escape(section_num)}\b', page_content):
                    pages_found.append(page_num)
            
            return pages_found
        except Exception as e:
            print(f"Error finding section {section_num}: {e}")
            return []

    def _format_raw_content(self, content, page_num):
        """Format raw content nicely with emojis but keep exact text"""
        lines = content.split('\n')
        formatted = f"# 📖 PAGE {page_num} - RAW CONTENT\n\n"
        formatted += "---\n\n"
        
        in_code_block = False
        for line in lines:
            ls = line.strip()
            if not ls:
                if in_code_block: 
                    formatted += "```\n\n"
                    in_code_block = False
                continue
            
            # Headings
            if re.match(r'^\d+\.\d+', ls):
                if in_code_block: formatted += "```\n"
                in_code_block = False
                formatted += f"\n## 📌 {ls}\n\n"
            elif ls.startswith(('Program ', 'Activity ', 'Output of ')):
                if in_code_block: formatted += "```\n"
                in_code_block = False
                emoji = '💻' if 'Program' in ls else ('🎯' if 'Activity' in ls else '📊')
                formatted += f"\n### {emoji} {ls}\n\n"
            # Code line detection
            elif (line.startswith('    ') or line.startswith('\t')) and not in_code_block:
                formatted += f"```python\n{line}\n"
                in_code_block = True
            elif (line.startswith('    ') or line.startswith('\t')) and in_code_block:
                formatted += f"{line}\n"
            else:
                if in_code_block: 
                    formatted += "```\n"
                    in_code_block = False
                formatted += f"{ls}\n\n"
        
        if in_code_block: formatted += "```\n"
        formatted += "\n---\n\n"
        formatted += f"*️⃣ *Note: Verbatim text from Page {page_num}*\n"
        return formatted

    def analyze_document(self):
        """Perform a deep analysis of the document content"""
        if not self.current_file: return "❌ No file loaded."
        
        try:
            base_name = Path(self.current_file).stem
            raw_file = f"documents/{base_name}_RAW_TEXT.txt"
            
            with open(raw_file, 'r', encoding='utf-8') as f:
                # Read first ~50k characters for analysis
                content = f.read(50000) 
            
            prompt = f"""Analyze this document thoroughly and provide a high-level educational breakdown.
            
Provide:
1.  **Overview**: What is this document about?
2.  **Key Topics**: List the main chapters/sections.
3.  **Target Audience**: Who is this for?
4.  **Learning Objectives**: What will the reader learn?

CONTENT SNIPPET:
{content}
"""
            if self.is_new_api:
                response = self.client.models.generate_content(model=self.model_name, contents=prompt)
                return response.text
            else:
                response = self.model.generate_content(prompt)
                return response.text
                
        except Exception as e:
            return f"❌ Analysis Error: {str(e)}"

    def ask_question(self, question):
        """Ask question - FIXED VERSION with proper page detection"""
        print(f"\n{'='*60}")
        print(f"❓ QUESTION: {question}")
        if self.current_file: print(f"📂 ACTIVE FILE: {self.current_file}")
        print(f"{'='*60}")
        
        if not self.vectorstore:
            return "❌ No documents loaded. Please upload a PDF first."
        
        # ANALYZE MODE
        if 'analyze' in question.lower():
            # Check if it's a short "analyze" command (ignoring the prepended context if any)
            # The server prepends a lot of text, so we check for the specific phrase
            if "analyze this document" in question.lower() or len(question.strip()) < 100:
                return self.analyze_document()

        # Mode detection
        is_raw_mode = any(kw in question.lower() for kw in ['raw', 'exact text', 'verbatim', '[raw]'])
        
        # Tools detection
        if any(kw in question.lower() for kw in ['index', 'table of contents', 'toc', 'all topics']):
            return self.get_document_index()
        if any(kw in question.lower() for kw in ['page summary', 'page-by-page']):
            return self.get_page_summary_table()
            
        # DETECT PAGE NUMBER
        page_match = re.search(r'page\s+(\d+)', question.lower())
        if page_match:
            page_num = int(page_match.group(1))
            print(f"📄 Handling PAGE {page_num} query")
            page_content = self._get_full_page_from_raw_file(page_num)
            
            if not page_content: return f"❌ Page {page_num} not found."
            if is_raw_mode: return self._format_raw_content(page_content, page_num)
            
            # EXPLAIN MODE
            prompt = f"Explain PAGE {page_num} from the textbook. Content:\n\n{page_content}\n\nTasks: Summarize key points, explain code/tables if any. Use emojis. BE ACCURATE TO THIS TEXT."
        
        else:
            # SECTION QUERY
            sect_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', question)
            if sect_match:
                section_num = sect_match.group(1)
                print(f"🔍 Handling SECTION {section_num} query")
                pages = self._find_pages_with_section(section_num)
                
                if not pages:
                    # Fallback to vector search if section number not literally found
                    print("⚠️ Section not found literally, falling back to search")
                else:
                    full_content = ""
                    for p in pages:
                        p_cont = self._get_full_page_from_raw_file(p)
                        if p_cont: full_content += f"\n\n--- PAGE {p} ---\n\n{p_cont}"
                    
                    if is_raw_mode:
                        res = f"# 📖 RAW CONTENT - Section {section_num}\n\n"
                        for p in pages:
                            res += self._format_raw_content(self._get_full_page_from_raw_file(p), p) + "\n\n"
                        return res
                    
                    prompt = f"Explain Section {section_num} based on this content:\n\n{full_content}\n\nBe thorough and engaging."
            
            # DEFAULT: VECTOR SEARCH
            if 'prompt' not in locals():
                print("🔍 Generic semantic search...")
                docs = self.vectorstore.similarity_search(question, k=5)
                if not docs: return "❌ No relevant content found."
                context = "\n\n---\n\n".join([d.page_content for d in docs])
                prompt = f"Answer this using the context provided:\n\nContext:\n{context}\n\nQuestion: {question}"

        # Generate response
        try:
            if self.is_new_api:
                response = self.client.models.generate_content(model=self.model_name, contents=prompt)
                return response.text
            else:
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def get_document_index(self):
        if not self.current_file: return "❌ No document loaded."
        from index_generator_fixed import generate_hierarchical_index
        return generate_hierarchical_index(self.current_file)
    
    def get_page_summary_table(self):
        if not self.current_file: return "❌ No document loaded."
        from index_generator import generate_page_summary
        return f"# 📄 PAGE-BY-PAGE SUMMARY\n\n" + generate_page_summary(self.current_file)

if __name__ == "__main__":
    rag = GeminiRAG(api_key=os.getenv('GEMINI_API_KEY'))
    if len(sys.argv) > 1: print(rag.ask_question(" ".join(sys.argv[1:])))
    else:
        while True:
            q = input("\n[YOU]: "); 
            if q.lower() in ['q', 'quit']: break
            print(f"\n[AI]:\n{rag.ask_question(q)}")
