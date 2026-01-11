---
description: Run comprehensive RAG system evaluation using the Master Prompt
---

# RAG System Evaluation Workflow

This workflow guides you through evaluating your RAG application using the Master Evaluation Prompt.

## Prerequisites

- Ensure `MASTER_EVALUATION_PROMPT.md` exists in the project root
- Have at least one document ingested (with `_RAW_TEXT.txt` and `_INDEX.txt`)
- Ollama running with `llama3.1` and `phi-3:mini` models installed

## Evaluation Steps

### 1. Prepare Test Document

Ensure you have a test document ready:
- Check that `documents/` contains at least one `_RAW_TEXT.txt` file
- Verify corresponding `_INDEX.txt` exists (if not, generate it first)

### 2. Copy Master Prompt

Open `MASTER_EVALUATION_PROMPT.md` and copy the entire content.

### 3. Run Evaluation with External LLM

**Option A: Using Claude (Recommended)**
1. Go to https://claude.ai
2. Start a new conversation
3. Paste the entire Master Prompt
4. Add context: "Please evaluate the RAG system described. I will provide test outputs."
5. Run test queries through your RAG app and paste outputs for evaluation

**Option B: Using GPT-4**
1. Go to https://chat.openai.com
2. Start a new chat
3. Paste the entire Master Prompt
4. Follow same process as Claude

**Option C: Using Local Model (Advanced)**
```bash
# Use a large local model if available
ollama run llama3.1:70b
```
Then paste the Master Prompt and provide test outputs.

### 4. Run Test Scenarios

Execute each test category systematically:

#### Test 1: Indexing
```bash
python main.py
# Enter: "Create the full index of this book"
# Copy output and paste to evaluator
```

#### Test 2: Reading Flow
```bash
python main.py
# Enter: "Start reading Chapter 1"
# Then: "Continue"
# Copy outputs and paste to evaluator
```

#### Test 3: Transcript Mode (if applicable)
```bash
python main.py
# Enter: "Explain 0-10 minutes"
# Copy output and paste to evaluator
```

#### Test 4: Zero-Loss Audit
```bash
python main.py
# Enter: "Have we covered everything from Chapter 2?"
# Copy output and paste to evaluator
```

#### Test 5: Math/Logic
```bash
python main.py
# Enter: "Solve Example 4.2 using the book method"
# Copy output and paste to evaluator
```

#### Test 6: Reasoning
```bash
python main.py
# Enter: "Why does Chapter 5 contradict Chapter 2?"
# Copy output and paste to evaluator
```

### 5. Collect Evaluation Results

The evaluator will provide:
- ✅ PASS / ❌ FAIL for each category
- 🔧 Fix recommendations
- 🧠 Missing capabilities
- 🧪 Additional tests to add

### 6. Document Findings

Create an evaluation report:
```bash
# Create evaluation results file
notepad evaluation_results.md
```

Document:
- Date of evaluation
- Test results for each category
- Specific failures with examples
- Recommended fixes
- Priority order for improvements

### 7. Implement Fixes

Based on evaluation results:
1. Prioritize critical failures (Indexing, Zero-Loss, Pipeline)
2. Update relevant handler files
3. Re-run failed tests
4. Document improvements

## Quick Evaluation Command

For rapid testing of specific features:

```bash
# Test indexing
python main.py
# Query: "Create the full index of this book"

# Test reading flow
python main.py
# Query: "Start reading Chapter 1"
# Query: "Continue"

# Test completeness
python main.py
# Query: "List all concepts in Chapter 2"
```

## Continuous Evaluation

Schedule regular evaluations:
- After adding new documents
- After modifying mode handlers
- After updating prompts
- Before major releases
- Weekly during active development

## Notes

- Keep all evaluation outputs for historical comparison
- Track improvements over time
- Use evaluation results to refine prompts and handlers
- Share evaluation reports when seeking help or collaboration
