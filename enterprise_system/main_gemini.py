"""
Gemini-Style RAG Study System
Natural conversation with interrupt capability.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.core.config.settings import config
from src.core.logging.logger import LoggerFactory
from src.infrastructure.database.vector_store.client import VectorStoreClient
from src.infrastructure.llm.client.ollama_client import LLMClient
from src.domain.orchestrator.router import EnterpriseQueryRouter
from src.audio.gemini_controller import GeminiAudioController


class GeminiRAGApp:
    """RAG Study System with Gemini-style voice interaction"""
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
        
        print("="*80)
        print("🎓 GEMINI-STYLE RAG STUDY SYSTEM")
        print("🎤 Natural Voice | Interrupt Anytime | Female Voice")
        print("="*80)
        print()
        
        self.logger.info("Initializing components...")
        
        try:
            # Core components
            self.vector_store = VectorStoreClient()
            self.llm_client = LLMClient()
            self.router = EnterpriseQueryRouter(
                vector_store=self.vector_store,
                llm_client=self.llm_client
            )
            
            # Gemini-style audio controller
            self.audio = GeminiAudioController()
            
            self.logger.info("✓ System ready!")
            print("✓ System ready!")
            print()
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", exc_info=True)
            print(f"❌ Error: {e}")
            print()
            print("💡 Make sure:")
            print("  1. Ollama is running: ollama serve")
            print("  2. Documents are indexed in chroma_db/")
            print("  3. Vosk model is downloaded")
            raise
    
    def run(self):
        """Run Gemini-style conversation loop"""
        
        # Welcome message
        self.audio.say("Hello! I'm your study assistant. What would you like to learn today?")
        
        print("🎯 Gemini-Style Interaction:")
        print("  • Just start speaking - I'm always listening")
        print("  • Interrupt me anytime by talking")
        print("  • Say 'stop' or 'exit' to quit")
        print()
        
        while True:
            try:
                # Listen for query (Whisper)
                user_input = self.audio.listen("Ready to listen...")
                
                if not user_input:
                    continue
                
                # Check for exit
                if user_input.lower() in ['stop', 'exit', 'quit', 'bye', 'goodbye']:
                    self.audio.say("Goodbye! Happy studying!")
                    break
                
                # Process query
                print(f"\n🔍 Processing: {user_input}")
                response = self.router.route(user_input)
                
                if response and response.success:
                    # Speak response (interruptible by Vosk)
                    self.audio.speak(response.content, interruptible=True)
                    
                    # Store context
                    self.audio.last_response = response.content
                else:
                    self.audio.say("I couldn't find information on that. Try asking about a specific page or topic.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user")
                self.audio.say("Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error in conversation loop: {e}", exc_info=True)
                self.audio.say("Sorry, I encountered an error. Let's try again.")


def main():
    parser = argparse.ArgumentParser(description="Gemini-Style RAG Study System")
    args = parser.parse_args()
    
    try:
        app = GeminiRAGApp()
        app.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
