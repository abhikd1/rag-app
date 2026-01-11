from PyPDF2 import PdfReader
import sys
import re

# Fix encoding for Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_book_index(pdf_path):
    reader = PdfReader(pdf_path)
    index = []
    
    # regex for main headings (e.g., "1. Topic" or "10. Topic")
    main_head_re = re.compile(r'^(\d+)\.\s+([A-Z\s\-]+)$|^([A-Z\s]{5,})$')
    # regex for sub headings (e.g., "1.1. Topic")
    sub_head_re = re.compile(r'^(\d+\.\d+)\.?\s+(.+)$')
    # regex for numbered lists (e.g., "1) Topic")
    list_re = re.compile(r'^(\d+)\)\s+(.+)$')

    print("# 📚 BOOK INDEX: DBMS.PDF\n")
    
    current_main = None

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text: continue
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # 1. Check for Chapters/Main Heads (e.g. "1. INTRODUCTION")
            main_match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if main_match and len(line) < 60 and not '.' in main_match.group(2):
                num, title = main_match.groups()
                print(f"\n## 📘 CHAPTER {num}: {title.upper()}")
                current_main = num
                continue
                
            # 2. Check for Sub-headings (e.g. "1.1. Data Modeling")
            sub_match = sub_head_re.match(line)
            if sub_match:
                num, title = sub_match.groups()
                print(f"   🔹 {num} {title}")
                continue

            # 3. Check for specific important keywords if they look like headers
            if line.startswith('') and len(line) < 50:
                print(f"      ◦ {line[1:].strip()}")
                continue
            
            if "ARCHITECTURE" in line.upper() and len(line) < 30:
                 print(f"   🏗️ {line}")

if __name__ == "__main__":
    generate_book_index(r"c:\Users\sumit\rag app\documents\dbms.pdf")
