
import os
from groq import Groq

def ask_groq_to_build_translator():
    # API Key Configuration
    key = "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"
    client = Groq(api_key=key)
    
    # Prompt for Groq: Building the Hindi-to-English translation utility
    system_prompt = """You are a Master Python Engineer. Your goal is to write clean, high-efficiency, and production-grade code.
The user needs a Hindi-to-English translation utility.
- Language: Python (match the current project tech stack).
- Requirements: Must handle large text, maintain formatting, and be easy to integrate.
- Preference: Use reliable libraries like 'deep-translator' or 'googletrans' (Python libraries).
- Output: Multiple files if necessary (e.g., a core translation module and a test script).
"""

    user_query = """
    Please write the Python code for a professional Hindi-to-English Translation System.
    1. Create 'translator_core.py': A class-based utility that handles text translation. Match it with my project's Python architecture.
    2. Provide a 'test_translator.py': A script to demonstrate translation of a Hindi paragraph.
    Ensure handling for long strings and basic error checking. 
    Use the 'deep-translator' library as it's stable and free.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1, 
            stream=False
        )
        answer = completion.choices[0].message.content
        
        # Save the result to a file for review
        output_file = r"c:\Users\sumit\rag app\translator_code_from_groq.txt"
        with open(output_file, "w", encoding="utf-8") as out_f:
            out_f.write(answer)
        
        print(f"SUCCESS: Translation code generated in {output_file}")
    except Exception as e:
        print(f"GROQ_ERROR: {str(e)}")

if __name__ == "__main__":
    ask_groq_to_build_translator()
