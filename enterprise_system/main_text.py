"""
Master Architect - Text Mode (Turbo Powered)
A high-performance text-based interface for the RAG system.
Optimized for deep study and lossless recall.
"""
import sys
import os
import io
import time

# Force UTF-8 for beautiful output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.infrastructure.database.vector_store.client import VectorStoreClient
from src.infrastructure.llm.client.ollama_client import LLMClient
from src.domain.orchestrator.router import EnterpriseQueryRouter

class TextModeApp:
    def __init__(self):
        print("🚀 Initializing Master Architect (Text Mode)...")
        self.vector_store = VectorStoreClient()
        self.llm_client = LLMClient()
        self.router = EnterpriseQueryRouter(self.vector_store, self.llm_client)
        print("✅ System Ready!")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        header = """
        ╔════════════════════════════════════════════════════════════════╗
        ║          🎓 MASTER ARCHITECT: TEXT-ONLY TURBO MODE             ║
        ║      (Type 'exit' to quit | Type 'h' for help)                 ║
        ╚════════════════════════════════════════════════════════════════╝
        """
        print(header)

    def run(self):
        self.clear_screen()
        self.print_header()
        
        while True:
            try:
                query = input("\n📝 Query > ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Happy Studying! Closing Master Architect...")
                    break
                
                if query.lower() == 'h':
                    self.show_help()
                    continue

                print("\n🔍 Analysing and Retrieving Content...")
                start_time = time.time()
                
                # Route query
                response = self.router.route(query)
                
                duration = time.time() - start_time
                
                # Print Response
                print("\n" + "═"*70)
                print(f"📖 MODE: {response.mode_name}")
                print("═"*70 + "\n")
                
                print(response.content)
                
                print("\n" + "═"*70)
                print(f"⚡ Time: {duration:.2f}s | Session Memory Active")
                print("═"*70)
                
                if "Shall we continue" in response.content or "?" in response.content[-100:]:
                    print("\n💡 [TURBO TIP] Just type 'yes' to move to the next page or segment!")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Use 'exit' to quit properly.")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

    def show_help(self):
        print("""
        📖 MASTER ARCHITECT COMMANDS:
        -----------------------------
        1. 'Explain page 5' -> NCERT Lossless Mode A
        2. 'Summarize segment 10:00 to 20:00' -> Transcript Mode
        3. 'yes' -> Automagically goes to the next page/segment (Turbo)
        4. 'exit' -> Close application
        """)

if __name__ == "__main__":
    app = TextModeApp()
    app.run()
