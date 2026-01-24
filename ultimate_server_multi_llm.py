"""
🚀 ULTIMATE SERVER WITH MULTI-LLM ROUTER
Unlimited free requests by rotating between 6 LLM providers!
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
import traceback
import re

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except:
    print("⚠️  Using system environment variables")

# Import the multi-LLM router
from multi_llm_router import get_llm_router, ask_llm

app = Flask(__name__, static_folder='.')
CORS(app)

# Global state
llm_router = None
last_uploaded_file = None

def init_llm():
    """Initialize the multi-LLM router"""
    global llm_router
    llm_router = get_llm_router()
    return llm_router is not None

def get_page_content(pdf_name, page_num):
    """Extract exact page content from RAW_TEXT file"""
    basename = Path(pdf_name).stem
    raw_file = Path(f"documents/{basename}_RAW_TEXT.txt")
    
    if not raw_file.exists():
        return None
    
    content = raw_file.read_text(encoding='utf-8')
    pattern = rf"=== PAGE {page_num} ==="
    
    parts = re.split(pattern, content)
    if len(parts) < 2:
        return None
    
    # Get content until next page
    next_pattern = rf"=== PAGE {page_num + 1} ==="
    page_content = parts[1].split(next_pattern)[0] if next_pattern in parts[1] else parts[1]
    
    # Clean big separator bars
    page_content = re.sub(r'^={15,}.*$', '', page_content, flags=re.MULTILINE)
    page_content = page_content.strip()
    
    return page_content if len(page_content) > 10 else None

@app.route('/')
def home():
    """Serve the ultimate UI"""
    return send_from_directory('.', 'ultimate_interface.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    """Handle file upload"""
    global last_uploaded_file
    
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
        print(f"📄 UPLOADED: {file.filename}")
        print(f"{'='*60}")
        
        # Extract content
        if filepath.suffix.lower() == '.pdf':
            from mode_a_extractor import extract_with_headings
            extract_with_headings(str(filepath))
            
            last_uploaded_file = file.filename
            
            return jsonify({
                'success': True,
                'status': 'success',
                'file': file.filename,
                'message': f'✅ {file.filename} uploaded and indexed!'
            })
        else:
            return jsonify({'error': 'Only PDF files supported'}), 400
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with multi-LLM router (unlimited free requests!)"""
    global last_uploaded_file
    
    data = request.json
    question = data.get('message', '')
    
    if not question:
        return jsonify({'error': 'No message'}), 400
    
    if not last_uploaded_file:
        return jsonify({'error': 'No document loaded. Upload a PDF first.'}), 400
    
    try:
        # Check if asking about a specific page
        page_match = re.search(r'\bpage\s+(\d+)', question.lower())
        
        if page_match:
            page_num = int(page_match.group(1))
            page_content = get_page_content(last_uploaded_file, page_num)
            
            if not page_content:
                return jsonify({
                    'response': f"❌ Page {page_num} has no readable content.",
                    'model': 'system',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Check if RAW mode
            if any(kw in question.lower() for kw in ['raw', 'exact', 'verbatim']):
                # Return raw content formatted nicely
                formatted = f"# 📖 PAGE {page_num} - RAW CONTENT\n\n{page_content}\n\n*Note: Verbatim text from Page {page_num}*"
                return jsonify({
                    'response': formatted,
                    'model': 'raw',
                    'timestamp': datetime.now().isoformat()
                })
            
            # EXPLAIN mode - use LLM
            prompt = f"""📄 Analyzing PAGE {page_num} from {last_uploaded_file}

CRITICAL RULES:
1. Use ONLY the text below - NO external knowledge
2. If content is unclear/limited, say so clearly
3. Quote exact text where possible
4. Do NOT invent or add textbook knowledge

PAGE CONTENT:
{page_content}

QUESTION: {question}

Answer ONLY based on the page above with rich formatting and emojis:"""
        
        else:
            # General question - would need vector search (not implemented in this simple version)
            prompt = f"""📚 Document Analysis: {last_uploaded_file}

Answer based on document content only.

QUESTION: {question}"""
        
        # Use multi-LLM router (automatically tries all providers)
        response = ask_llm(prompt, temperature=0.1)
        
        return jsonify({
            'response': response,
            'cached': False,
            'model': 'multi-llm',
            'queried_file': last_uploaded_file,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"❌ Chat error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/index', methods=['GET'])
def get_index():
    """Get complete hierarchical document index"""
    global last_uploaded_file
    
    try:
        if not last_uploaded_file:
            return jsonify({'success': False, 'error': 'No document loaded'}), 400
        
        from index_generator_fixed import generate_hierarchical_index
        topic_table = generate_hierarchical_index(last_uploaded_file)
        
        return jsonify({
            'success': True,
            'index': topic_table
        })
    except Exception as e:
        print(f"❌ Error generating index: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/page-raw', methods=['GET'])
def get_page_raw():
    """Get raw text content for a specific page"""
    global last_uploaded_file
    
    try:
        page_num = request.args.get('page', type=int)
        if not page_num:
            return jsonify({'success': False, 'error': 'Page number required'}), 400
        
        if not last_uploaded_file:
            return jsonify({'success': False, 'error': 'No document loaded'}), 400
        
        content = get_page_content(last_uploaded_file, page_num)
        if not content:
            return jsonify({
                'success': True,
                'content': f'❌ Page {page_num} appears empty or not found.'
            })
        
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get system status"""
    global llm_router
    
    stats = llm_router.get_stats() if llm_router else {}
    
    return jsonify({
        'last_uploaded_file': last_uploaded_file,
        'llm_providers': stats.get('active_providers', []),
        'total_requests': stats.get('total_requests', 0),
        'request_count': stats.get('request_count', {})
    })

if __name__ == '__main__':
    if not init_llm():
        print("❌ No LLM providers available. Add API keys to .env file.")
        print("\nGet free API keys from:")
        print("  - https://console.groq.com/keys")
        print("  - https://openrouter.ai/keys")
        print("  - https://together.ai/app")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 ULTIMATE SERVER WITH MULTI-LLM ROUTER")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("\n💡 Features:")
    print("   ✅ Unlimited free requests (6 LLM providers)")
    print("   ✅ Automatic failover & load balancing")
    print("   ✅ Page-specific RAG queries")
    print("   ✅ RAW mode for exact text")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
