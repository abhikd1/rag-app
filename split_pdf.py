from PyPDF2 import PdfReader, PdfWriter
import os

def split_pdf(input_path, output_folder, chunk_size=50):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    for start in range(0, total_pages, chunk_size):
        end = min(start + chunk_size, total_pages)
        writer = PdfWriter()
        
        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])
            
        output_filename = f"part_{start//chunk_size + 1}_{start}_to_{end}.pdf"
        output_path = os.path.join(output_folder, output_filename)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"Created: {output_filename}")

if __name__ == "__main__":
    split_pdf(r"c:\Users\sumit\rag app\documents\rakesh_yadav_7300.pdf", r"c:\Users\sumit\rag app\split_parts")
