
import os
import sys
import glob

# Force UTF-8 for emojis
if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import os
import sys
import glob
import subprocess

# Force UTF-8 for emojis (Simpler approach)
sys.stdout.reconfigure(encoding='utf-8')

def get_all_documents(docs_dir):
    """Find all supported documents and check index status"""
    extensions = ['*.pdf', '*.txt']
    docs = []
    
    for ext in extensions:
        # Exclude generated files
        files = glob.glob(os.path.join(docs_dir, ext))
        for f in files:
            if "_INDEX.txt" in f or "_RAW_TEXT.txt" in f or "STUDY_GUIDE" in f:
                continue
            
            # Check if index exists
            base_name = os.path.splitext(f)[0]
            index_path = base_name + "_INDEX.txt"
            status = "✅ READY" if os.path.exists(index_path) else "🆕 UNINDEXED"
            
            docs.append({
                'path': f,
                'name': os.path.basename(f),
                'status': status,
                'index_path': index_path
            })
    return docs

def generate_index(doc_path):
    """Call Mode A to generate index"""
    print(f"\n⚙️  Generating Index for: {os.path.basename(doc_path)}...")
    print("   (This uses Mode A Extractor)")
    
    try:
        # Run mode_a_extractor.py
        subprocess.run([sys.executable, "mode_a_extractor.py", doc_path], check=True)
        print("✅ Index Generation Complete!")
        return True
    except Exception as e:
        print(f"❌ Error generating index: {e}")
        return False

def print_index_table(file_path):
    """Read and format the index file"""
    if not os.path.exists(file_path):
        print("❌ Index file not found.")
        return

    filename = os.path.basename(file_path).replace("_INDEX.txt", "")
    print(f"\n📚 BOOK INDEX: {filename}")
    print("="*80)
    print(f"{'SECTION / TOPIC':<60} | {'PAGE':<10}")
    print("-" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line or line.startswith("==="): continue
        if line.startswith("📖"):
            # Chapter Headers
            print(f"\n{line:<60} |")
        elif "→" in line:
            # Sub topics with page numbers
            try:
                parts = line.split("(Page")
                topic = parts[0].replace("→", "").strip()
                page = parts[1].replace(")", "").strip() if len(parts) > 1 else ""
                
                # Truncate overly long topics
                if len(topic) > 58: topic = topic[:55] + "..."
                print(f"  {topic:<58} | {page}")
            except:
                print(f"  {line:<58} |")
    
    print("="*80 + "\n")

if __name__ == "__main__":
    docs_dir = os.path.join(os.getcwd(), "documents")
    documents = get_all_documents(docs_dir)
    
    if not documents:
        print("❌ No documents found in 'documents/' folder.")
        sys.exit(1)
        
    print("\n📚 LIBRARY CONTENTS")
    print("="*60)
    for i, doc in enumerate(documents):
        # Format: 1. [READY] book name
        print(f"{i+1}. [{doc['status']}] {doc['name']}")
    print("="*60)
        
    try:
        choice = input("\nSelect a book number: ").strip()
        if not choice.isdigit():
            print("❌ Invalid input.")
            sys.exit(1)
            
        idx = int(choice) - 1
        if 0 <= idx < len(documents):
            selected_doc = documents[idx]
            
            # If not indexed, generate it first
            if selected_doc['status'] == "🆕 UNINDEXED":
                success = generate_index(selected_doc['path'])
                if not success: sys.exit(1)
            
            # Show the table
            print_index_table(selected_doc['index_path'])
            
        else:
            print("❌ Invalid selection.")
    except Exception as e:
        print(f"❌ Error: {e}")
