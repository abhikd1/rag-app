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

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from src.domain.orchestrator.router import EnterpriseQueryRouter
from src.infrastructure.database.vector_store.client import VectorStoreClient
from src.infrastructure.llm.client.ollama_client import LLMClient
from src.core.logging.logger import LoggerFactory
from src.core.config.settings import config

console = Console()

class StudySystemCLI:
    """
    Command Line Interface for the Enterprise Study System.
    Provides interactive chat with all 5 study modes.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
        
        # Initialize infrastructure
        self.logger.info("Initializing Enterprise Study System...")
        console.rule("[bold cyan]Initializing Enterprise Study System[/bold cyan]")
        
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
        welcome_text = """
# 📚 ENTERPRISE STUDY SYSTEM  
### *Advanced RAG For Specialized Learning*

**Available Modes:**
- 📄 **MODE A: Exact Recall** (Page-specific retrieval)
- 🧩 **MODE B: Stuck-Point Explanation** (Surgical clarification)
- 🔗 **MODE C: Concept Linking** (Cross-chapter connections)
- 🗣️ **MODE D: Oral Revision** (Voice-friendly scripts)
- 🧠 **MODE E: Active Recall** (Self-testing)

**Quick Commands:**
- Type your question naturally (Auto-detected).
- `quit` or `exit` to close.
"""
        console.print(Panel(Markdown(welcome_text), border_style="cyan", title="Welcome"))
    
    def run(self):
        """Main interactive loop"""
        self.print_welcome()
        
        while True:
            try:
                # Get user input
                query = Prompt.ask("\n[bold green]YOU[/bold green]")
                
                # Handle special commands
                if query.lower() in ['quit', 'exit']:
                    console.print("\n[bold yellow]👋 Goodbye! Happy studying![/bold yellow]")
                    break
                
                if query.lower() == 'modes':
                    modes = self.router.get_available_modes()
                    console.print("\n[bold cyan]📋 Available Modes:[/bold cyan]")
                    for mode in modes:
                        console.print(f"  • {mode}")
                    continue
                
                if not query:
                    continue
                
                # Route query
                with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
                    response = self.router.route(query)
                
                # Display response
                if response:
                    console.print("\n")
                    console.print(Panel(Markdown(response.content), title="🤖 AI Assistant", border_style="purple"))
                else:
                    console.print("[bold red]Standard chat mode not yet implemented. Please try a specific query.[/bold red]")
                
            except KeyboardInterrupt:
                console.print("\n\n[bold yellow]👋 Interrupted. Goodbye![/bold yellow]")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")


def main():
    """Entry point"""
    cli = StudySystemCLI()
    cli.run()


if __name__ == "__main__":
    main()
