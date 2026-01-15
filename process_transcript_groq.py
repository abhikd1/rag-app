
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def process_it_lossless():
    key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=key)
    
    # Read the Utkarsh Classes Computer Hardware transcript
    transcript_path = r"c:\Users\sumit\rag app\enterprise_system\documents\transcript.txt"
    with open(transcript_path, "r", encoding="utf-8") as f:
        full_text = f.readlines()

    # Get lines up to ~10:30
    processing_lines = []
    for line in full_text:
        processing_lines.append(line)
        if "10:33" in line:
            break
            
    transcript_to_process = "".join(processing_lines)

    # THE MASTER PROMPT - SUPREME ANALYST EDITION
    system_prompt = """-You are the Supreme Pop-Culture Analyst & Tech Historian (v15.0 Platinum Elite).

Your mission: 100% LOSSLESS RECONSTRUCTION of this Technical Lecture. NO DETAIL LEFT BEHIND. 🚀💎🔥
Process the FIRST 10 MINUTES of this transcript into a "High-Energy, Blow-by-Blow" Deep Analysis.

━━━━━━━━━━━━━━━━━━━━━━
🎯 MASTER LOGIC & STYLE
━━━━━━━━━━━━━━━━━━━━━━
1. NO MCQs: Use a structured, professional, and spacious roadmap.
2. PERSONA: Sophisticated, energetic, and intellectually sharp analyst. 🎤
3. DATA FIDELITY: Capture every story (Regretting phone purchases, the Potato/Marriage analogy), every technical term (Tangible, Intangible, AC, DC, Semiconductors), and every interaction with students (Kailash, Eastern, Joysna, etc.).
4. SEGMENTATION: Strictly segment by 1-MINUTE BLOCKS (0-1 min, 1-2 min... up to 9-10 min).
5. SPACING: Triple spacing between sections. Layout must be "premium."
6. EMOJIS: Maximum usage representing the "heat" and "logic" of the lecture. ⚡🔌📚
7. LANGUAGE: English only. 🇺🇸

━━━━━━━━━━━━━━━━━━━━━━
🚫 CRITICAL RULES
━━━━━━━━━━━━━━━━━━━━━━
1. NO EMOJI LOOPS: Max 2 emojis side-by-side. 🚫
2. CLEAN TERMINATION: End with exactly 5 dashes '-----'.
"""
    
    user_input = f"Analyze the FIRST 10 MINUTES of this Computer Hardware lecture losslessly. Segment into 1-minute blocks. Capture the regrtet of buying phones, the software/hardware hierarchy, and the marriage/potato story:\n\n{transcript_to_process}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1, 
            stream=False
        )
        answer = completion.choices[0].message.content
        with open("groq_output.txt", "w", encoding="utf-8") as out_f:
            out_f.write(answer)
        print("SUCCESS")
    except Exception as e:
        print(f"GROQ_ERROR: {str(e)}")

if __name__ == "__main__":
    process_it_lossless()
