"""
ULTIMATE SERVER - FIXED VERSION (NUCLEAR + FORCED VECTOR)
Forces queries to ONLY search the most recently uploaded document.
Updated to use the FIXED Gemini RAG class.
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
import traceback

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"⚠️  Could not load .env: {e}")

# Import RAG
try:
    from gemini_rag import GeminiRAG
    import gemini_rag, inspect
    print(f"✅ Loaded GeminiRAG from: {inspect.getfile(gemini_rag)}")
    GEMINI_OK = True
except Exception as e:
    print(f"[WARN] Gemini: {e}")
    GEMINI_OK = False

try:
    from groq_rag import GroqRAG
    import groq_rag, inspect
    print(f"✅ Loaded GroqRAG from: {inspect.getfile(groq_rag)}")
    GROQ_OK = True
except Exception as e:
    print(f"[WARN] Groq: {e}")
    GROQ_OK = False

app = Flask(__name__, static_folder='.')
CORS(app)

# Global state
active_models = {}
conversation_memory = []
response_cache = {}
last_uploaded_file = None  # Track most recent upload

def init_models():
    """Initialize RAG systems"""
    global active_models
    
    print("\n" + "="*60)
    print("🚀 Initializing FIXED RAG System...")
    print("="*60)
    
    if GEMINI_OK:
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                active_models['gemini'] = GeminiRAG(api_key=api_key)
                print("✅ Gemini READY")
            else:
                print("❌ Gemini: API KEY NOT FOUND")
        except Exception as e:
            print(f"❌ Gemini initialization: {e}")
    
    if GROQ_OK:
        try:
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                active_models['groq'] = GroqRAG(api_key=groq_key)
                print("✅ Groq READY")
            else:
                print("❌ Groq: API KEY NOT FOUND")
        except Exception as e:
            print(f"❌ Groq initialization: {e}")
    
    print("="*60 + "\n")
    return len(active_models) > 0


def delete_chroma_db():
    """Delete entire ChromaDB to start fresh"""
    chroma_path = Path('chroma_db')
    if chroma_path.exists():
        try:
            shutil.rmtree(chroma_path)
            print("🗑️ Old ChromaDB deleted")
            return True
        except Exception as e:
            print(f"❌ Could not delete ChromaDB: {e}")
            return False
    return True


def reload_rag_with_only_new_file(filename):
    """
    NUCLEAR OPTION: Delete old DB, reload with ONLY the new file
    """
    global active_models, last_uploaded_file
    
    print("\n" + "="*70)
    print("🔥 NUCLEAR RELOAD: DELETING OLD DB & INDEXING ONLY NEW FILE")
    print("="*70)
    
    # Step 1: Delete old ChromaDB
    delete_chroma_db()
    
    # Step 2: Reload RAG systems (will create new empty DB)
    if 'gemini' in active_models:
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            active_models['gemini'] = GeminiRAG(api_key=api_key, persist_directory="./chroma_db")
            print(f"✅ Gemini reloaded with NEW empty DB")
    
    if 'groq' in active_models:
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            active_models['groq'] = GroqRAG(api_key=groq_key, persist_directory="./chroma_db")
            print(f"✅ Groq reloaded with NEW empty DB")
    
    last_uploaded_file = filename
    
    print(f"✅ ONLY FILE IN DATABASE: {filename}")
    print("="*70 + "\n")


@app.route('/')
def home():
    """Serve the ultimate UI"""
    return send_from_directory('.', 'ultimate_interface.html')


@app.route('/api/upload', methods=['POST'])
def upload():
    """Handle file upload and load into RAG"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Save file
        docs_dir = Path('documents')
        docs_dir.mkdir(exist_ok=True)
        filepath = docs_dir / file.filename
        file.save(str(filepath))
        
        print(f"\n{'='*60}")
        print(f"📄 UPLOADED & PROCESSING: {file.filename}")
        print(f"{'='*60}")
        
        # Extract content first (to ensure RAW_TEXT exists)
        if filepath.suffix.lower() == '.pdf':
            from mode_a_extractor import extract_with_headings
            extract_with_headings(str(filepath))
            
            # Load into RAG models
            for name, model in active_models.items():
                print(f"🔄 Loading {file.filename} into {name} model...")
                model.load_specific_file(file.filename)
            
            global last_uploaded_file
            last_uploaded_file = file.filename
            
            return jsonify({
                'success': True,
                'status': 'success',
                'file': file.filename,
                'message': f'✅ {file.filename} uploaded and indexed!'
            })
        else:
            return jsonify({'error': 'Only PDF files supported for RAG'}), 400
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_existing():
    """Re-analyze an already uploaded PDF"""
    global last_uploaded_file
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
            
        docs_dir = Path('documents')
        filepath = docs_dir / filename
        
        if not filepath.exists():
            return jsonify({'error': f'File {filename} not found on server'}), 404
            
        # Ensure extraction has happened
        from mode_a_extractor import extract_with_headings
        extract_with_headings(str(filepath))
        
        # Load into RAG models
        for name, model in active_models.items():
            print(f"🔄 Re-analyzing {filename} in {name} model...")
            model.load_specific_file(filename)
            
        last_uploaded_file = filename
        
        return jsonify({
            'success': True,
            'status': 'success',
            'filename': filename,
            'message': f'✅ {filename} analyzed successfully!'
        })
    except Exception as e:
        print(f"❌ Analyze error: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/api/index', methods=['GET'])
def get_index():
    """Get complete hierarchical document index"""
    global last_uploaded_file, active_models
    try:
        current_file = last_uploaded_file
        if not current_file:
            model = active_models.get('gemini') or active_models.get('groq')
            if model: current_file = model.current_file
            
        if not current_file:
            return jsonify({'success': False, 'error': 'No document loaded'}), 400
        
        # Use the NEW hierarchical index generator
        from index_generator_fixed import generate_hierarchical_index
        
        # Call it with current file
        topic_table = generate_hierarchical_index(current_file)
        
        return jsonify({
            'success': True,
            'index': topic_table
        })
    except Exception as e:
        print(f"❌ Error generating index: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/page-summary', methods=['GET'])
def get_page_summary():
    """Get page-by-page summary table"""
    global active_models
    try:
        # Prioritize Gemini
        model = active_models.get('gemini')
        if not model and 'groq' in active_models:
            model = active_models['groq']
            
        if model:
            summary_table = model.get_page_summary_table()
            return jsonify({
                'success': True,
                'summary': summary_table
            })
        return jsonify({'success': False, 'error': 'No active model found'}), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/page-raw', methods=['GET'])
def get_page_raw():
    """Get raw text content for a specific page"""
    global active_models
    try:
        page_num = request.args.get('page', type=int)
        if not page_num:
            return jsonify({'success': False, 'error': 'Page number required'}), 400
            
        model = active_models.get('gemini') or active_models.get('groq')
        if not model:
            return jsonify({'success': False, 'error': 'No document loaded'}), 400
            
        content = model.get_page_content(page_num)
        if not content:
            return jsonify({
                'success': True, 
                'content': '❌ Page appears empty or not found in the raw text file.'
            })
            
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with file-specific context"""
    global last_uploaded_file
    
    data = request.json
    question = data.get('message', '')
    
    if not question:
        return jsonify({'error': 'No message'}), 400
    
    # PREFER GROQ (10x higher quota, blazing fast!) if available
    model = data.get('model', 'groq')  # Changed default from 'gemini' to 'groq'
    
    # Get RAG model with intelligent fallback
    rag = active_models.get(model)
    if not rag:
        # Fallback priority: groq > gemini
        if 'groq' in active_models:
            model = 'groq'
            rag = active_models['groq']
        elif 'gemini' in active_models:
            model = 'gemini'
            rag = active_models['gemini']
        else:
            model = next(iter(active_models.keys())) if active_models else None
            rag = active_models.get(model) if model else None
        
    if not rag:
        return jsonify({'error': f'No models available'}), 500

    
    try:
        # Enhance question with file context if available
        if last_uploaded_file:
            enhanced_question = f"""
Question about the file "{last_uploaded_file}" that was just uploaded:

{question}

Important: Answer ONLY based on the content from {last_uploaded_file}. 
Ignore any other documents. This is the ONLY document that should be searched.
"""
            print(f"\n[QUERY] Enhanced question for: {last_uploaded_file}")
        else:
            enhanced_question = question
            print(f"\n[QUERY] Regular question")
        
        # Consistent interface
        if hasattr(rag, 'ask_question'):
            response = rag.ask_question(enhanced_question)
        elif hasattr(rag, 'ask'):
            response = rag.ask(enhanced_question)
        else:
            response = "❌ Model interface error"
        
        return jsonify({
            'response': response,
            'cached': False,
            'model': model,
            'queried_file': last_uploaded_file,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Chat error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    return jsonify({
        'models_available': list(active_models.keys()),
        'last_uploaded_file': last_uploaded_file,
        'chroma_db_exists': Path('chroma_db').exists()
    })


if __name__ == '__main__':
    if not init_models():
        print("❌ No models available")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 FIXED SERVER STARTING")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("\n💡 This version DELETES old DB on each upload!")
    print("   Only the most recent file will be searchable.")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
