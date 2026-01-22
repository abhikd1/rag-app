
import os
from groq import Groq

def ask_groq_about_coding():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("GROQ_ERROR: GROQ_API_KEY environment variable not set.")
        return
    client = Groq(api_key=key)
    
    # The user's specific meta-question
    user_query = """
    Question for Groq: Can you (Llama 3.3 70B) code autonomously like 'Antigravity' (reading local files, writing code, and running terminal commands)? 
    If you cannot do it natively, what free tools/models (like Gemini 1.5 Flash) should a developer with limited budget and low-end local hardware (which can't run big Ollama models) use to get a high-end agentic coding experience? 
    Please respond in a descriptive, high-energy, and encouraging tone in English.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a world-class AI Expert and Developer Mentor. You provide ultra-descriptive, honest, and high-energy advice to developers."},
                {"role": "user", "content": user_query}
            ],
            temperature=0.2, 
            stream=False
        )
        answer = completion.choices[0].message.content
        with open("groq_meta_response.txt", "w", encoding="utf-8") as out_f:
            out_f.write(answer)
        print("SUCCESS")
    except Exception as e:
        print(f"GROQ_ERROR: {str(e)}")

if __name__ == "__main__":
    ask_groq_about_coding()
