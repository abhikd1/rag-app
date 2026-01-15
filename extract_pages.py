import fitz
import os

pdf_path = r"c:\Users\sumit\rag app\documents\prompt-engineering-for-llms-the-art-and-science-of-building-large-language-modelbased-applications-9781098156152 (1).pdf"
output_path = r"c:\Users\sumit\rag app\documents\prompt_indexing_temp.txt"

doc = fitz.open(pdf_path)
with open(output_path, "w", encoding="utf-8") as f:
    for page_num in range(30):  # Starting with first 30 pages to cover intro/index
        page = doc.load_page(page_num)
        text = page.get_text()
        f.write(f"--- PAGE {page_num + 1} ---\n")
        f.write(text)
        f.write("\n\n")

print(f"Extraction complete. Saved to {output_path}")
