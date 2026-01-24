"""
🎨 CHATGPT-STYLE PROMPT TEMPLATES
Generates beautiful, engaging responses like ChatGPT with rich formatting
"""

def get_page_explanation_prompt(page_num, page_content, filename="document"):
    """Anti-hallucination prompt for page explanations"""

    return f"""You are analyzing Page {page_num} from {filename}.

CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY use information explicitly stated in the page content below
2. If the content is unclear or insufficient, say "The content on this page is limited"
3. DO NOT add examples, explanations, or context not present in the source
4. DO NOT use general textbook knowledge to fill gaps
5. If you cannot answer fully from the content, say "This specific information is not clearly stated on this page"
6. DO NOT make assumptions about what "should" be on the page

ACTUAL PAGE {page_num} CONTENT:
{page_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Now explain ONLY what is written above in a clear, student-friendly manner like ChatGPT with rich formatting and emojis.
If the page discusses file operations, explain those operations.
If the page shows code examples, explain those examples.
If the page defines terms, explain those definitions.

Use ONLY the content provided above. Do not invent or assume anything.

REQUIRED OUTPUT STRUCTURE:

# [Page Title/Main Topic]

## What You'll Master
[Bullet list of 3-5 key concepts covered - be specific!]
- [Concept 1]
- [Concept 2]
- [Concept 3]

## Complete Breakdown

### [First Major Concept]
**Definition:** [Clear, simple explanation in 2-3 sentences]
**Why It Matters:** [Real-world relevance or exam importance]
**Key Points:**
- **[Point 1]:** [Detailed explanation]
- **[Point 2]:** [Detailed explanation]
- **[Point 3]:** [Detailed explanation]

**Remember:** [Memory trick or simple analogy]

**Example:** [If any example exists on the page, explain it step-by-step]

### [Second Major Concept]
[Repeat structure above for each concept]

## Visual Comparisons
[If comparing 2+ things, create a comparison table]

| Feature | Option A | Option B |
|---------|----------|----------|
| **[Aspect]** | [Detail] | [Detail] |

## Code/Syntax Examples
[If any code, formulas, or syntax:]
```[language]
[code here with inline comments]
```

## Common Mistakes & Tips
**Don't:** [Common mistake]
**Do:** [Correct approach]
**Pro Tip:** [Expert advice]

## Activities/Exercises Mentioned
[List any activities/exercises from the page]

## Complete Summary
**Everything Covered:** [List topics]
**Key Takeaway:** [One sentence]
**Exam Alert:** [Important note]

FORMATTING REQUIREMENTS:
1. Use rich emojis throughout (20+ minimum) to make it visual and engaging
2. **Bold** for ALL key terms
3. `Code blocks` for technical terms
4. Blockquotes for definitions
5. Friendly, conversational, enthusiastic tone. Use "you"
6. Explain EVERY term and cover EVERY example. Don't skip anything!

GENERATE THE COMPLETE PAGE {page_num} EXPLANATION NOW:
"""



def get_general_question_prompt(question, context, filename=None):
    """
    Generate ChatGPT-style prompt for GENERAL questions
    """
    file_info = f"**SOURCE:** {filename}\n" if filename else ""
    
    return f"""You are an elite educational AI tutor answering questions in ChatGPT's engaging style.

{file_info}
**STUDENT QUESTION:** {question}

**RELEVANT CONTENT:**
```
{context}
```

---

**RESPONSE REQUIREMENTS:**

### STRUCTURE:
# [Topic Title]
[Direct answer]

## Detailed Explanation
### [Main Point]
[Explanation with bold terms and emojis]

## Comparison/Table (If relevant)
## Code/Examples (If relevant)

## Important Notes
- Common Mistake
- Best Practice

## Quick Summary
- Main points
- Remember

### FORMATTING:
- 15+ emojis
- **Bold** key terms
- Rich markdown tables/code

### TONE:
Enthusiastic, clear, engaging. Use "you".

**ANSWER THE QUESTION NOW:**
"""


def get_concept_explanation_prompt(concept, context):
    """
    For explaining specific concepts in depth
    """
    return f"""You are explaining a concept in ChatGPT's crystal-clear, engaging style.

**CONCEPT TO EXPLAIN:** {concept}

**REFERENCE MATERIAL:**
```
{context}
```

---

**CREATE THIS STRUCTURE:**
# {concept}
## What Is It?
[2-3 sentences]

## Complete Explanation
[Deep dive with bullet points]

## Analogy
[Make it click]

## Example
[Step-by-step]

## Summary
In one sentence
Key points

### USE:
- 20+ emojis
- **Bold** for terms

**EXPLAIN THE CONCEPT NOW:**
"""

# Export templates
__all__ = ['get_page_explanation_prompt', 'get_general_question_prompt', 'get_concept_explanation_prompt']
