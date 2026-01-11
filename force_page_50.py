import os
import sys
import io
import ollama

# Fix Windows Unicode Output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_page_content(page_num):
    file_path = "c:\\Users\\sumit\\rag app\\documents\\prompt-engineering-for-llms-the-art-and-science-of-building-large-language-modelbased-applications-9781098156152 (1)_RAW_TEXT.txt"
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    start_marker = f"📄 PAGE {page_num}"
    end_marker = f"📄 PAGE {int(page_num) + 1}"
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return None
        
    end_idx = content.find(end_marker)
    if end_idx == -1:
        end_idx = len(content)
        
    return content[start_idx:end_idx]

def process_with_ai(text):
    print(f"[AI] Found Page 50! Processing with Phi-3 (Formatting)...")
    
    # 1. Formatting
    formatting_prompt = f"""Rewrite the content below to be extremely readable and engaging.
    
RULES:
- Use a friendly, ChatGPT-like tone.
- Use bullet points.
- Emoji style: 📚 💡 ✅.
- Summarize the key points clearly.

CONTENT:
{text}

REWRITTEN ANSWER:"""

    response = ollama.generate(
        model='phi3:mini', 
        prompt=formatting_prompt,
        options={'temperature': 0.3}
    )
    return response['response']

if __name__ == "__main__":
    page_text = get_page_content(50)
    if page_text:
        print(process_with_ai(page_text))
    else:
        print("Page 50 not found in raw text file.")
