"""
Groq RAG with Fixed Imports and Enhanced Page Chunking (2026)
"""
import os
import sys
import json
import re
import shutil
import time
from pathlib import Path
from groq import Groq

# NEW: Use langchain_huggingface to avoid deprecation warnings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

# FIXED: Use new LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

class GroqRAG:
    def __init__(self, api_key, persist_directory="./chroma_db"):
        """Initialize Groq RAG"""
        
        print("\n" + "="*60)
        print("⚡ Warming up Groq LPU Engines (2026 Enhanced)")
        print("="*60)
        
        self.client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"
        
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

        print("✅ System Online: Groq Ready")
        print("="*60 + "\n")

    def load_specific_file(self, pdf_name):
        """Load ONLY one specific PDF file with enhanced page-based chunking"""
        
        print(f"\n{'='*60}")
        print(f"📂 [GROQ] Loading ONLY: {pdf_name}")
        print(f"{'='*60}")
        
        docs_folder = Path("documents")
        base_name = Path(pdf_name).stem
        
        raw_file = docs_folder / f"{base_name}_RAW_TEXT.txt"
        page_index_file = docs_folder / f"{base_name}_PAGE_INDEX.json"
        
        if not raw_file.exists():
            print(f"❌ Not extracted: {raw_file}")
            return False
        
        # Load content
        content = raw_file.read_text(encoding='utf-8')
        
        # Enhanced Page-Based Chunking
        page_pattern = r'=== PAGE (\d+) ==='
        parts = re.split(page_pattern, content)
        
        all_chunks = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        for i in range(1, len(parts), 2):
            page_num = int(parts[i])
            page_content = parts[i+1].strip()
            
            if page_content:
                page_chunks = text_splitter.split_text(page_content)
                for chunk_idx, chunk in enumerate(page_chunks):
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
        
        # ✅ CRITICAL: Check if we have chunks before creating vectorstore
        if not all_chunks:
            print(f"❌ CRITICAL ERROR: No content extracted from {pdf_name}")
            return False
            
        print(f"📊 [GROQ] Created {len(all_chunks)} chunks")
        
        # Delete old vector store
        if Path(self.persist_directory).exists():
            try:
                shutil.rmtree(self.persist_directory)
            except: pass
        
        # Create NEW vector store
        self.vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        self.current_file = pdf_name
        print(f"✅ [GROQ] Vector store ready")
        print(f"{'='*60}\n")
        
        return True

    def get_page_content(self, page_num):
        """FIXED: Get exact content from RAW_TEXT file, not vectorstore"""
        if self.current_file:
            docs_folder = Path("documents")
            base_name = Path(self.current_file).stem
            raw_file = docs_folder / f"{base_name}_RAW_TEXT.txt"
            
            if raw_file.exists():
                try:
                    with open(raw_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find this page's markers
                    start_marker = f"=== PAGE {page_num} ==="
                    next_page_marker = f"=== PAGE {page_num + 1} ==="
                    
                    start_idx = content.find(start_marker)
                    if start_idx == -1: return None
                    
                    # Move past the marker line
                    start_idx = content.find('\n', start_idx) + 1
                    
                    # Find where this page ends
                    end_idx = content.find(next_page_marker, start_idx)
                    if end_idx == -1:
                        page_content = content[start_idx:].strip()
                    else:
                        page_content = content[start_idx:end_idx].strip()
                    
                    # Remove ONLY big separator bars
                    page_content = re.sub(r'^={15,}.*$', '', page_content, flags=re.MULTILINE).strip()
                    return page_content if len(page_content) > 10 else None
                except: return None
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

    def get_raw_content(self, query):
        """Get RAW book content WITHOUT AI explanation - Improved with page detection"""
        print(f"\n{'='*60}")
        print(f"📄 [GROQ] RAW MODE: {query}")
        print(f"{'='*60}")
        
        if not self.vectorstore:
            return "❌ No documents loaded."
        
        page_match = re.search(r'page\s+(\d+)', query.lower())
        if page_match:
            page_num = int(page_match.group(1))
            page_content = self.get_page_content(page_num)
            if not page_content:
                return f"❌ Could not find content for page {page_num}"
            return self._format_raw_content(page_content, page_num)
        
        # Check for section
        sect_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', query)
        if sect_match:
            section_num = sect_match.group(1)
            pages = self._find_pages_with_section(section_num)
            if pages:
                results = f"# 📖 RAW CONTENT - Section {section_num}\n\n"
                for p in pages:
                    p_cont = self.get_page_content(p)
                    if p_cont:
                        results += self._format_raw_content(p_cont, p) + "\n\n"
                return results
        
        # Default to multi-page search results but deduplicated by page
        docs = self.vectorstore.similarity_search(query, k=10)
        if not docs:
            return "❌ No relevant content found."
        
        unique_pages = sorted(list(set([doc.metadata.get('page') for doc in docs])))
        results = f"# 📖 RAW CONTENT SEARCH RESULTS\n\n"
        for p in unique_pages:
            p_cont = self._get_full_page_from_raw_file(p)
            if p_cont:
                results += self._format_raw_content(p_cont, p) + "\n\n"
        
        return results

    def analyze_document(self):
        """Perform a deep analysis of the document content"""
        if not self.current_file: return "❌ No file loaded."
        
        try:
            base_name = Path(self.current_file).stem
            raw_file = f"documents/{base_name}_RAW_TEXT.txt"
            
            with open(raw_file, 'r', encoding='utf-8') as f:
                # Read first ~10 pages for analysis if too large
                content = f.read(50000) 
            
            prompt = f"""Analyze this document thoroughly.
Provide:
1.  **Overview**: What is this document about?
2.  **Key Topics**: List the main chapters/sections.
3.  **Target Audience**: Who is this for?
4.  **Learning Objectives**: What will the reader learn?

CONTENT SNIPPET:
{content}
"""
            messages = [
                {"role": "system", "content": "You are a senior academic analyst. Provide a professional, deep analysis of the provided textbook content."},
                {"role": "user", "content": prompt}
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
            )
            return completion.choices[0].message.content
            
        except Exception as e:
            return f"❌ Analysis Error: {str(e)}"

    def ask_question(self, question):
        """Unified ask_question interface for Groq - HARMONIZED VERSION"""
        
        print(f"\n{'='*60}")
        print(f"❓ QUESTION: {question}")
        if self.current_file:
            print(f"📂 ACTIVE FILE: {self.current_file}")
        print(f"{'='*60}")
        
        if not self.vectorstore:
            return "❌ No file loaded. Please upload a PDF first."

        # ANALYZE MODE
        if 'analyze' in question.lower():
            if "analyze this document" in question.lower() or len(question.strip()) < 100:
                return self.analyze_document()

        # RAW MODE detection
        is_raw_mode = any(keyword in question.lower() for keyword in ['raw', 'exact text', 'verbatim', '[raw]'])
        
        # TOOLS detection
        if any(keyword in question.lower() for keyword in ['index', 'table of contents', 'toc', 'all topics']):
            return self.get_document_index()
        
        if any(kw in question.lower() for kw in ['page summary', 'page-by-page', 'all pages']):
            return self.get_page_summary_table()

        # DETECT PAGE NUMBER
        page_match = re.search(r'page\s+(\d+)', question.lower())
        if page_match:
            page_num = int(page_match.group(1))
            print(f"📄 [GROQ] Handling PAGE {page_num} query")
            page_content = self.get_page_content(page_num)
            
            if not page_content:
                return f"❌ Page {page_num} not found or empty."
            
            if is_raw_mode: return self._format_raw_content(page_content, page_num)
            
            # EXPLAIN MODE
            from chatgpt_prompt_template import get_page_explanation_prompt
            system_prompt = "You are a strict anti-hallucination educational AI tutor."
            user_content = get_page_explanation_prompt(
                page_num=page_num,
                page_content=page_content,
                filename=self.current_file or "document"
            )

        else:
            # SECTION DETECT
            sect_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', question)
            if sect_match:
                section_num = sect_match.group(1)
                print(f"🔍 [GROQ] Targeted Section {section_num}")
                pages = self._find_pages_with_section(section_num)
                
                if pages:
                    full_content = ""
                    for p in pages:
                        p_cont = self.get_page_content(p)
                        if p_cont: full_content += f"\n\n--- PAGE {p} ---\n\n{p_cont}"
                    
                    if is_raw_mode:
                        res = f"# 📖 RAW CONTENT - Section {section_num}\n\n"
                        for p in pages:
                            res += self._format_raw_content(self.get_page_content(p), p) + "\n\n"
                        return res
                    
                    system_prompt = "You are an educational AI tutor. Explain the following section content accurately and thoroughly."
                    user_content = f"Content for Section {section_num}:\n{full_content}\n\nQuestion: {question}"
                else:
                    # Fallback to search
                    print("⚠️ Section not found literally, falling back to search")
            
            if 'user_content' not in locals():
                # General Query - Semantic Search
                print("🔍 [GROQ] General Search")
                docs = self.vectorstore.similarity_search(question, k=10)
                if is_raw_mode: return self.get_raw_content(question)
                
                if not docs:
                    return "❌ No relevant context found."
                
                context = "\n\n---\n\n".join([f"[Page {d.metadata.get('page')}]\n{d.page_content}" for d in docs])
                system_prompt = "You are an educational AI tutor. Answer using the provided context. Use rich formatting and emojis."
                user_content = f"Context:\n{context}\n\nQuestion: {question}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        try:
            print("🚀 Thinking at Groq speed...")
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.4,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"❌ Groq Error: {str(e)}"

    def get_page_content(self, page_num):
        """FIXED: Get exact content from RAW_TEXT file"""
        if self.current_file:
            docs_folder = Path("documents")
            base_name = Path(self.current_file).stem
            raw_file = docs_folder / f"{base_name}_RAW_TEXT.txt"
            
            if raw_file.exists():
                try:
                    with open(raw_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    start_marker = f"=== PAGE {page_num} ==="
                    next_page_marker = f"=== PAGE {page_num + 1} ==="
                    
                    start_idx = content.find(start_marker)
                    if start_idx == -1: return None
                    
                    start_idx = content.find('\n', start_idx) + 1
                    end_idx = content.find(next_page_marker, start_idx)
                    
                    if end_idx == -1:
                        page_content = content[start_idx:].strip()
                    else:
                        page_content = content[start_idx:end_idx].strip()
                        
                    page_content = re.sub(r'={60,}\n?', '', page_content).strip()
                    return page_content if len(page_content) > 10 else None
                except: return None
        return None

    def get_document_index(self):
        """Get the complete hierarchical topic-wise index for current document"""
        if not self.current_file:
            return "❌ No document loaded. Please upload a PDF first."
        
        from index_generator_fixed import generate_hierarchical_index
        return generate_hierarchical_index(self.current_file)
    
    def get_page_summary_table(self):
        """Get page-by-page summary list"""
        if not self.current_file:
            return "❌ No document loaded. Please upload a PDF first."
        
        from index_generator import IndexGenerator
        
        base_name = Path(self.current_file).stem
        raw_text_file = f"documents/{base_name}_RAW_TEXT.txt"
        
        if not Path(raw_text_file).exists():
            return f"❌ RAW_TEXT file not found for {self.current_file}"
        
        generator = IndexGenerator(raw_text_file)
        result = generator.generate_page_summary_table()
        return f"# 📄 PAGE-BY-PAGE SUMMARY\n\n{result}"

    def ask(self, question):
        return self.ask_question(question)

if __name__ == "__main__":
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("Please set GROQ_API_KEY")
        sys.exit(1)
    
    rag = GroqRAG(api_key=key)
    if len(sys.argv) > 1:
        print(rag.ask_question(" ".join(sys.argv[1:])))
    else:
        print("Interactive mode: Type 'quit' to exit.")
        while True:
            q = input("\n[GROQ]: ")
            if q.lower() in ['q', 'quit']: break
            print(f"\n[AI]:\n{rag.ask_question(q)}")

