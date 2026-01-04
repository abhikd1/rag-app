"""
Refined indexing script for the Computer Science Chapter 2 PDF.
Correctly splits content by the page markers used by mode_a_extractor.
"""

import os
import sys
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.database.vector_store.client import VectorStoreClient
from langchain_core.documents import Document
from core.logging.logger import LoggerFactory

def index_file(file_path):
    logger = LoggerFactory.get_logger(__name__)
    print(f"[INFO] Indexing: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by the page marker "📄 PAGE X"
    # The pattern is usually:
    # ================================================================================
    # 📄 PAGE X
    # ================================================================================
    
    chunks = re.split(r'={10,}\n📄 PAGE \d+\n={10,}', content)
    
    # The first chunk is the metadata header
    header = chunks[0]
    page_chunks = chunks[1:]
    
    documents = []
    
    for i, chunk in enumerate(page_chunks):
        page_num = i + 1
        page_text = chunk.strip()
        
        if not page_text:
            continue
            
        doc = Document(
            page_content=f"PAGE {page_num}\n\n{page_text}",
            metadata={"source": "computer 12ch2.pdf", "page": page_num}
        )
        documents.append(doc)

    if not documents:
        print("[WARNING] No pages found. Trying fallback split logic...")
        # Fallback: just split by "PAGE"
        pages = content.split("PAGE")
        for i, p in enumerate(pages[1:]): # skip header
            doc = Document(
                page_content=f"PAGE {i+1}\n\n{p.strip()}",
                metadata={"source": "computer 12ch2.pdf", "page": i+1}
            )
            documents.append(doc)

    print(f"[INFO] Prepared {len(documents)} document pages.")
    
    client = VectorStoreClient()
    success = client.add_documents(documents)
    
    if success:
        print(f"[SUCCESS] Successfully indexed {len(documents)} pages from Computer Science Chapter 2.")
    else:
        print("[ERROR] Indexing failed.")

if __name__ == "__main__":
    raw_text_path = r"c:\Users\sumit\rag app\documents\computer 12ch2_RAW_TEXT.txt"
    index_file(raw_text_path)
