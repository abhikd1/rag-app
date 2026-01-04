"""
Quick setup script to prepare the enterprise system for testing.
Run this before starting the main application.
"""

import os
import sys
import shutil

# Fix encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("🔧 Setting up Enterprise Study System...")

# 1. Create necessary directories
directories = [
    './documents',
    './chroma_db',
    './logs'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"✅ Created directory: {directory}")

# 2. Copy documents from parent directory
parent_docs = r"c:\Users\sumit\rag app\documents"
local_docs = "./documents"

if os.path.exists(parent_docs):
    print(f"\n📂 Copying documents from {parent_docs}...")
    
    # Look for RAW_TEXT files
    for file in os.listdir(parent_docs):
        if "RAW_TEXT" in file or "INDEX" in file:
            src = os.path.join(parent_docs, file)
            dst = os.path.join(local_docs, file)
            
            try:
                shutil.copy2(src, dst)
                print(f"✅ Copied: {file}")
            except Exception as e:
                print(f"⚠️ Could not copy {file}: {e}")

# 3. Check if ChromaDB exists in parent
parent_chroma = r"c:\Users\sumit\rag app\chroma_db"
if os.path.exists(parent_chroma):
    print(f"\n💾 Found existing ChromaDB at {parent_chroma}")
    print("   The system will use this database.")
else:
    print("\n⚠️ No existing ChromaDB found.")
    print("   You'll need to index documents first.")

print("\n✨ Setup complete!")
print("\n🚀 Next step: Run 'python main.py' to start the system")
