# ENTERPRISE STUDY SYSTEM - ARCHITECTURE DOCUMENTATION

## 🏗️ System Overview

This is an enterprise-grade RAG (Retrieval-Augmented Generation) system designed for comprehensive book study and knowledge retention. The system implements 5 specialized study modes, each optimized for different learning scenarios.

---

## 📂 Directory Structure

```
enterprise_system/
├── src/
│   ├── core/                      # System Core (Config, Logging, Security)
│   │   ├── config/
│   │   │   └── settings.py        # Centralized configuration
│   │   ├── logging/
│   │   │   └── logger.py          # Professional logging system
│   │   └── security/
│   │       └── validator.py       # Input validation & sanitization
│   │
│   ├── domain/                    # Business Logic Layer
│   │   ├── orchestrator/
│   │   │   └── router.py          # Query routing & intent detection
│   │   └── study_modes/
│   │       ├── base/
│   │       │   └── interface.py   # Abstract base class (SOLID)
│   │       ├── recall/
│   │       │   ├── exact_recall.py    # MODE A
│   │       │   └── active_recall.py   # MODE E
│   │       ├── explainer/
│   │       │   └── stuck_point.py     # MODE B
│   │       ├── synthesizer/
│   │       │   └── concept_linker.py  # MODE C
│   │       └── tutor/
│   │           └── oral_revision.py   # MODE D
│   │
│   ├── infrastructure/            # External Services Layer
│   │   ├── database/
│   │   │   └── vector_store/
│   │   │       └── client.py      # ChromaDB abstraction
│   │   ├── llm/
│   │   │   └── client/
│   │   │       └── ollama_client.py   # LLM abstraction
│   │   └── filesystem/
│   │       ├── pdf/
│   │       │   └── processor.py   # PDF extraction & indexing
│   │       └── text/
│   │
│   └── interface/                 # User Interface Layer
│       ├── cli/
│       │   └── app.py             # Terminal interface
│       └── api/                   # Future: Web API
│
├── tests/                         # Test Suite
│   ├── unit/
│   └── integration/
│
├── documentation/
│   ├── architecture/
│   │   └── ARCHITECTURE.md        # This file
│   └── user_guides/
│
└── main.py                        # Entry point
```

---

## 🎯 Design Principles

### 1. **SOLID Principles**
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Easy to extend with new modes without modifying existing code
- **Liskov Substitution**: All modes implement the same interface
- **Interface Segregation**: Clean, focused interfaces
- **Dependency Inversion**: Depends on abstractions, not concrete implementations

### 2. **Separation of Concerns**
- **Core**: System-wide utilities (config, logging, security)
- **Domain**: Business logic (study modes, routing)
- **Infrastructure**: External dependencies (database, LLM, filesystem)
- **Interface**: User interaction (CLI, future API)

### 3. **Dependency Injection**
- Components receive their dependencies rather than creating them
- Makes testing and swapping implementations easy

---

## 🔄 Request Flow

```
User Input
    ↓
[CLI Interface] (src/interface/cli/app.py)
    ↓
[Input Validation] (src/core/security/validator.py)
    ↓
[Query Router] (src/domain/orchestrator/router.py)
    ↓
[Intent Detection] (Each mode's can_handle())
    ↓
[Mode Execution] (Selected mode's execute())
    ↓
[Vector Store Query] (src/infrastructure/database/vector_store/client.py)
    ↓
[LLM Generation] (src/infrastructure/llm/client/ollama_client.py)
    ↓
[Response Formatting] (Mode-specific formatting)
    ↓
[Display to User] (CLI output)
```

---

## 🧩 Study Modes

### MODE A: Exact Recall
- **Purpose**: Lossless text retrieval
- **Use Case**: "What is on page 14?"
- **Implementation**: `src/domain/study_modes/recall/exact_recall.py`
- **Key Feature**: Returns raw text without LLM processing

### MODE B: Stuck-Point Explanation
- **Purpose**: Surgical clarification of confusing parts
- **Use Case**: "I don't understand the 'thought vector' concept"
- **Implementation**: `src/domain/study_modes/explainer/stuck_point.py`
- **Key Feature**: Minimal, focused explanations using book context only

### MODE C: Concept Linking
- **Purpose**: Show relationships across chapters
- **Use Case**: "How does the attention mechanism relate to transformers?"
- **Implementation**: `src/domain/study_modes/synthesizer/concept_linker.py`
- **Key Feature**: Cross-references with page numbers

### MODE D: Oral Revision
- **Purpose**: Voice-friendly revision scripts
- **Use Case**: "Revise Chapter 2 for me"
- **Implementation**: `src/domain/study_modes/tutor/oral_revision.py`
- **Key Feature**: Sequential, conversational narration

### MODE E: Active Recall
- **Purpose**: Self-testing with tiered questions
- **Use Case**: "Test me on GPT models"
- **Implementation**: `src/domain/study_modes/recall/active_recall.py`
- **Key Feature**: 3-level difficulty progression

---

## 🔧 Configuration

All system settings are centralized in `src/core/config/settings.py`.

### Environment Variables
- `LLM_MODEL`: Model name (default: gpt-oss:120b-cloud)
- `LLM_TEMPERATURE`: Sampling temperature (default: 0.0)
- `VECTOR_DB_PATH`: ChromaDB location (default: ./chroma_db)
- `CHUNK_SIZE`: Text chunk size (default: 700)
- `DOCUMENTS_FOLDER`: Source documents (default: ./documents)

---

## 📊 Logging

Professional logging system in `src/core/logging/logger.py`:
- Console output (UTF-8 encoded)
- File output (`./logs/system_YYYYMMDD.log`)
- Structured format with timestamps
- Configurable log levels

---

## 🔒 Security

Input validation in `src/core/security/validator.py`:
- Maximum query length enforcement
- Injection attack prevention
- Input sanitization
- Null byte removal

---

## 🚀 Extending the System

### Adding a New Study Mode

1. Create new file in appropriate `study_modes/` subdirectory
2. Implement `IStudyMode` interface:
   ```python
   from src.domain.study_modes.base.interface import IStudyMode, ModeResponse
   
   class MyNewMode(IStudyMode):
       def can_handle(self, query: str) -> bool:
           # Detection logic
           
       def execute(self, query: str, context: dict) -> ModeResponse:
           # Execution logic
           
       def get_mode_name(self) -> str:
           return "MODE F: MY NEW MODE"
           
       def get_system_prompt(self, query: str, context: str) -> str:
           # Prompt generation
   ```

3. Register in `src/domain/orchestrator/router.py`:
   ```python
   from src.domain.study_modes.mynew.mode import MyNewMode
   
   self.modes = [
       # ... existing modes ...
       MyNewMode(),
   ]
   ```

### Swapping LLM Provider

1. Create new client in `src/infrastructure/llm/client/`
2. Implement same interface as `ollama_client.py`
3. Update configuration to use new client

---

## 📈 Scalability

Current system is designed to scale to:
- **100,000+ lines of code** (modular architecture)
- **Multiple LLM providers** (abstraction layer)
- **Different vector databases** (clean interface)
- **Web API** (interface layer separation)
- **Microservices** (domain separation)

---

## 🧪 Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user flows

Test files go in `tests/unit/` and `tests/integration/`.

---

## 📝 Future Enhancements

1. **Document Reloading**: Implement live document indexing
2. **Web API**: FastAPI-based REST API
3. **Answer Grading**: For MODE E self-tests
4. **Voice Integration**: Text-to-speech for MODE D
5. **Multi-user Support**: User sessions and history
6. **Analytics**: Study pattern tracking

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-04  
**Maintainer**: Enterprise Study System Team
