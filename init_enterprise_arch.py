import os
import sys

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# The Enterprise Architecture Definition
structure = [
    # CORE: The Heart of the System
    r"src\core\config",             # Settings management
    r"src\core\logging",            # Advanced logging
    r"src\core\security",           # Input validation/Sanitization
    
    # DOMAIN: Business Logic (The Modes)
    r"src\domain\orchestrator",     # The Router logic
    r"src\domain\study_modes\base", # Abstract Base Classes (SOLID)
    r"src\domain\study_modes\recall",      # Mode A, E
    r"src\domain\study_modes\explainer",   # Mode B
    r"src\domain\study_modes\synthesizer", # Mode C
    r"src\domain\study_modes\tutor",       # Mode D
    
    # INFRASTRUCTURE: External Connections
    r"src\infrastructure\database\vector_store", # ChromaDB wrapper
    r"src\infrastructure\llm\client",            # Ollama wrapper
    r"src\infrastructure\filesystem\pdf",        # PDF Processing
    r"src\infrastructure\filesystem\text",       # Text Processing
    
    # INTERFACE: How users interact
    r"src\interface\cli",  # Terminal UI
    r"src\interface\api",  # Future Web API (FastAPI ready)
    
    # TESTING: Quality Assurance
    r"tests\unit",
    r"tests\integration",
    
    # DOCS
    r"documentation\architecture",
    r"documentation\user_guides"
]

base_path = r"c:\Users\sumit\rag app\enterprise_system"

print(f"🚀 Initializing Enterprise Architecture at: {base_path}...")

for folder in structure:
    full_path = os.path.join(base_path, folder)
    os.makedirs(full_path, exist_ok=True)
    # Create __init__.py to make them packages
    with open(os.path.join(full_path, "__init__.py"), 'w') as f:
        pass
    print(f"✅ Created Module: {folder}")

print("\n✨ Architecture Generation Complete. Ready for 100k lines of code.")
