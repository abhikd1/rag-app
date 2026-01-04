# 📚 Enterprise Study System

> An industrial-grade RAG (Retrieval-Augmented Generation) system for comprehensive book study and knowledge retention.

## 🌟 Features

- **5 Specialized Study Modes** - Each optimized for different learning scenarios
- **Enterprise Architecture** - Modular, scalable, and maintainable
- **SOLID Principles** - Professional software engineering practices
- **Intelligent Routing** - Automatic intent detection
- **Security Layer** - Input validation and sanitization
- **Professional Logging** - Comprehensive system monitoring

---

## 🚀 Quick Start

```powershell
cd "c:\Users\sumit\rag app\enterprise_system"
python main.py
```

---

## 📋 Study Modes

| Mode | Purpose | Example Query |
|------|---------|---------------|
| **📄 MODE A** | Exact Recall | `Page 14` |
| **🧩 MODE B** | Stuck-Point Explanation | `I don't understand "thought vector"` |
| **🔗 MODE C** | Concept Linking | `How does X relate to Y?` |
| **🗣️ MODE D** | Oral Revision | `Revise Chapter 1` |
| **🧠 MODE E** | Active Recall | `Test me on transformers` |

---

## 🏗️ Architecture

```
enterprise_system/
├── src/
│   ├── core/           # Config, Logging, Security
│   ├── domain/         # Business Logic (Study Modes)
│   ├── infrastructure/ # External Services (DB, LLM)
│   └── interface/      # User Interfaces (CLI, API)
├── tests/              # Unit & Integration Tests
├── documentation/      # Architecture & User Guides
└── main.py            # Entry Point
```

**Design Principles:**
- ✅ Separation of Concerns
- ✅ Dependency Injection
- ✅ Interface Segregation
- ✅ Single Responsibility
- ✅ Open/Closed Principle

---

## 📖 Documentation

- **[Architecture Guide](documentation/architecture/ARCHITECTURE.md)** - System design and extensibility
- **[User Guide](documentation/user_guides/USER_GUIDE.md)** - How to use all features

---

## 🔧 Configuration

Edit `src/core/config/settings.py` or use environment variables:

```bash
LLM_MODEL=gpt-oss:120b-cloud
LLM_TEMPERATURE=0.0
VECTOR_DB_PATH=./chroma_db
CHUNK_SIZE=700
DOCUMENTS_FOLDER=./documents
```

---

## 🧪 Testing

```powershell
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/
```

---

## 📊 System Requirements

- Python 3.8+
- Ollama (for LLM)
- ChromaDB (for vector storage)
- PyMuPDF (for PDF processing)

---

## 🔒 Security Features

- Input validation and sanitization
- Injection attack prevention
- Maximum query length enforcement
- Null byte removal

---

## 📈 Scalability

Designed to scale to:
- **100,000+ lines of code**
- **Multiple LLM providers**
- **Different vector databases**
- **Web API deployment**
- **Microservices architecture**

---

## 🛠️ Extending the System

### Adding a New Study Mode

1. Create file in `src/domain/study_modes/`
2. Implement `IStudyMode` interface
3. Register in `src/domain/orchestrator/router.py`

See [Architecture Guide](documentation/architecture/ARCHITECTURE.md) for details.

---

## 📝 Logging

Logs are saved to `./logs/system_YYYYMMDD.log` with:
- Timestamps
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Module names
- UTF-8 encoding

---

## 🎯 Use Cases

- **Students**: Comprehensive book study and exam preparation
- **Researchers**: Quick fact-checking and concept linking
- **Educators**: Creating revision materials and quizzes
- **Professionals**: Knowledge retention and review

---

## 🤝 Contributing

This is an enterprise-grade system. Contributions should:
- Follow SOLID principles
- Include unit tests
- Update documentation
- Maintain separation of concerns

---

## 📄 License

Proprietary - Enterprise Study System

---

## 🙏 Acknowledgments

Built with:
- LangChain
- ChromaDB
- Ollama
- PyMuPDF

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: 2026-01-04

---

## 💡 Example Session

```
[YOU]: Page 14

[SYSTEM]:
================================================================================
📄 PAGE 14
================================================================================
[Exact text from page 14...]
================================================================================

[YOU]: I don't understand "thought vector"

[SYSTEM]:
================================================================================
🧩 STUCK-POINT EXPLANATION
================================================================================
💡 EXPLANATION: A thought vector is...
📖 BOOK RELEVANCE: This concept is crucial because...
🔗 CONNECTION: This relates back to...
================================================================================

[YOU]: Test me on this chapter

[SYSTEM]:
================================================================================
🧠 ACTIVE RECALL TEST
================================================================================
**Q1 (Basic):** What is a thought vector?
**Q2 (Intermediate):** How does the thought vector relate to...
**Q3 (Advanced):** Compare and contrast...
================================================================================
```

---

**Ready to revolutionize your study workflow? Run `python main.py` to get started!** 🚀
