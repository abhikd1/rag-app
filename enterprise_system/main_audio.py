"""
Audio-Enabled RAG App - Main Entry Point
Supports both text and voice interaction.

Usage:
  python main_audio.py              # Text mode (default)
  python main_audio.py --audio      # Voice mode (hands-free)
  python main_audio.py --help       # Show options
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.infrastructure.database.vector_store.client import VectorStoreClient
from src.infrastructure.llm.client.ollama_client import LLMClient
from src.domain.orchestrator.router import EnterpriseQueryRouter
from src.audio.controller import AudioController
from src.core.logging.logger import LoggerFactory
from src.core.config.settings import config


class AudioEnabledRAGApp:
    """
    RAG Application with optional audio features.
    """
    
    def __init__(self, audio_mode: bool = False):
        """
        Initialize the RAG app.
        
        Args:
            audio_mode: If True, enable voice input/output
        """
        self.logger = LoggerFactory.get_logger(__name__)
        self.audio_mode = audio_mode
        self.audio_controller = None
        
        print("="*80)
        print("🚀 ENTERPRISE RAG STUDY SYSTEM")
        if audio_mode:
            print("🎤 Audio Mode - Voice Enabled")
        print("="*80)
        print()
        
        # Initialize components
        self.logger.info("Initializing components...")
        
        try:
            # Vector store
            self.vector_store = VectorStoreClient()  # Uses config internally
            
            # LLM client
            self.llm_client = LLMClient()
            
            # Query router
            self.router = EnterpriseQueryRouter(
                vector_store=self.vector_store,
                llm_client=self.llm_client
            )
            
            # Audio controller (if enabled)
            if audio_mode:
                self.audio_controller = AudioController()
                status = self.audio_controller.get_status()
                
                if not (status['tts_available'] and status['stt_available']):
                    print("⚠️ Warning: Audio features partially unavailable")
                    print(f"  TTS: {'✅' if status['tts_available'] else '❌'}")
                    print(f"  STT: {'✅' if status['stt_available'] else '❌'}")
                    print()
                else:
                    print("✅ Audio features ready!")
                    print(f"  Speech rate: {status['speech_rate']} WPM")
                    print(f"  Volume: {int(status['volume']*100)}%")
                    print()
            
            print("✅ System ready!")
            print()
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}", exc_info=True)
            print(f"❌ Error: {e}")
            print("\n💡 Make sure:")
            print("  1. Ollama is running: ollama serve")
            print("  2. Documents are indexed in chroma_db/")
            print("  3. For audio: microphone is connected")
            sys.exit(1)
    
    def run_text_mode(self):
        """Run in traditional text input/output mode"""
        print("📝 Text Mode")
        print("Type your queries (or 'quit' to exit)")
        print("Examples: 'Page 2', 'Explain page 3', 'MODE: A Page 5'")
        print("="*80)
        print()
        
        while True:
            try:
                # Get text input
                query = input("\n> ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                # Process query
                print("\n⚙️ Processing...")
                response = self.router.route(query)
                
                if response:
                    print(f"\n{response.content}\n")
                else:
                    print("\n⚠️ No specific mode matched. Try being more specific.\n")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error: {e}", exc_info=True)
                print(f"\n❌ Error: {e}\n")
    
    def run_audio_mode(self):
        """Run in voice-enabled hands-free mode"""
        if not self.audio_controller:
            print("❌ Audio mode not available")
            return
        
        print("🎤 Voice Mode - Hands-Free Learning")
        print()
        print("Voice Commands:")
        print("  • NEXT - Move to next section")
        print("  • SIMPLER - Request simpler explanation")
        print("  • EXAMPLE - Add an example")
        print("  • REPEAT - Repeat current section")
        print("  • TEST - Quiz me")
        print("  • STOP - Exit voice mode")
        print()
        print("="*80)
        print()
        
        self.audio_controller.say("Voice mode activated. What would you like to study?")
        
        while True:
            try:
                # Listen for query or command
                user_input = self.audio_controller.listen_for_command()
                
                if not user_input:
                    # If nothing heard, just loop back silently or verify availability
                    continue
                
                print(f"\n🗣️ You said: '{user_input}'")
                
                # Check for direct exit command first
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    self.audio_controller.say("Goodbye!")
                    break
                
                # Process command
                command_result = self.audio_controller.process_command(user_input)
                action = command_result.get('action')
                
                if action == 'stop':
                    self.audio_controller.say("Stopping. Goodbye!")
                    print("\n👋 Exiting voice mode")
                    break
                
                elif action == 'repeat':
                    # Repeat last response
                    if self.audio_controller.current_response:
                        print("\n🔁 Repeating...")
                        self.audio_controller.say_with_tags(
                            self.audio_controller.current_response
                        )
                    else:
                        self.audio_controller.say("Nothing to repeat yet.")
                
                elif action in ['query', 'simplify', 'example', 'test']:
                    # Process as query
                    query = command_result.get('query', user_input)
                    print(f"\n🔍 Query: {query}")
                    
                    # Route and process
                    response = self.router.route(query)
                    
                    if response and response.success:
                        # Store context
                        self.audio_controller.set_current_context(query, response.content)
                        
                        # Display text
                        print(f"\n{response.content}\n")
                        
                        # Speak with tag processing
                        needs_input = self.audio_controller.say_with_tags(response.content)
                        
                        if needs_input:
                            # [WAIT] tag encountered, listen for response
                            continue
                    else:
                        msg = "No matching content found. Try another query."
                        print(f"\n⚠️ {msg}\n")
                        self.audio_controller.say(msg)
                
                elif action == 'next':
                    self.audio_controller.say(command_result.get('message'))
                    # TODO: Implement section navigation
                
            except KeyboardInterrupt:
                print("\n\n👋 Exiting voice mode")
                self.audio_controller.say("Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error in audio mode: {e}", exc_info=True)
                print(f"\n❌ Error: {e}\n")
    
    def run(self):
        """Run the appropriate mode"""
        if self.audio_mode:
            self.run_audio_mode()
        else:
            self.run_text_mode()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Audio-Enabled RAG Study System"
    )
    parser.add_argument(
        '--audio',
        action='store_true',
        help='Enable audio mode (voice input/output)'
    )
    parser.add_argument(
        '--rate',
        type=int,
        default=150,
        help='Speech rate in words per minute (default: 150)'
    )
    
    args = parser.parse_args()
    
    # Create and run app
    app = AudioEnabledRAGApp(audio_mode=args.audio)
    app.run()


if __name__ == "__main__":
    main()
