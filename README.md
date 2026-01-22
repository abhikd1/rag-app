# 📚 RAG Study System - Complete Edition

AI-powered document analysis system with hierarchical indexing and multi-model support.

## 🚀 Quick Start (3 Steps)

### 1️⃣ Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2️⃣ Setup API Keys
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
# Edit .env and add your keys
```

### 3️⃣ Run the Server
```powershell
python ultimate_server.py
```

Open browser: **http://localhost:5000**

---

## 📦 What's Included

### Core System Files
- `ultimate_server.py` - Main Flask server
- `gemini_rag.py` - Gemini RAG engine
- `groq_rag.py` - Groq integration
- `index_generator_fixed.py` - Hierarchical index generator

### User Interfaces
- `ultimate_interface.html` - Main study interface
- `upload_documents.html` - Document upload
- `study_master_portal.html` - Study dashboard
- `web_ui.html` - Alternative UI

### Utilities
- `verify_system.py` - System health check
- `show_index.py` - Display document index
- `mode_a_extractor.py` - PDF text extraction

### Documentation
- `ULTIMATE_SETUP_GUIDE.md` - Complete setup guide
- `SYSTEM_ARCHITECTURE_MAP.md` - System architecture
- `START_WITHOUT_FLASK.md` - Standalone usage

---

## 🎯 Features

### 📖 Study Modes
- **RAW Mode** - View exact page content
- **EXPLAIN Mode** - AI-powered explanations
- **TOPIC Mode** - Topic-based learning

### 🤖 AI Models
- **Gemini 2.5 Flash** - Google's latest model
- **Groq Llama 3.3** - Ultra-fast inference

### 📊 Document Analysis
- Hierarchical topic indexing
- Page-by-page summaries
- Smart caching system

---

## 📁 Project Structure

```
rag-app/
├── ultimate_server.py          # Main server
├── gemini_rag.py              # RAG engine
├── groq_rag.py                # Groq integration
├── index_generator_fixed.py   # Index generator
├── ultimate_interface.html    # Main UI
├── documents/                 # PDF storage
│   ├── *.pdf                 # Your PDFs
│   ├── *_RAW_TEXT.txt       # Extracted text
│   └── *_INDEX.txt          # Generated indexes
├── chroma_db/                # Vector database (auto-created)
└── requirements.txt          # Dependencies
```

---

## 🔧 Troubleshooting

### Server won't start
```powershell
# Check Python version (3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### API errors
- Check `.env` file exists and has valid keys
- Verify keys at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check Groq credits at [Groq Console](https://console.groq.com)

### Documents not loading
```powershell
# Verify documents folder exists
mkdir documents

# Check file permissions
icacls documents
```

---

## 📚 Documentation

- [Complete Setup Guide](ULTIMATE_SETUP_GUIDE.md)
- [System Architecture](SYSTEM_ARCHITECTURE_MAP.md)
- [Flask Installation](FLASK_INSTALLATION_GUIDE.md)

---

## 🎓 Use Cases

- **Exam Preparation** - Study textbooks with AI assistance
- **Document Analysis** - Analyze technical documents
- **Research** - Extract insights from PDFs
- **Learning** - Interactive topic-based learning

---

## ⚙️ System Requirements

- Python 3.8+
- 4GB RAM minimum
- Internet connection (for AI APIs)
- Modern web browser

---

## 📝 License

Free to use for personal and educational purposes.

---

## 🤝 Support

For issues, check the documentation or create an issue on GitHub.

---

**Made with ❤️ for better learning**
