import fitz  # PyMuPDF
import os
import sys
import re

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def detect_heading(text, font_size=None):
    """
    Detect if a line is likely a heading based on:
    - All caps
    - Short length
    - Starts with "Chapter" or numbered pattern
    """
    text = text.strip()
    
    # Empty or too long
    if not text or len(text) > 150:
        return False
    
    # Chapter patterns
    chapter_patterns = [
        r'^Chapter \d+',
        r'^CHAPTER \d+',
        r'^Part [IVX]+',
        r'^PART [IVX]+',
        r'^\d+\.\s+[A-Z]',  # "1. Introduction"
    ]
    
    for pattern in chapter_patterns:
        if re.match(pattern, text):
            return True
    
    # All caps and short
    if text.isupper() and len(text) < 80:
        return True
    
    return False


def extract_with_headings(pdf_path):
    """Enhanced extraction with PAGE MARKERS for page-specific queries"""
    import fitz  # PyMuPDF
    import json
    from pathlib import Path
    
    pdf_path = Path(pdf_path)
    base_name = pdf_path.stem
    
    print(f"\n{'='*60}")
    print(f"📄 Extracting with PAGE MARKERS: {pdf_path.name}")
    print(f"{'='*60}")
    
    # Open PDF
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    print(f"📊 Total pages: {total_pages}")
    
    # Storage
    full_text = []
    page_index = {}
    
    # Extract EACH page separately
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        text = text.strip()
        
        if text:
            # ADD PAGE MARKER (critical for page queries!)
            page_marker = f"\n\n{'='*60}\n=== PAGE {page_num + 1} ===\n{'='*60}\n\n"
            full_text.append(page_marker)
            full_text.append(text)
            
            # Index this page
            page_index[str(page_num + 1)] = {  # Store as string for JSON
                'page_number': page_num + 1,
                'char_count': len(text),
                'preview': text[:200].replace('\n', ' ')
            }
            
            print(f"✅ Page {page_num + 1}: {len(text)} chars")
    
    # Save full text WITH page markers
    raw_file = pdf_path.parent / f"{base_name}_RAW_TEXT.txt"
    with open(raw_file, 'w', encoding='utf-8') as f:
        f.write(''.join(full_text))
    
    # Save page index JSON
    index_file = pdf_path.parent / f"{base_name}_PAGE_INDEX.json"
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(page_index, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved:")
    print(f"   📄 {raw_file.name} ({len(full_text)} parts with page markers)")
    print(f"   📋 {index_file.name} ({len(page_index)} pages indexed)")
    
    # VERIFY page markers
    full_content = ''.join(full_text)
    import re
    markers_found = len(re.findall(r'=== PAGE \d+ ===', full_content))
    print(f"   ✅ Verified: {markers_found} page markers in output")
    
    print(f"{'='*60}\n")
    
    doc.close()
    return raw_file, index_file



if __name__ == "__main__":
    default_pdf = r"c:\Users\sumit\rag app\documents\prompt-engineering-for-llms-the-art-and-science-of-building-large-language-modelbased-applications-9781098156152 (1).pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = default_pdf
    
    if os.path.isfile(pdf_path):
        extract_with_headings(pdf_path)
    else:
        print(f"❌ File not found: {pdf_path}")
