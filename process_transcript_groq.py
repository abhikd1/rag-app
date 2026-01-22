
import os
import sys
from groq import Groq

# Fix Windows Terminal encoding for printing emojis/special characters
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def process_it_lossless():
    # Groq API Key from environment variable
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("ERROR: GROQ_API_KEY environment variable not set.")
        return
    client = Groq(api_key=key)
    
    # ✅ FIXED: Correct path to the Hindi podcast transcript
    transcript_path = r"c:\Users\sumit\rag app\documents\all transcript.txt"
    if not os.path.exists(transcript_path):
        print(f"ERROR: File not found at {transcript_path}")
        return

    with open(transcript_path, "r", encoding="utf-8") as f:
        full_text = f.readlines()

    # ✅ Extract 10-20 MINUTES
    processing_lines = []
    started = False
    
    print(f"📄 Extracting 10-20 minutes from transcript...")
    
    for line in full_text:
        # Start from 10:00
        if not started:
            if "10:0" in line or "10:1" in line or "10:2" in line:
                started = True
        
        if started:
            processing_lines.append(line)
            # Stop at 20:00
            if "20:0" in line or "20:1" in line:
                break
            
    transcript_to_process = "".join(processing_lines)
    
    if not transcript_to_process:
        print("ERROR: No transcript content found for the specified range.")
        return

    print(f"✅ Extracted {len(processing_lines)} lines from 10-20 minutes.\n")

    # THE LOSSLESS EXTRACTION ENGINE PROMPT
    system_prompt = """🧠 ROLE:
You are a LOSSLESS INFORMATION EXTRACTION ENGINE.
You are NOT a summarizer.
You are NOT an editor.
You are NOT an advisor.
You are NOT allowed to “optimize” content.

The input text is a REAL TRANSCRIPT.
It is the ABSOLUTE SOURCE OF TRUTH.

🎯 CORE OBJECTIVE:
Extract and present ALL information with ZERO LOSS.

🧾 YOU MUST PRESERVE (MANDATORY):
✅ Every emotion (anger 😡, despair 💀, guilt 😔, fear 😰)
✅ Every number, salary, cost, percentage, ratio 💰
✅ Every timeline and time-stamp ⏱️
✅ Every accusation, power imbalance, exploitation 🔥
✅ Every cause → effect → consequence chain 🔄
✅ Repetition if it reflects psychological pressure 🧠

🚫 YOU ARE STRICTLY FORBIDDEN TO:
❌ Summarize
❌ Shorten
❌ Generalize
❌ Sanitize language
❌ Add advice, solutions, or moral commentary
❌ Replace specifics with abstractions
❌ Drop details because they feel “obvious”
❌ Merge points that change intensity or meaning

📐 OUTPUT FORMAT (NON-NEGOTIABLE):
🕒 Time-range based sections (e.g. 20:00–21:00, 21:00–22:00)
🎬 Strong documentary-style section titles
📌 Bullet points (clear, structured)
🎭 Emojis used INTENTIONALLY to reinforce meaning
🧠 Maintain narrative tension and emotional weight
📊 Preserve ALL math exactly as stated

🧪 SELF-VALIDATION RULE:
If EVEN ONE factual, emotional, or numerical detail
from the transcript is missing or weakened,
YOUR OUTPUT IS INVALID.

🚨 CONTEXT SAFETY RULE:
If context length is reached or risk of data loss appears,
STOP immediately and output ONLY:
“🛑 CONTEXT LIMIT REACHED — NO INFORMATION DROPPED”

▶️ TASK:
Process the transcript below in FULL COMPLIANCE.
Do NOT explain what you are doing.
Do NOT add commentary.
ONLY output the structured extraction.
"""
    
    user_input = f"Process minutes 10:00 to 20:00 of this Hindi podcast transcript about corporate life. Cover everything losslessly and divide it into 1-minute blocks:\n\n{transcript_to_process}"

    print("=" * 80)
    print("🚀 [GROQ STREAMING] STARTING LOSSLESS EXTRACTION (10-20 MIN)")
    print("=" * 80)
    print("\n📺 LIVE OUTPUT (Streaming in real-time):\n")
    print("-" * 80 + "\n")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1, 
            stream=True 
        )
        
        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                print(text, end="", flush=True)
                full_response += text
                
        # Save to file after streaming completes
        output_file = "groq_output_10_20.txt"
        with open(output_file, "w", encoding="utf-8") as out_f:
            out_f.write(full_response)
        
        print("\n\n" + "=" * 80)
        print(f"✅ [SUCCESS] Lossless Extraction saved to {output_file}")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ [GROQ_ERROR]: {str(e)}")

if __name__ == "__main__":
    process_it_lossless()
