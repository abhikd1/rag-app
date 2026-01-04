# ENTERPRISE STUDY SYSTEM - USER GUIDE

## 🚀 Quick Start

### Installation

1. **Navigate to the system directory:**
   ```powershell
   cd "c:\Users\sumit\rag app\enterprise_system"
   ```

2. **Run the system:**
   ```powershell
   python main.py
   ```

---

## 📚 Using the 5 Study Modes

The system automatically detects which mode you need based on your question. You can also force a specific mode by typing `MODE: X` at the start.

### 📄 MODE A: Exact Recall

**What it does:** Returns word-for-word text from specific pages.

**When to use:** When you need the exact content without any interpretation.

**Examples:**
```
Page 14
What is written on page 25?
Show me the exact text from page 100
MODE: A Tell me about transformers
```

**Output:** Raw text exactly as it appears in the book.

---

### 🧩 MODE B: Stuck-Point Explanation

**What it does:** Explains only the specific part you're confused about.

**When to use:** When a particular sentence or concept doesn't make sense.

**Examples:**
```
I am confused about the "thought vector" on page 20
I don't understand what "attention mechanism" means
Explain this part: "cold fusion had finally arrived"
MODE: B What is seq2seq?
```

**Output:** Focused explanation using only book context.

---

### 🔗 MODE C: Concept Linking

**What it does:** Shows how concepts connect across different chapters.

**When to use:** When you want to see the big picture and relationships.

**Examples:**
```
How does the attention mechanism relate to transformers?
Connect the concept of "embeddings" to earlier chapters
What is the relationship between GPT-2 and GPT-3?
MODE: C Link prompt engineering to LLM training
```

**Output:** Cross-references with specific page numbers and explanations.

---

### 🗣️ MODE D: Oral Revision

**What it does:** Creates a smooth, voice-friendly script for revision.

**When to use:** When you want to review material you've already studied.

**Examples:**
```
Revise Chapter 1
Read Chapter 2 to me
Oral revision of the transformer architecture
MODE: D Go through the history of GPT models
```

**Output:** Sequential, conversational script ready to be read aloud.

---

### 🧠 MODE E: Active Recall

**What it does:** Generates tiered questions to test your knowledge.

**When to use:** When you want to verify what you've learned.

**Examples:**
```
Test me on Chapter 1
Quiz me on transformers
Generate questions about prompt engineering
MODE: E Ask me about GPT models
```

**Output:** 3 questions (Basic, Intermediate, Advanced) based on the content.

---

## 💡 Tips for Best Results

### 1. **Be Specific**
- ❌ "Tell me about AI"
- ✅ "What is written on page 14 about GPT-2?"

### 2. **Use Natural Language**
You don't need to memorize commands. Just ask naturally:
- "I don't get the attention mechanism"
- "Test me on Chapter 2"
- "Page 25"

### 3. **Force a Mode When Needed**
If auto-detection picks the wrong mode, be explicit:
```
MODE: A (for exact text)
MODE: B (for explanation)
MODE: C (for linking)
MODE: D (for revision)
MODE: E (for testing)
```

### 4. **Combine Modes**
Use different modes for different purposes:
1. Start with **MODE A** to read the raw content
2. Use **MODE B** if something is confusing
3. Use **MODE C** to see how it connects to other chapters
4. Use **MODE D** to revise everything
5. Use **MODE E** to test yourself

---

## 🎯 Common Workflows

### Workflow 1: First-Time Learning
```
1. "Page 12" (MODE A - Read raw content)
2. "I don't understand 'thought vector'" (MODE B - Clarify confusion)
3. "How does this relate to earlier concepts?" (MODE C - See connections)
```

### Workflow 2: Pre-Exam Revision
```
1. "Revise Chapter 1" (MODE D - Sequential review)
2. "Test me on Chapter 1" (MODE E - Self-assessment)
3. "Page 25" (MODE A - Quick fact check)
```

### Workflow 3: Deep Understanding
```
1. "Page 20" (MODE A - Read content)
2. "Connect attention mechanism to transformers" (MODE C - See relationships)
3. "Explain the attention mechanism" (MODE B - Clarify if needed)
```

---

## ⚙️ Special Commands

- **`modes`**: List all available modes
- **`reload`**: Re-index documents (future feature)
- **`quit`** or **`exit`**: Close the system

---

## 🐛 Troubleshooting

### "No matching content found"
- **Cause:** The topic isn't in your indexed documents
- **Solution:** Make sure you've loaded the correct PDF

### "Error: Required services not available"
- **Cause:** Vector store or LLM client failed to initialize
- **Solution:** Check that Ollama is running and ChromaDB is accessible

### Mode auto-detection picks wrong mode
- **Solution:** Use explicit mode selection: `MODE: X your question`

---

## 📊 Understanding the Output

Each mode has a distinct output format:

**MODE A:**
```
================================================================================
📄 PAGE 14
================================================================================
[Exact text from the page]
================================================================================
```

**MODE B:**
```
================================================================================
🧩 STUCK-POINT EXPLANATION
================================================================================
💡 EXPLANATION: ...
📖 BOOK RELEVANCE: ...
🔗 CONNECTION: ...
================================================================================
```

**MODE C:**
```
================================================================================
🔗 CONCEPT LINKING ANALYSIS
================================================================================
📍 [Section/Page]: Relationship...
📍 [Section/Page]: Relationship...
🎯 SYNTHESIS: ...
================================================================================
```

**MODE D:**
```
================================================================================
🗣️ ORAL REVISION SCRIPT
================================================================================
[Voice-friendly sequential narration]
================================================================================
```

**MODE E:**
```
================================================================================
🧠 ACTIVE RECALL TEST
================================================================================
**Q1 (Basic):** ...
**Q2 (Intermediate):** ...
**Q3 (Advanced):** ...
================================================================================
```

---

## 🎓 Study Best Practices

1. **Active Learning**: Use MODE E regularly to test yourself
2. **Spaced Repetition**: Use MODE D to review at intervals
3. **Deep Processing**: Use MODE C to connect concepts
4. **Clarify Immediately**: Use MODE B when confused
5. **Verify Understanding**: Use MODE A to check facts

---

## 📞 Support

For issues or questions:
1. Check the Architecture Documentation
2. Review the logs in `./logs/`
3. Ensure all dependencies are installed

---

**Happy Studying! 📚✨**
