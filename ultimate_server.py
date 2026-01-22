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

# Import RAG
try:
    from gemini_rag import GeminiRAG
    GEMINI_OK = True
except Exception as e:
    print(f"[WARN] Gemini: {e}")
    GEMINI_OK = False

try:
    from groq_rag import GroqRAG
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
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No filename'}), 400
    
    try:
        # Save file
        docs_dir = Path('documents')
        docs_dir.mkdir(exist_ok=True)
        filepath = docs_dir / file.filename
        file.save(filepath)
        
        print(f"\n{'='*60}")
        print(f"📄 UPLOADED: {file.filename}")
        print(f"{'='*60}")
        
        # Process PDF
        if filepath.suffix.lower() == '.pdf':
            try:
                from mode_a_extractor import extract_with_headings
                
                print(f"📊 Extracting with page markers...")
                extract_with_headings(str(filepath))
                print(f"✅ Extraction complete")
                
                # RELOAD RAG WITH ONLY THIS FILE
                print(f"\n{'='*60}")
                print(f"🔄 LOADING INTO RAG...")
                print(f"{'='*60}")
                
                # Clear cache
                global response_cache
                response_cache.clear()
                print("✅ Cache cleared")
                
                # Reload Gemini with only this file
                if 'gemini' in active_models:
                    success = active_models['gemini'].load_specific_file(file.filename)
                    if not success:
                        return jsonify({
                            'success': False,
                            'error': 'Failed to load into RAG'
                        }), 500
                
                # Reload Groq with only this file (if you have groq_rag.py updated similarly)
                if 'groq' in active_models:
                    try:
                        active_models['groq'].load_specific_file(file.filename)
                    except:
                        pass  # Groq might not have this method yet
                
                print(f"{'='*60}\n")
                
                # Initialize tracker if it exists
                try:
                    from progress_tracker import StudyProgressTracker
                    tracker = StudyProgressTracker()
                    tracker.add_document(file.filename, 'pdf')
                except:
                    pass
                
                return jsonify({
                    'success': True,
                    'processed': True,
                    'file': file.filename,
                    'message': f'✅ {file.filename} indexed! Now the ONLY searchable file.',
                    'vector_reload_complete': True
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        else:
            # Non-PDF file
            return jsonify({
                'success': True,
                'processed': False,
                'file': file.filename,
                'message': 'Only PDF files are processed'
            })
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
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


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with file-specific context"""
    global last_uploaded_file
    
    data = request.json
    question = data.get('message', '')
    
    if not question:
        return jsonify({'error': 'No message'}), 400
    # PREER GROQ (no quota limits!) if available, otherwise use requested model
    model = data.get('model', 'gemini')
    
    # Get RAG model
    rag = active_models.get(model)
    if not rag:
        # Final fallback
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
