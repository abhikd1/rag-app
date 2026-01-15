# 🎯 Quick Evaluation Guide

## What You Now Have

✅ **MASTER_EVALUATION_PROMPT.md** - The authoritative contract for testing your RAG system  
✅ **run_evaluation_tests.py** - Automated test runner  
✅ **.agent/workflows/run-evaluation.md** - Step-by-step workflow  
✅ **Complete codebase alignment** - All required files present

---

## 🚀 How to Run Evaluation (3 Methods)

### Method 1: Automated Testing (Recommended)

```bash
# Run all tests automatically
python run_evaluation_tests.py
```

This will:
- Execute all 25+ test scenarios
- Save results to `evaluation_outputs/evaluation_YYYYMMDD_HHMMSS.md`
- Generate a comprehensive report

Then:
1. Open the generated results file
2. Copy entire content
3. Go to Claude.ai or ChatGPT
4. Paste `MASTER_EVALUATION_PROMPT.md` first
5. Paste the results file
6. Ask: "Please evaluate this RAG system based on the Master Prompt"

---

### Method 2: Manual Testing (Interactive)

```bash
# Run your RAG app normally
python main.py
```

Then run test queries one by one:

**Indexing Tests:**
- "Create the full index of this book"
- "Show only Chapter 3 headings"
- "List subtopics under 2.1"

**Reading Flow Tests:**
- "Start reading Chapter 1"
- "Continue"
- "Pause here and summarize"

**Zero-Loss Tests:**
- "Have we covered everything from Chapter 2?"
- "What concepts are left unread?"
- "List what I haven't studied yet"

Copy outputs and paste to evaluator.

---

### Method 3: Workflow-Guided (Detailed)

```bash
# Use the workflow command
/run-evaluation
```

Follow the step-by-step guide in `.agent/workflows/run-evaluation.md`

---

## 📊 What the Evaluator Will Check

### ✅ PASS Criteria

1. **Indexing** - Complete, hierarchical, preserves numbering
2. **Reading Flow** - Linear, asks before continuing, no skipping
3. **Completeness** - Zero content loss, full coverage tracking
4. **Reasoning** - Logical, step-by-step, fact-based
5. **Math** - Correct, uses book methods, shows work
6. **Readability** - Formatted, engaging, ChatGPT-like
7. **Engagement** - Emojis, headings, white space, micro-summaries

### ❌ FAIL Triggers

- Missing index entries
- Skipped content
- Boring wall-of-text output
- Hallucinated facts
- Auto-continuation without asking
- Content outside time ranges (transcripts)
- Plain academic text (no formatting)

---

## 🔧 After Evaluation

The evaluator will provide:

1. **Category Scores** - PASS/FAIL for each area
2. **Fix Recommendations** - Specific code changes needed
3. **Missing Capabilities** - Features to add
4. **Additional Tests** - Edge cases to cover

Then you can:
- Prioritize fixes (start with critical failures)
- Update relevant handler files
- Re-run failed tests
- Track improvements over time

---

## 📁 File Structure Reference

```
rag app/
├── MASTER_EVALUATION_PROMPT.md      ← The contract
├── run_evaluation_tests.py          ← Automated runner
├── .agent/workflows/
│   └── run-evaluation.md            ← Manual workflow
├── evaluation_outputs/              ← Test results (auto-created)
│   └── evaluation_YYYYMMDD.md
├── main.py                          ← Orchestrator
├── query_router.py                  ← Mode selector
├── mode_a_handler.py                ← Page recall
├── mode_b_handler.py                ← Deep explanations
├── mode_c_handler.py                ← Cross-chapter
├── mode_d_handler.py                ← Oral/revision
├── mode_e_handler.py                ← Active recall
├── chroma_db/                       ← Vector store
└── documents/
    ├── *_RAW_TEXT.txt               ← Source truth
    └── *_INDEX.txt                  ← Book indexes
```

---

## 🎯 Core Principles (Never Forget)

1. ❌ **NO hallucination**
2. ❌ **NO skipping content**
3. ❌ **NO vague summaries**
4. ❌ **NO boring wall-of-text**
5. ✅ **Index first, then content**
6. ✅ **Readable, paced, human-friendly**
7. ✅ **Ask user before moving forward**

---

## 🧠 Model Pipeline (Strict)

```
Documents → ChromaDB → Llama 3.1 (Reasoning) → Phi-3 Mini (Formatting) → User
```

**Llama 3.1** (temp ≤ 0.2):
- Facts only
- Logic only
- Zero formatting

**Phi-3 Mini** (temp 0.6-0.8):
- Formatting only
- Style only
- Preserve facts exactly

---

## 🚨 Quick Troubleshooting

**Problem:** Tests fail with import errors  
**Solution:** Ensure you're in the project directory and have all dependencies installed

**Problem:** No output generated  
**Solution:** Check that documents exist in `documents/` folder

**Problem:** Evaluator says "missing index"  
**Solution:** Run `python get_book_index.py` first to generate indexes

**Problem:** Output is boring/plain text  
**Solution:** This is what the evaluation will catch - implement fixes based on evaluator feedback

---

## 📞 Next Steps

1. **Run automated tests:** `python run_evaluation_tests.py`
2. **Get evaluation:** Paste results + Master Prompt to Claude/GPT-4
3. **Implement fixes:** Based on evaluator recommendations
4. **Re-test:** Run tests again to verify improvements
5. **Iterate:** Repeat until all categories PASS

---

## 🎓 Remember

This system is designed to let you **read entire books without missing anything and without boredom**.

The Master Prompt ensures:
- **DeepSeek-level depth** (via Llama 3.1)
- **ChatGPT-level readability** (via Phi-3 Mini)
- **Zero content loss** (via strict testing)
- **Engaging flow** (via style requirements)

You now have the **complete evaluation framework**. Use it to harden your RAG system to production quality.

---

**Last Updated:** 2026-01-09  
**Version:** 1.0
