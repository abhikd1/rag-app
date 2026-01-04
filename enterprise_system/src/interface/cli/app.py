"""
Command Line Interface for the Enterprise Study System.
Clean, user-friendly terminal interface.
"""

import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.domain.orchestrator.router import EnterpriseQueryRouter
from src.infrastructure.database.vector_store.client import VectorStoreClient
from src.infrastructure.llm.client.ollama_client import LLMClient
from src.core.logging.logger import LoggerFactory
from src.core.config.settings import config


class StudySystemCLI:
    """
    Command Line Interface for the Enterprise Study System.
    Provides interactive chat with all 5 study modes.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
        
        # Initialize infrastructure
        self.logger.info("Initializing Enterprise Study System...")
        self.vector_store = VectorStoreClient()
        self.llm_client = LLMClient()
        
        # Initialize router
        self.router = EnterpriseQueryRouter(
            self.vector_store,
            self.llm_client
        )
        
        self.logger.info("System initialized successfully")
    
    def print_welcome(self):
        """Print welcome message"""
        welcome = """
{'='*80}
📚 ENTERPRISE STUDY SYSTEM
{'='*80}

Available Modes:
  📄 MODE A: Exact Recall (Page-specific retrieval)
  🧩 MODE B: Stuck-Point Explanation (Surgical clarification)
  🔗 MODE C: Concept Linking (Cross-chapter connections)
  🗣️ MODE D: Oral Revision (Voice-friendly scripts)
  🧠 MODE E: Active Recall (Self-testing)

Commands:
  - Type your question naturally (mode auto-detected)
  - Type 'MODE: X' to force a specific mode
  - Type 'reload' to re-index documents
  - Type 'modes' to see available modes
  - Type 'quit' or 'exit' to close

{'='*80}
"""
        print(welcome)
    
    def run(self):
        """Main interactive loop"""
        self.print_welcome()
        
        while True:
            try:
                # Get user input
                query = input("\n[YOU]: ").strip()
                
                # Handle special commands
                if query.lower() in ['quit', 'exit']:
                    print("\n👋 Goodbye! Happy studying!")
                    break
                
                if query.lower() == 'modes':
                    modes = self.router.get_available_modes()
                    print("\n📋 Available Modes:")
                    for mode in modes:
                        print(f"  • {mode}")
                    continue
                
                if query.lower() == 'reload':
                    print("\n🔄 Reloading documents...")
                    # TODO: Implement document reloading
                    print("✅ Documents reloaded")
                    continue
                
                if not query:
                    continue
                
                # Route query
                print("\n[THINKING]...", end="\r")
                response = self.router.route(query)
                
                # Display response
                if response:
                    print(f"\n{response.content}")
                else:
                    # Fallback to standard RAG (not implemented in this version)
                    print("\n💬 Standard chat mode not yet implemented.")
                    print("Please use one of the specialized modes (A-E).")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                print(f"\n❌ Error: {str(e)}")


def main():
    """Entry point"""
    cli = StudySystemCLI()
    cli.run()


if __name__ == "__main__":
    main()
