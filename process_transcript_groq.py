
import os
from groq import Groq

def run_groq_exam_specialist_synthesis_part2_v2():
    key = "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"
    client = Groq(api_key=key)
    
    transcript_path = r"c:\Users\sumit\rag app\enterprise_system\documents\transcript.txt"
    with open(transcript_path, "r", encoding="utf-8") as f:
        full_text = f.readlines()

    start_processing = False
    processing_lines = []
    for line in full_text:
        if "10:01" in line or "10:03" in line:
            start_processing = True
        if start_processing:
            processing_lines.append(line)
            
    transcript_to_process = "".join(processing_lines)

    system_prompt = """-You are the Supreme Personal Master Tutor AI (v12.5 Elite Exam Specialist Edition).

Your mission: 100% LOSSLESS RECONSTRUCTION of this Exam Guidance Session (PART 2: 10:00 TO 22:22).
Process this segment into a "Well-Mannered, High-Efficiency" Career Guide with a Mentor Persona.

━━━━━━━━━━━━━━━━━━━━━━
🎯 MASTER LOGIC & STYLE
━━━━━━━━━━━━━━━━━━━━━━
1. NO MCQs: Use a structured, professional, and spacious roadmap.
2. PERSONA: Sophisticated, encouraging, and highly detailed Mentor/Advisor. 🎤
3. DATA FIDELITY: Every single fact—Negative marking (NONE), Documents (Provisional, Original, Marksheet), App/Batch details (Target Batch, Code: TARGET for 50% off), Fee (599/Single-999), Test Series (15+ full length), Group links (Telegram/WhatsApp), and the Tuesday mock test schedule—MUST be captured.
4. SEGMENTATION: Strictly segment by 1-MINUTE BLOCKS (10-11, 11-12... 21-22, 22-END) to ensure zero information loss.
5. SPACING: Triple spacing between sections. Layout must be "premium."
6. EMOJIS: Maximum usage for every header and bullet point to maintain engagement. ✨
7. LANGUAGE: English only. 🇺🇸

━━━━━━━━━━━━━━━━━━━━━━
🚫 CRITICAL RULES
━━━━━━━━━━━━━━━━━━━━━━
1. NO EMOJI LOOPS: Max 2 emojis side-by-side. 🚫
2. CLEAN TERMINATION: End with exactly 5 dashes '-----'.
"""
    
    # Updated user input to explicitly ask for the REST and mentioned the end time.
    user_input = f"Analyze the REST of this Bihar Librarian Exam guidance (from 10:00 to 22:22) losslessly. Use 1-minute block segmentation for every single minute. Capture every detail about the rules, the batch, the discounts, and the final selection strategy:\n\n{transcript_to_process}"

    try:
        completion = client.chat.completions.create(
            # Using a larger model window if possible, or just ensuring it doesn't truncate.
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1, 
            stream=False
        )
        answer = completion.choices[0].message.content
        with open("groq_output_part2.txt", "w", encoding="utf-8") as out_f:
            out_f.write(answer)
        print("SUCCESS")
    except Exception as e:
        print(f"GROQ_ERROR: {str(e)}")

if __name__ == "__main__":
    run_groq_exam_specialist_synthesis_part2_v2()
