"""
🚀 RAG Study Assistant - Unified Backend Server
Flask server that powers the all-in-one web interface
"""

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import RAG systems
try:
    from gemini_rag import GeminiRAG
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Gemini not available: {e}")
    GEMINI_AVAILABLE = False

try:
    from groq_rag import GroqRAG
    GROQ_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Groq not available: {e}")
    GROQ_AVAILABLE = False

try:
    from progress_tracker import StudyProgressTracker
    TRACKER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Progress Tracker not available: {e}")
    TRACKER_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for frontend

# Global instances
rag_system = None
tracker = None
conversation_history = []

def initialize_system():
    """Initialize the RAG system and tracker"""
    global rag_system, tracker
    
    print("🚀 Initializing RAG Study Assistant Backend...")
    
    # Initialize tracker
    if TRACKER_AVAILABLE:
        tracker = StudyProgressTracker()
        tracker.start_session()
        print("✅ Progress Tracker initialized")
    
    # Initialize RAG (prefer Gemini)
    if GEMINI_AVAILABLE:
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                rag_system = GeminiRAG(api_key=api_key)
                print("✅ Gemini RAG initialized")
                return "gemini"
        except Exception as e:
            print(f"❌ Gemini init failed: {e}")
    
    if GROQ_AVAILABLE:
        try:
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                rag_system = GroqRAG(api_key=api_key)
                print("✅ Groq RAG initialized")
                return "groq"
            else:
                print("❌ Groq initialization: API KEY NOT FOUND")
        except Exception as e:
            print(f"❌ Groq init failed: {e}")
    
    print("❌ No RAG system available!")
    return None

# Routes

@app.route('/')
def index():
    """Serve the main HTML page"""
    return app.send_static_file('study_master_portal.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    global conversation_history
    
    data = request.json
    message = data.get('message', '')
    use_memory = data.get('use_memory', True)
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    if not rag_system:
        return jsonify({'error': 'RAG system not initialized'}), 500
    
    try:
        # Add to conversation history
        if use_memory:
            conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
        
        # Log to tracker
        if tracker:
            tracker.log_question(message, subject="General Study")
        
        # Get AI response
        response = rag_system.ask_question(message)
        
        # Add AI response to history
        if use_memory:
            conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini' if GEMINI_AVAILABLE else 'groq'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Handle streaming chat (like ChatGPT)"""
    data = request.json
    message = data.get('message', '')
    
    if not message or not rag_system:
        return jsonify({'error': 'Invalid request'}), 400
    
    def generate():
        """Generator for streaming response"""
        try:
            # Get full response
            response = rag_system.ask_question(message)
            
            # Stream it word by word
            words = response.split(' ')
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'chunk': word + ' ', 'done': False})}\n\n"
            
            yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get study progress statistics"""
    if not tracker:
        return jsonify({'error': 'Tracker not available'}), 500
    
    try:
        stats = tracker.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/report', methods=['GET'])
def get_progress_report():
    """Get detailed progress report"""
    if not tracker:
        return jsonify({'error': 'Tracker not available'}), 500
    
    try:
        report = tracker.generate_report()
        return jsonify({'report': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save to documents folder
        documents_dir = Path('documents')
        documents_dir.mkdir(exist_ok=True)
        
        filepath = documents_dir / file.filename
        file.save(filepath)
        
        # Process if PDF
        if filepath.suffix.lower() == '.pdf':
            try:
                from mode_a_extractor import extract_with_headings
                extract_with_headings(str(filepath))
                
                # Log to tracker
                if tracker:
                    tracker.add_document(file.filename, doc_type='pdf')
                
                return jsonify({
                    'success': True,
                    'message': f'PDF processed: {file.filename}',
                    'filename': file.filename,
                    'processed': True
                })
            except Exception as e:
                return jsonify({
                    'success': True,
                    'message': f'File uploaded but processing failed: {str(e)}',
                    'filename': file.filename,
                    'processed': False
                })
        else:
            # Just uploaded, not processed
            if tracker:
                tracker.add_document(file.filename, doc_type='txt')
            
            return jsonify({
                'success': True,
                'message': f'File uploaded: {file.filename}',
                'filename': file.filename,
                'processed': False
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all documents in the documents folder"""
    try:
        documents_dir = Path('documents')
        if not documents_dir.exists():
            return jsonify({'documents': []})
        
        docs = []
        for file in documents_dir.iterdir():
            if file.is_file():
                docs.append({
                    'name': file.name,
                    'size': file.stat().st_size,
                    'type': file.suffix,
                    'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        
        return jsonify({'documents': docs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    return jsonify({'history': conversation_history})

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({'success': True})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'gemini_available': GEMINI_AVAILABLE,
        'groq_available': GROQ_AVAILABLE,
        'tracker_available': TRACKER_AVAILABLE,
        'rag_initialized': rag_system is not None,
        'active_model': 'gemini' if GEMINI_AVAILABLE else 'groq' if GROQ_AVAILABLE else 'none'
    })

if __name__ == '__main__':
    # Initialize system
    model = initialize_system()
    
    if not rag_system:
        print("\n❌ ERROR: No RAG system could be initialized!")
        print("Please set GEMINI_API_KEY or check your setup.\n")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 RAG STUDY ASSISTANT - UNIFIED BACKEND")
    print("="*60)
    print(f"✅ Active Model: {model.upper()}")
    print(f"✅ Progress Tracking: {'Enabled' if tracker else 'Disabled'}")
    print(f"✅ Conversation Memory: Enabled")
    print("\n🌐 Server starting at: http://localhost:5000")
    print("📱 Open this URL in your browser to access the interface")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
