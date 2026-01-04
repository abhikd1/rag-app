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


def extract_with_headings(pdf_path, output_dir=None):
    """
    Extract PDF with heading detection and create:
    1. RAW_TEXT.txt - Pure page-by-page text
    2. INDEX.txt - Structured index with headings
    """
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    # Setup output directory
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    raw_text_path = os.path.join(output_dir, f"{base_name}_RAW_TEXT.txt")
    index_path = os.path.join(output_dir, f"{base_name}_INDEX.txt")
    
    print(f"📚 Processing: {os.path.basename(pdf_path)}")
    print(f"📄 Total Pages: {total_pages}")
    print(f"💾 Output Directory: {output_dir}")
    print("=" * 80)
    
    # Storage
    headings = []  # (heading_text, page_num, line_num)
    current_chapter = None
    
    # Extract raw text with heading detection
    with open(raw_text_path, "w", encoding="utf-8") as raw_file:
        raw_file.write("=" * 80 + "\n")
        raw_file.write(f"📖 LOSSLESS BOOK EXTRACTION — MODE A COMPATIBLE\n")
        raw_file.write(f"Source: {os.path.basename(pdf_path)}\n")
        raw_file.write(f"Total Pages: {total_pages}\n")
        raw_file.write("=" * 80 + "\n\n")
        
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Write page header
            raw_file.write(f"\n{'='*80}\n")
            raw_file.write(f"📄 PAGE {page_num + 1}\n")
            raw_file.write(f"{'='*80}\n\n")
            
            # Process text line by line for heading detection
            if text.strip():
                lines = text.split('\n')
                for line_num, line in enumerate(lines, 1):
                    # Check if heading
                    if detect_heading(line):
                        headings.append((line.strip(), page_num + 1, line_num))
                        
                        # Track chapters
                        if re.match(r'^(Chapter|CHAPTER|Part|PART)', line):
                            current_chapter = line.strip()
                
                # Write full text
                raw_file.write(text)
            else:
                raw_file.write("⚠️ [This page appears to be blank or image-only]\n")
            
            raw_file.write("\n\n")
            
            # Progress
            if (page_num + 1) % 10 == 0:
                print(f"✅ Processed {page_num + 1}/{total_pages} pages...")
    
    # Create structured index
    with open(index_path, "w", encoding="utf-8") as idx_file:
        idx_file.write("=" * 80 + "\n")
        idx_file.write(f"📑 BOOK INDEX — HEADINGS & PAGE MAPPING\n")
        idx_file.write(f"Source: {os.path.basename(pdf_path)}\n")
        idx_file.write(f"Total Headings Detected: {len(headings)}\n")
        idx_file.write("=" * 80 + "\n\n")
        
        current_chapter_name = None
        
        for heading, page, line in headings:
            # Check if new chapter
            if re.match(r'^(Chapter|CHAPTER|Part|PART)', heading):
                idx_file.write(f"\n{'='*80}\n")
                idx_file.write(f"📖 {heading}\n")
                idx_file.write(f"{'='*80}\n")
                current_chapter_name = heading
            else:
                # Sub-heading
                idx_file.write(f"  → {heading} (Page {page})\n")
    
    print(f"\n🎉 Extraction Complete!")
    print(f"📄 Raw Text: {raw_text_path}")
    print(f"📑 Index: {index_path}")
    print(f"\n💡 Next Step: Type 'reload' in your RAG app to index these files.")
    
    return raw_text_path, index_path


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
