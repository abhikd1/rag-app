import fitz
import easyocr
import numpy as np
from PIL import Image
import sys

# Handling Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def read_index():
    reader = easyocr.Reader(['en'])
    doc = fitz.open(r"c:\Users\sumit\rag app\documents\rakesh_yadav_7300.pdf")
    
    # Check the first 15 pages for Index/Contents
    for i in range(15):
        print(f"Reading Page {i} for Index...")
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        results = reader.readtext(np.array(img), detail=0)
        text = " ".join(results)
        print(f"--- PAGE {i} TEXT ---")
        print(text)
        if "CONTENTS" in text.upper() or "INDEX" in text.upper() or "PERCENTAGE" in text.upper():
            print("Found potential Index or Chapter Start!")

if __name__ == "__main__":
    read_index()
