# ⚡ Speed Optimization Guide

## Current Speed Issue

Your queries take 30-90 seconds because:
- CPU-only processing (no GPU)
- Large models (Llama 3.1 = 8B parameters)
- Dual-engine pipeline (2 models per query)
- Large context (k=5 documents)

---

## 🚀 Quick Fixes (Choose One)

### Option 1: Use Faster Models (RECOMMENDED)

**Install smaller models:**
```bash
ollama pull llama3.2:1b
ollama pull phi3:mini
```

**Update main.py:**
Change line ~120:
```python
# OLD (slow):
model='llama3.1'

# NEW (5x faster):
model='llama3.2:1b'
```

**Speed improvement:** 30-60s → 10-15s per query

---

### Option 2: Reduce Context Size

**Update main.py line ~100:**
```python
# OLD:
relevant_docs = self.vector_store.similarity_search(search_query, k=5)

# NEW:
relevant_docs = self.vector_store.similarity_search(search_query, k=2)
```

**Speed improvement:** 30-60s → 20-30s per query

---

### Option 3: Skip Formatting for Testing

**Temporarily disable Phi-3 formatting:**

In `main.py`, around line 140, comment out the formatting step:
```python
# TEMPORARY: Skip formatting for speed
# formatting_response_obj = ollama.generate(...)
# final_response = formatting_response_obj['response']

# Use raw response instead:
final_response = raw_answer
```

**Speed improvement:** 30-60s → 15-25s per query

---

### Option 4: Increase Temperature (Slight Speed Boost)

**Update main.py:**
```python
# OLD:
options={'temperature': 0.1}

# NEW:
options={'temperature': 0.3}
```

**Speed improvement:** 5-10% faster

---

## ⚡ FASTEST SETUP (For Testing Only)

```bash
# Install tinyllama (super fast, less accurate)
ollama pull tinyllama
```

**Update main.py:**
```python
# Line ~120:
model='tinyllama'  # Instead of llama3.1

# Line ~100:
k=2  # Instead of k=5

# Line ~120:
options={'temperature': 0.3}  # Instead of 0.1
```

**Speed:** 5-10 seconds per query (but lower quality)

---

## 🎯 RECOMMENDED FOR YOU

**For Evaluation Testing:**
1. Use `llama3.2:1b` (faster, still good quality)
2. Reduce k=2 (less context)
3. Keep Phi-3 formatting (important for evaluation)

**For Production Use:**
1. Keep `llama3.1` (best quality)
2. Keep k=5 (full context)
3. Keep Phi-3 formatting
4. Accept 30-60s response time

---

## 💡 The Reality

**You have 3 choices:**

1. **Fast + Less Accurate** → Use tinyllama, k=2
2. **Balanced** → Use llama3.2:1b, k=3
3. **Slow + Most Accurate** → Use llama3.1, k=5 (current)

**For evaluation, I recommend Option 2 (Balanced)**

---

## 🔧 How to Apply Changes

1. **Stop current process** (Ctrl+C if needed)
2. **Edit main.py** with changes above
3. **Run again:** `python main.py`
4. **Test speed improvement**

---

**Note:** The Master Evaluation Prompt tests QUALITY, not speed. 
Slower = more accurate = better evaluation results.
