"""
🚀 RAG Study Assistant - Web Interface
Beautiful Gradio UI for your Multi-Modal RAG System
"""

import gradio as gr
import os
import sys
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
    from main import FreeDocumentQA
    OLLAMA_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Ollama not available: {e}")
    OLLAMA_AVAILABLE = False


class RAGWebInterface:
    """Enhanced web interface for RAG system"""
    
    def __init__(self):
        self.current_model = "gemini"
        self.rag_gemini = None
        self.rag_groq = None
        self.rag_ollama = None
        
        # Initialize available models
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize available RAG models"""
        if GEMINI_AVAILABLE:
            try:
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key:
                    self.rag_gemini = GeminiRAG(api_key=api_key)
                    print("✅ Gemini initialized")
            except Exception as e:
                print(f"❌ Gemini init failed: {e}")
        
        if GROQ_AVAILABLE:
            try:
                # Use environment variable for API key
                api_key = os.getenv('GROQ_API_KEY')
                if api_key:
                    self.rag_groq = GroqRAG(api_key=api_key)
                    print("✅ Groq initialized")
                else:
                    print("❌ Groq initialization: API KEY NOT FOUND")
            except Exception as e:
                print(f"❌ Groq init failed: {e}")
        
        if OLLAMA_AVAILABLE:
            try:
                self.rag_ollama = FreeDocumentQA()
                print("✅ Ollama initialized")
            except Exception as e:
                print(f"❌ Ollama init failed: {e}")
    
    def chat(self, message, history, model_choice):
        """Main chat function"""
        if not message.strip():
            return history, ""
        
        # Add user message to history
        history = history or []
        history.append([message, None])
        
        try:
            # Select model
            if model_choice == "Gemini 2.5 Flash (Fast & Free)" and self.rag_gemini:
                response = self.rag_gemini.ask_question(message)
            elif model_choice == "Groq Llama 3.3 70B (Fastest)" and self.rag_groq:
                # Groq returns by printing, we need to capture it
                import io
                from contextlib import redirect_stdout
                
                f = io.StringIO()
                with redirect_stdout(f):
                    self.rag_groq.ask(message)
                response = f.getvalue()
                
                # If nothing captured, read from last_answer.md
                if not response.strip():
                    try:
                        with open("last_answer.md", "r", encoding="utf-8") as file:
                            response = file.read()
                    except:
                        response = "✅ Answer saved to last_answer.md"
            elif model_choice == "Ollama (Local)" and self.rag_ollama:
                response = self.rag_ollama.ask_question(message)
            else:
                response = f"❌ {model_choice} is not available. Please check your setup."
            
            # Update history with response
            history[-1][1] = response
            
        except Exception as e:
            history[-1][1] = f"❌ Error: {str(e)}"
        
        return history, ""
    
    def get_available_models(self):
        """Get list of available models"""
        models = []
        if self.rag_gemini:
            models.append("Gemini 2.5 Flash (Fast & Free)")
        if self.rag_groq:
            models.append("Groq Llama 3.3 70B (Fastest)")
        if self.rag_ollama:
            models.append("Ollama (Local)")
        
        return models if models else ["No models available"]
    
    def upload_document(self, file):
        """Handle document upload"""
        if file is None:
            return "❌ No file selected"
        
        try:
            # Copy file to documents folder
            import shutil
            dest = Path("documents") / Path(file.name).name
            shutil.copy(file.name, dest)
            
            # Process if PDF
            if dest.suffix.lower() == '.pdf':
                from mode_a_extractor import extract_with_headings
                extract_with_headings(str(dest))
                return f"✅ PDF processed: {dest.name}\n📄 Created RAW_TEXT and INDEX files"
            else:
                return f"✅ File uploaded: {dest.name}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def reload_documents(self):
        """Reload all documents into vector store"""
        try:
            if self.rag_ollama:
                self.rag_ollama.load_documents_from_folder()
                return "✅ Documents reloaded successfully!"
            else:
                return "❌ Ollama not available for document loading"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def process_transcript(self, start_min, end_min):
        """Process transcript segment"""
        try:
            # Update process_transcript_groq.py with new range
            # For now, just return instruction
            return f"📝 To process {start_min}-{end_min} minutes:\n\n1. Open process_transcript_groq.py\n2. Change time range to {start_min}:00 - {end_min}:00\n3. Run: python process_transcript_groq.py"
        except Exception as e:
            return f"❌ Error: {str(e)}"


def create_interface():
    """Create the Gradio interface"""
    
    rag_interface = RAGWebInterface()
    available_models = rag_interface.get_available_models()
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    .chatbot {
        height: 600px;
    }
    .message {
        font-size: 16px;
        line-height: 1.6;
    }
    """
    
    with gr.Blocks(css=custom_css, title="RAG Study Assistant", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🚀 RAG Study Assistant
        ### Multi-Modal AI-Powered Learning System
        Ask questions about your documents, process transcripts, and study smarter!
        """)
        
        with gr.Tabs():
            # ===== TAB 1: CHAT =====
            with gr.Tab("💬 Chat"):
                with gr.Row():
                    with gr.Column(scale=4):
                        chatbot = gr.Chatbot(
                            label="AI Assistant",
                            height=500,
                            show_label=True,
                            avatar_images=(None, "🤖")
                        )
                        
                        with gr.Row():
                            msg = gr.Textbox(
                                label="Your Question",
                                placeholder="Ask anything about your documents... (e.g., 'Explain ACID properties', 'page 50', 'test me on Chapter 3')",
                                lines=2,
                                scale=4
                            )
                            submit = gr.Button("Send 🚀", variant="primary", scale=1)
                        
                        gr.Examples(
                            examples=[
                                "What is normalization?",
                                "Show me page 50",
                                "I don't understand foreign keys",
                                "Test me on Chapter 3",
                                "Revise chapter 2",
                            ],
                            inputs=msg,
                            label="💡 Example Questions"
                        )
                    
                    with gr.Column(scale=1):
                        model_selector = gr.Radio(
                            choices=available_models,
                            value=available_models[0] if available_models else None,
                            label="🧠 Select Model",
                            info="Choose your AI model"
                        )
                        
                        gr.Markdown("""
                        ### 📊 Model Info
                        
                        **Gemini 2.5 Flash**
                        - ⚡ Fast (5-10s)
                        - 🆓 Free
                        - ⭐ Excellent quality
                        
                        **Groq Llama 3.3**
                        - ⚡⚡⚡ Fastest (2-5s)
                        - 🆓 Free
                        - ⭐⭐⭐⭐⭐ Best quality
                        
                        **Ollama (Local)**
                        - 🐌 Slower (30-60s)
                        - 🆓 Free
                        - 🔒 Offline
                        """)
                        
                        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
                
                # Chat interactions
                submit.click(
                    rag_interface.chat,
                    inputs=[msg, chatbot, model_selector],
                    outputs=[chatbot, msg]
                )
                
                msg.submit(
                    rag_interface.chat,
                    inputs=[msg, chatbot, model_selector],
                    outputs=[chatbot, msg]
                )
                
                clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])
            
            # ===== TAB 2: DOCUMENT MANAGEMENT =====
            with gr.Tab("📚 Documents"):
                gr.Markdown("### Upload and manage your study materials")
                
                with gr.Row():
                    with gr.Column():
                        file_upload = gr.File(
                            label="📄 Upload Document",
                            file_types=[".pdf", ".txt"],
                            type="filepath"
                        )
                        upload_btn = gr.Button("Upload & Process", variant="primary")
                        upload_status = gr.Textbox(label="Status", lines=3)
                    
                    with gr.Column():
                        reload_btn = gr.Button("🔄 Reload All Documents", variant="secondary")
                        reload_status = gr.Textbox(label="Reload Status", lines=3)
                        
                        gr.Markdown("""
                        ### 📖 Current Documents
                        Check your `documents/` folder for:
                        - PDF files
                        - TXT files
                        - Generated INDEX files
                        """)
                
                upload_btn.click(
                    rag_interface.upload_document,
                    inputs=file_upload,
                    outputs=upload_status
                )
                
                reload_btn.click(
                    rag_interface.reload_documents,
                    outputs=reload_status
                )
            
            # ===== TAB 3: TRANSCRIPT PROCESSOR =====
            with gr.Tab("🎙️ Transcript Processor"):
                gr.Markdown("### Process YouTube transcripts with lossless extraction")
                
                with gr.Row():
                    start_min = gr.Number(label="Start (minutes)", value=0, precision=0)
                    end_min = gr.Number(label="End (minutes)", value=10, precision=0)
                
                process_btn = gr.Button("Process Transcript Segment", variant="primary")
                transcript_output = gr.Textbox(label="Instructions", lines=5)
                
                gr.Markdown("""
                ### 📝 How to use:
                1. Enter time range (e.g., 0-10, 10-20, 20-30)
                2. Click "Process Transcript Segment"
                3. Follow the instructions to run the script
                
                **Note:** Transcript processing uses Groq for lossless extraction
                """)
                
                process_btn.click(
                    rag_interface.process_transcript,
                    inputs=[start_min, end_min],
                    outputs=transcript_output
                )
            
            # ===== TAB 4: STUDY MODES =====
            with gr.Tab("🎓 Study Modes"):
                gr.Markdown("""
                ### 5 Specialized Study Modes
                
                Use these keywords in your questions to activate different modes:
                
                #### 📄 MODE A: Exact Recall
                - **Keywords:** "page X", "exact text", "word for word", "verbatim"
                - **Example:** "Show me page 50"
                - **Output:** Exact text from the page (lossless)
                
                #### 🧩 MODE B: Stuck-Point Explanation
                - **Keywords:** "I don't understand", "explain this part", "confused about"
                - **Example:** "I don't understand foreign keys"
                - **Output:** Surgical explanation of just that concept
                
                #### 🔗 MODE C: Concept Linking
                - **Keywords:** "relate to", "connect this", "relationship between"
                - **Example:** "How does ACID relate to transactions?"
                - **Output:** Shows connections across the book
                
                #### 🗣️ MODE D: Oral Revision
                - **Keywords:** "revise chapter", "oral revision", "read this to me"
                - **Example:** "Revise chapter 2"
                - **Output:** Voice-friendly revision script
                
                #### 🧠 MODE E: Self-Testing
                - **Keywords:** "test me", "quiz me", "ask me questions"
                - **Example:** "Test me on Chapter 3"
                - **Output:** Quiz questions at 3 difficulty levels
                """)
            
            # ===== TAB 5: SETTINGS =====
            with gr.Tab("⚙️ Settings"):
                gr.Markdown("""
                ### API Configuration
                
                #### Gemini API Key
                Set your Gemini API key:
                ```bash
                # Windows
                $env:GEMINI_API_KEY="your_key_here"
                
                # Linux/Mac
                export GEMINI_API_KEY="your_key_here"
                ```
                
                Get free key: [Google AI Studio](https://aistudio.google.com/apikey)
                
                #### Groq API Key
                Already configured in `groq_rag.py`
                
                #### Ollama Setup
                1. Install: [ollama.com](https://ollama.com)
                2. Pull models:
                ```bash
                ollama pull llama3.1
                ollama pull phi3:mini
                ```
                
                ### 📊 System Status
                """)
                
                status_text = f"""
                **Available Models:**
                - Gemini: {'✅ Ready' if rag_interface.rag_gemini else '❌ Not configured'}
                - Groq: {'✅ Ready' if rag_interface.rag_groq else '❌ Not configured'}
                - Ollama: {'✅ Ready' if rag_interface.rag_ollama else '❌ Not configured'}
                
                **Documents Folder:** `documents/`
                **Vector Database:** `chroma_db/`
                """
                
                gr.Markdown(status_text)
        
        gr.Markdown("""
        ---
        ### 💡 Tips
        - Use **Gemini** for best balance of speed and quality
        - Use **Groq** when you need fastest responses
        - Use **Ollama** when working offline
        - Upload PDFs to automatically extract and index them
        - Try different study modes for different learning needs
        
        **Made with ❤️ using Gradio**
        """)
    
    return demo


if __name__ == "__main__":
    print("🚀 Starting RAG Study Assistant Web Interface...")
    print("=" * 60)
    
    demo = create_interface()
    
    # Launch with sharing enabled
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True for public URL
        show_error=True,
        inbrowser=True  # Auto-open in browser
    )
