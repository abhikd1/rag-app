"""
Gemini-Style Audio Controller
Integrates Vosk (interrupt), Whisper (accuracy), and natural TTS.
"""

import threading
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.logging.logger import LoggerFactory
from src.audio.interaction_engine import interaction_engine

class GeminiAudioController:
    """
    Gemini-style conversation controller.
    Delegates high-level logic to the InteractionEngine (State Machine).
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
        self.engine = interaction_engine
        
        try:
            self.engine.start() # Ignite the engine
        except Exception as e:
            self.logger.error(f"Engine Validation Failed: {e}")
            
    def speak(self, text: str, interruptible: bool = True):
        """Delegate to Engine"""
        self.engine.speak(text, interruptible=interruptible)
    
    def listen(self, prompt: str = "Listening...") -> str:
        """Delegate to Engine (Smart Listen)"""
        return self.engine.listen_smart(prompt)
    
    def say(self, text: str):
        """Simple speak"""
        self.engine.speak(text, interruptible=False)
        
    def stop_speaking(self):
        self.engine.audio_out.stop()
        
    def get_context(self) -> dict:
        return {'engine_state': self.engine.state.name}
