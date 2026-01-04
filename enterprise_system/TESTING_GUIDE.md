# 🧪 TESTING GUIDE - ENTERPRISE STUDY SYSTEM

## 📋 QUICK START TESTING

### **Option 1: Automated Testing (Recommended)**

Run the automated test script:

```powershell
cd "c:\Users\sumit\rag app\enterprise_system"
python test_system.py
```

This will test all 5 modes automatically and show results.

---

### **Option 2: Manual Interactive Testing**

Start the system manually:

```powershell
cd "c:\Users\sumit\rag app\enterprise_system"
python main.py
```

Then try these queries one by one:

---

## 🧪 TEST CASES BY MODE

### **📄 MODE A: Exact Recall**

**Test 1:**
```
Page 14
```
**Expected:** Raw text from page 14

**Test 2:**
```
What is written on page 20?
```
**Expected:** Raw text from page 20

**Test 3:**
```
MODE: A Show me page 13
```
**Expected:** Forced MODE A, shows page 13

---

### **🧩 MODE B: Stuck-Point Explanation**

**Test 1:**
```
I am confused about the thought vector
```
**Expected:** Surgical explanation of "thought vector"

**Test 2:**
```
I don't understand what attention mechanism means
```
**Expected:** Focused explanation of attention mechanism

**Test 3:**
```
MODE: B Explain cold fusion
```
**Expected:** Forced MODE B, explains the "cold fusion" metaphor

---

### **🔗 MODE C: Concept Linking**

**Test 1:**
```
How does the attention mechanism relate to transformers?
```
**Expected:** Cross-references showing the relationship

**Test 2:**
```
Connect GPT-2 to GPT-3
```
**Expected:** Links between GPT-2 and GPT-3 across pages

**Test 3:**
```
MODE: C Link prompt engineering to LLM training
```
**Expected:** Forced MODE C, shows connections

---

### **🗣️ MODE D: Oral Revision**

**Test 1:**
```
Revise Chapter 1
```
**Expected:** Voice-friendly sequential script

**Test 2:**
```
Read the history of GPT models to me
```
**Expected:** Conversational narration

**Test 3:**
```
MODE: D Go through the transformer architecture
```
**Expected:** Forced MODE D, revision script

---

### **🧠 MODE E: Active Recall**

**Test 1:**
```
Test me on Chapter 1
```
**Expected:** 3 tiered questions (Basic, Intermediate, Advanced)

**Test 2:**
```
Quiz me on transformers
```
**Expected:** Questions about transformers

**Test 3:**
```
MODE: E Ask me about GPT models
```
**Expected:** Forced MODE E, generates quiz

---

## ✅ VERIFICATION CHECKLIST

After running tests, verify:

- [ ] MODE A returns exact text without LLM processing
- [ ] MODE B provides focused explanations
- [ ] MODE C shows cross-references with page numbers
- [ ] MODE D creates conversational scripts
- [ ] MODE E generates 3-level questions
- [ ] Input validation rejects suspicious inputs
- [ ] Logs are created in `./logs/` directory
- [ ] No crashes or unhandled exceptions

---

## 🐛 TROUBLESHOOTING

### **Error: "No relevant documents found"**
**Solution:** Run `python setup.py` to copy documents

### **Error: "Failed to initialize vector store"**
**Solution:** Check that ChromaDB path is correct in `src/core/config/settings.py`

### **Error: "LLM generation failed"**
**Solution:** Ensure Ollama is running: `ollama serve`

### **Error: "Module not found"**
**Solution:** Install dependencies: `pip install langchain chromadb ollama pymupdf`

---

## 📊 EXPECTED OUTPUT FORMAT

### **MODE A Output:**
```
================================================================================
📄 PAGE 14
================================================================================
[Exact text from the page...]
================================================================================
```

### **MODE B Output:**
```
================================================================================
🧩 STUCK-POINT EXPLANATION
================================================================================
💡 EXPLANATION: ...
📖 BOOK RELEVANCE: ...
🔗 CONNECTION: ...
================================================================================
```

### **MODE C Output:**
```
================================================================================
🔗 CONCEPT LINKING ANALYSIS
================================================================================
📍 [Section/Page]: ...
📍 [Section/Page]: ...
🎯 SYNTHESIS: ...
================================================================================
```

### **MODE D Output:**
```
================================================================================
🗣️ ORAL REVISION SCRIPT
================================================================================
[Sequential narration...]
================================================================================
```

### **MODE E Output:**
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

## 📝 LOGGING

All system activity is logged to:
```
./logs/system_YYYYMMDD.log
```

Check this file if you encounter issues.

---

## 🎯 SUCCESS CRITERIA

The system is working correctly if:

1. ✅ All 5 modes can be triggered
2. ✅ Each mode produces correctly formatted output
3. ✅ No crashes or unhandled exceptions
4. ✅ Logs are created and contain debug information
5. ✅ Input validation prevents malicious inputs

---

**Happy Testing! 🚀**
