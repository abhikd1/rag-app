"""
MASTER ARCHITECT: AUTONOMOUS PILOT (SONNET EDITION)
Executes a RAG mission from start to finish with zero user interaction.
"""
import sys
import os
import time
import msvcrt

# Force UTF-8 for high-end terminal visuals
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.infrastructure.database.vector_store.client import VectorStoreClient
from src.infrastructure.llm.client.ollama_client import LLMClient
from src.domain.orchestrator.router import EnterpriseQueryRouter

class AutonomousPilot:
    def __init__(self, document_target):
        print(f"🚀 MISSION ACTIVATED: {document_target}")
        self.vector_store = VectorStoreClient()
        self.llm_client = LLMClient()
        self.router = EnterpriseQueryRouter(self.vector_store, self.llm_client)
        self.target = document_target
        self.active = True

    def run(self, initial_query):
        current_query = initial_query
        print("\n" + "═"*80)
        print("🤖 [AUTONOMOUS MODE] ACTIVE. SYSTEM RUNNING UNTIL EOF.")
        print("🛑 PRESS 'Q' AT ANY TIME TO ABORT MISSION.")
        print("═"*80 + "\n")

        while self.active:
            # Check for manual interrupt
            if msvcrt.kbhit():
                key = msvcrt.getch().lower()
                if key == b'q':
                    print("\n\n🛑 ABORT SIGNAL RECEIVED. SHUTTING DOWN...")
                    break

            print(f"📡 EXECUTING: {current_query}")
            start_time = time.time()
            
            # Route and Execute
            response = self.router.route(current_query)
            duration = time.time() - start_time
            
            if not response.success:
                print(f"⚠️ MISSION HALTED: {response.content}")
                break

            # Print output to console for the user to see
            print("\n" + "─"*60)
            print(response.content)
            print("─"*60)
            print(f"📊 CHUNK COMPLETE | Time: {duration:.1f}s")

            # AUTOMATIC CONTINUATION (The 'Core' logic)
            # The Router already has the logic to increment pages/segments.
            # We just feed it 'yes' to trigger the next logical step.
            print("\n🦅 [PILOT] CALCULATING NEXT SEGMENT...")
            time.sleep(1) # Small delay for visual pacing
            current_query = "yes"
            
            # If the response indicates end of document, stop
            if " missione complete " in response.content.lower() or "end of transcript" in response.content.lower():
                print("\n✨ MISSION SUCCESS: End of Document Reached.")
                break

        print("\n🏁 Mission Termination Sequence Complete.")

if __name__ == "__main__":
    # Example starting point: Change this to whatever you want to start with
    # Mission: Transcript Summarization from 00:00
    pilot = AutonomousPilot("all transcript.txt")
    pilot.run("Summarize transcript from 00:00 to 10:00")
