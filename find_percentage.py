import fitz
import easyocr
import numpy as np
from PIL import Image
import sys

# Handling Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def find_chapter_ocr(pdf_path, search_term="PERCENTAGE"):
    reader = easyocr.Reader(['en'])
    doc = fitz.open(pdf_path)
    
    # Sample pages every 50 to get a rough idea, then narrow down
    print(f"Searching for {search_term} in {pdf_path}...")
    
    found_page = -1
    for p_num in range(0, len(doc), 50):
        print(f"Sampling Page {p_num}...")
        page = doc.load_page(p_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_np = np.array(img)
        
        results = reader.readtext(img_np, detail=0)
        text = " ".join(results).upper()
        
        if search_term in text:
            print(f"Found {search_term} near page {p_num}!")
            found_page = p_num
            break
            
    if found_page != -1:
        # Narrow down: search 50 pages backwards
        for p_num in range(max(0, found_page - 50), found_page + 1):
            print(f"Checking Page {p_num}...")
            page = doc.load_page(p_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_np = np.array(img)
            results = reader.readtext(img_np, detail=0)
            text = " ".join(results).upper()
            if search_term in text:
                print(f"Exact Start Found at Page {p_num}")
                # Now OCR this exact page fully and the next few
                for i in range(p_num, p_num + 3):
                    print(f"--- CONTENT OF PAGE {i} ---")
                    pix = doc.load_page(i).get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    results = reader.readtext(np.array(img), detail=0)
                    print("\n".join(results))
                return

if __name__ == "__main__":
    find_chapter_ocr(r"c:\Users\sumit\rag app\documents\rakesh_yadav_7300.pdf")
