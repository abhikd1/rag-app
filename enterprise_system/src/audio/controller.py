"""
Audio Controller - Orchestrates audio input/output flow
Manages the hands-free voice interaction workflow.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.audio.output_handler import AudioOutputHandler
from src.audio.input_handler import AudioInputHandler
from src.core.logging.logger import LoggerFactory


class AudioController:
    """
    Manages the complete audio interaction flow.
    
    Workflow (from ChatGPT conversation):
    1. User speaks query
    2. STT converts to text
    3. App processes with enhanced prompts
    4. TTS reads output with tags
    5. User says command (NEXT, SIMPLER, etc.)
    6. Loop continues
    """
    
    def __init__(self):
        """Initialize audio components"""
        self.logger = LoggerFactory.get_logger(__name__)
        self.audio_output = AudioOutputHandler()
        self.audio_input = AudioInputHandler()
        self.current_response = None
        self.last_query = None
        
        self.logger.info("Audio controller initialized")
    
    def say(self, text: str):
        """Speak text (simple wrapper)"""
        self.audio_output.speak(text)
    
    def say_with_tags(self, tagged_text: str) -> bool:
        """
        Speak text with tag processing.
        
        Returns:
            True if needs to wait for input
        """
        return self.audio_output.speak_with_tags(tagged_text)
    
    def listen_for_query(self) -> str:
        """
        Listen for user query.
        
        Returns:
            Query text or None
        """
        return self.audio_input.listen_for_query()
    
    def listen_for_command(self) -> str:
        """
        Listen for voice command.
        
        Returns:
            Command (NEXT, SIMPLER, etc.) or query text
        """
        result = self.audio_input.listen_for_command()
        
        # EXPERIMENTAL FIX: Add small delay to ensure mic stream releases
        # before TTS engine tries to grab the audio device
        if result:
            import time
            time.sleep(0.5) 
            
        return result
    
    def process_command(self, command: str) -> dict:
        """
        Process a voice command and return action.
        
        Args:
            command: Command text (NEXT, SIMPLER, etc.)
            
        Returns:
            Dict with action details
        """
        command_upper = command.upper() if command else ""
        
        if command_upper == "NEXT":
            return {'action': 'next', 'message': 'Moving to next section...'}
        
        elif command_upper == "SIMPLER":
            return {'action': 'simplify', 'query': f"Explain this simpler: {self.last_query}"}
        
        elif command_upper == "EXAMPLE":
            return {'action': 'example', 'query': f"Give example for: {self.last_query}"}
        
        elif command_upper == "REPEAT":
            return {'action': 'repeat', 'response': self.current_response}
        
        elif command_upper == "TEST":
            return {'action': 'test', 'query': f"Test me on: {self.last_query}"}
        
        elif command_upper == "STOP":
            return {'action': 'stop', 'message': 'Stopping audio...'}
        
        else:
            # Not a command, treat as new query
            return {'action': 'query', 'query': command}
    
    def set_current_context(self, query: str, response: str):
        """Store current interaction context"""
        self.last_query = query
        self.current_response = response
    
    def stop(self):
        """Stop current audio"""
        self.audio_output.stop()
    
    def is_available(self) -> bool:
        """Check if audio features are available"""
        return (self.audio_output.engine is not None and 
                self.audio_input.microphone is not None)
    
    def get_status(self) -> dict:
        """Get audio system status"""
        return {
            'tts_available': self.audio_output.engine is not None,
            'stt_available': self.audio_input.microphone is not None,
            'speech_rate': self.audio_output.rate,
            'volume': self.audio_output.volume
        }
