
import os
import sys
from groq import Groq

def run_pro_groq_transcript_finale():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("GROQ_ERROR: GROQ_API_KEY environment variable not set.")
        return
    client = Groq(api_key=key)
    
    # 📝 RAW TRANSCRIPT CHUNK: 1:30:00 - THE END
    with open(r"c:\Users\sumit\rag app\documents\all transcript.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        chunk_text = "".join(lines[1738:]) 

    # 👑 THE "ULTRA-STRICT / ELITE" MASTER PROMPT
    system_prompt = """-You are the Supreme Personal Master Tutor AI (v11.9 Elite Edition).

Your mission: 200% Readability. 100% Fidelity (LOSSLESS). NO DATA LEFT BEHIND. 🚀💎🔥

━━━━━━━━━━━━━━━━━━━━━━
🚫 CRITICAL SAFETY RULES
━━━━━━━━━━━━━━━━━━━━━━
1. NO EMOJI LOOPS: Never place more than 2 emojis side-by-side. 🚫
2. NO REPETITION: Do not repeat symbols or words at the end of the message. 🚫
3. CLEAN TERMINATION: End your response with exactly 5 dashes '-----' and nothing else. 🚫

━━━━━━━━━━━━━━━━━━━━━━
🌟 THE 200% READABILITY RULES
━━━━━━━━━━━━━━━━━━━━━━
1. HYPER-SPACIOUS: Triple spacing between ALL major sections. ☁️
2. PUNCHY: Single, impactful sentences for every bullet. 💥
3. BOLDING: Bold terms like "Rent Mafia", "Electricity Mafia", "U-Block", "Nathanpur Village", "Reclaim Your Soul". ⚡

━━━━━━━━━━━━━━━━━━━━━━
🧩 OUTPUT STRUCTURE (STRICT)
━━━━━━━━━━━━━━━━━━━━━━
📌 **The Gurgaon Math & Final Escape (90 Min - End)**
🧠 **The "Cyber City" Illusion** (The gap between dreams and reality)
🪜 **Phase: THE RENT & ELECTRICITY MAFIA** (Gurgaon's hidden tax)
📊 **The Monthly Budget of a Slave** (Detailed table of expenses)
🔍 **The Corrupt Education & System** (Sattu theft to principal corruption)
⚠️ **Parting Advice: RECLAIM YOUR SOUL** (The closing message)
🧪 **Modern Analogy** (The Gilded Cage)
🎯 **Final Personal Deep Insight Box**
📘 **The Final Glossary** (Rent Mafia, Social Signaling, U-Block Reality)
📝 **Ultra-Short Summary**

Presentation Rule: Focus on the "Gurgaon Math" where ₹15k Rent + ₹6k Electricity + ₹6k Travel leaves even a ₹50k earner broke. Mention the speaker's childhood observation of corruption (Principals stealing nutrition/Sattu meant for children). Conclude with the speaker's final urge to be "Vocal" and "Reclaim your freedom."
"""
    
    user_input = f"Explain the final 15 minutes (90:00 to the end) of this transcript losslessly with 200% readability. Focus on the Gurgaon Rent/Electricity Mafia, the corruption in schools/government schemes (Sattu theft), the school-to-office pipeline, and the final message of reclaim your soul:\n\n{chunk_text}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            stream=False
        )
        answer = completion.choices[0].message.content
        with open("debug_answer.txt", "w", encoding="utf-8") as f:
            f.write(answer)
        print("GROQ_SUCCESS")
    except Exception as e:
        print(f"GROQ_ERROR: {str(e)}")

if __name__ == "__main__":
    run_pro_groq_transcript_finale()
