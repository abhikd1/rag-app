import fitz  # PyMuPDF
import easyocr
import numpy as np
from PIL import Image
import os
import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def ocr_pdf(pdf_path, output_txt_path, start_page=0, end_page=None):
    print(f"[INFO] Initializing OCR engine (English)...")
    reader = easyocr.Reader(['en'])
    
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    if end_page is None:
        end_page = total_pages
    
    print(f"[INFO] Starting OCR on {pdf_path}")
    print(f"[INFO] Processing pages {start_page+1} to {min(end_page, total_pages)}")
    
    with open(output_txt_path, "a", encoding="utf-8") as f:
        for page_num in range(start_page, min(end_page, total_pages)):
            print(f"[PROCESS] OCRing Page {page_num + 1}/{total_pages}...", end="\r")
            
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Zoom for better OCR
            
            # Convert pixmap to image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_np = np.array(img)
            
            # OCR
            results = reader.readtext(img_np, detail=0)
            text = "\n".join(results)
            
            f.write(f"\n--- PAGE {page_num + 1} ---\n")
            f.write(text)
            f.write("\n")
            
    print(f"\n[SUCCESS] OCR completed! Text saved to: {output_txt_path}")

if __name__ == "__main__":
    pdf_file = r"c:\Users\sumit\rag app\documents\rakesh_yadav_7300.pdf"
    output_file = r"c:\Users\sumit\rag app\documents\rakesh_yadav_text.txt"
    
    # Just do the first 50 pages for now to show it works
    ocr_pdf(pdf_file, output_file, start_page=0, end_page=50)
