
import os
import sys
import time
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import io

# Force UTF-8 encoding for Windows terminals (CRITICAL for Emojis)
if sys.platform == "win32":
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class GroqRAG:
    def __init__(self, api_key, persist_directory="./chroma_db"):
        """Initialize with Groq API"""
        print("⚡ Warming up the Groq LPU Engines...")
        
        self.client = Groq(api_key=api_key)
        self.model_name = "llama-3.3-70b-versatile"  # The big, smart, fast one
        
        # Local embeddings (keep privacy where it matters)
        print("📚 Loading your Knowledge Layer...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        print("✅ System Online: Ready for High-Speed Study!")

    def ask(self, question):
        """High-speed query using Groq"""
        
        # 1. Search (God Mode Context: 30 chunks)
        try:
            relevant_docs = self.vector_store.similarity_search(question, k=30)
            if not relevant_docs:
                return "❌ I couldn't find anything about that in your books."
        except Exception as e:
            return f"❌ Database Error: {e}"

        # 2. Build Context
        context_list = []
        sources = set()
        for doc in relevant_docs:
            src = os.path.basename(doc.metadata.get('source', 'Unknown'))
            sources.add(src)
            context_list.append(f"SOURCE ({src}):\n{doc.page_content}")
        
        context_text = "\n\n".join(context_list)
        
        # 3. The "ChatGPT" System Prompt
        system_prompt = """You are a brilliant, friendly, and engaging AI Tutor suitable for advanced study.
        
YOUR STYLE:
- **Chatty & Fun:** Don't be a robot. Be like a smart friend explaining things over coffee.
- **Visual & Spacious:** Use bold text, bullet points, and blank lines to make reading easy.
- **Emoji Rich:** Use emojis to break up text and add flavor (e.g., 🚀, 💡, 🧠, 📚).
- **Deep but Clear:** Explain complex topics simply (analogies are great), but don't skip details.

FORMATTING RULES:
1. Start with a friendly opening (e.g., "Great question!", "Let's dive into this!").
2. Use ## Headers for key sections.
3. Use **Bold** for important terms.
4. End with a "Micro-Summary" and a "Next Step" question.

SOURCE MATERIAL:
Use ONLY the provided context. If the answer isn't there, say so honestly.
"""

        # 4. Call Groq API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXT:\n{context_text}\n\nUSER QUESTION: {question}"}
        ]

        print("🚀 Thinking at light speed...", end="\r")
        start_time = time.time()
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.6,
                max_tokens=4096,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            # Print Result
            print(" " * 50, end="\r") # Clear loading line
            full_response = completion.choices[0].message.content
            print(full_response)
            
            # Save to file so we never miss it
            with open("last_answer.md", "w", encoding="utf-8") as f:
                f.write(full_response)
                
            return full_response

        except Exception as e:
            return f"❌ Groq API Error: {str(e)}"

    def interactive(self):
        """Chat Loop"""
        print("\n" + "="*50)
        print("   GROQ TURBO STUDY COMPANION 🚀")
        print("   (Type 'quit' to exit)")
        print("="*50 + "\n")
        
        while True:
            try:
                q = input("👉 YOU: ").strip()
                if q.lower() in ['quit', 'exit', 'q']:
                    print("👋 See ya!")
                    break
                if not q: continue
                
                print("\n🤖 AI:")
                self.ask(q)
                print("-" * 50 + "\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    # Your Key
    key = "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"
    
    rag = GroqRAG(api_key=key)
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        rag.ask(query)
    else:
        rag.interactive()
