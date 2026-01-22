"""
System Verification Script
Checks all components of the Ultimate RAG System
"""

import os
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_file(filepath, description):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {str(e)}")
        return False

print("="*60)
print("🔍 ULTIMATE RAG SYSTEM - VERIFICATION")
print("="*60)

# Check core files
print("\n📁 CORE FILES:")
core_files = [
    ("ultimate_server.py", "Ultimate Backend Server"),
    ("ultimate_interface.html", "Ultimate UI"),
    ("gemini_rag.py", "Gemini RAG"),
    ("groq_rag.py", "Groq RAG"),
    ("main.py", "Ollama RAG"),
    ("progress_tracker.py", "Progress Tracker"),
    ("query_router.py", "Query Router"),
]

core_ok = all(check_file(f, d) for f, d in core_files)

# Check mode handlers
print("\n🎓 STUDY MODE HANDLERS:")
mode_files = [
    ("mode_a_handler.py", "Mode A - Exact Recall"),
    ("mode_b_handler.py", "Mode B - Explanation"),
    ("mode_c_handler.py", "Mode C - Linking"),
    ("mode_d_handler.py", "Mode D - Revision"),
    ("mode_e_handler.py", "Mode E - Testing"),
]

modes_ok = all(check_file(f, d) for f, d in mode_files)

# Check utilities
print("\n🛠️ UTILITIES:")
util_files = [
    ("process_transcript_groq.py", "Transcript Processor"),
    ("mode_a_extractor.py", "PDF Extractor"),
]

utils_ok = all(check_file(f, d) for f, d in util_files)

# Check HTML interfaces
print("\n🌐 HTML INTERFACES:")
html_files = [
    ("ultimate_interface.html", "Ultimate Interface"),
    ("study_master_portal.html", "Study Portal"),
    ("web_ui.html", "Web UI"),
    ("upload_documents.html", "Upload Interface"),
    ("progress_dashboard.html", "Progress Dashboard"),
]

html_ok = all(check_file(f, d) for f, d in html_files)

# Check Python packages
print("\n📦 PYTHON PACKAGES:")
packages = [
    ("flask", "Flask Web Framework"),
    ("flask_cors", "Flask CORS"),
    ("google.generativeai", "Gemini AI"),
    ("groq", "Groq AI"),
    ("langchain", "LangChain"),
    ("chromadb", "ChromaDB"),
    ("sentence_transformers", "Embeddings"),
]

packages_ok = all(check_import(p, d) for p, d in packages)

# Check directories
print("\n📂 DIRECTORIES:")
dirs = [
    ("documents", "Documents folder"),
    ("chroma_db", "Vector database"),
]

dirs_ok = all(check_file(d, desc) for d, desc in dirs)

# Check environment
print("\n🔑 ENVIRONMENT:")
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print(f"✅ GEMINI_API_KEY is set ({gemini_key[:10]}...)")
else:
    print("⚠️ GEMINI_API_KEY not set (Gemini won't work)")

# Summary
print("\n" + "="*60)
print("📊 VERIFICATION SUMMARY")
print("="*60)

total_checks = 0
passed_checks = 0

checks = [
    (core_ok, "Core Files"),
    (modes_ok, "Study Modes"),
    (utils_ok, "Utilities"),
    (html_ok, "HTML Interfaces"),
    (packages_ok, "Python Packages"),
    (dirs_ok, "Directories"),
]

for status, name in checks:
    total_checks += 1
    if status:
        passed_checks += 1
        print(f"✅ {name}: PASS")
    else:
        print(f"❌ {name}: FAIL")

print("\n" + "="*60)
print(f"RESULT: {passed_checks}/{total_checks} checks passed")

if passed_checks == total_checks:
    print("🎉 ALL SYSTEMS GO! Ready to launch!")
    print("\n🚀 Run: python ultimate_server.py")
    print("🌐 Then open: http://localhost:5000")
else:
    print("⚠️ Some components missing. Check errors above.")
    if not packages_ok:
        print("\n💡 Install missing packages:")
        print("   pip install flask flask-cors google-generativeai groq langchain chromadb sentence-transformers")

print("="*60)
