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
from src.audio.output_handler import AudioOutputHandler
from src.audio.vosk_detector import VoskInterruptDetector
from src.audio.whisper_transcriber import WhisperTranscriber


class GeminiAudioController:
    """
    Gemini-style conversation controller.
    
    Flow:
    1. Vosk monitors mic in background (always listening)
    2. User speaks → Vosk detects → stops TTS
    3. Whisper transcribes accurately
    4. AI responds
    5. TTS speaks (while Vosk still monitors)
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
        
        # Components
        self.tts = AudioOutputHandler()  # Natural female voice
        self.vosk = None  # Interrupt detector
        self.whisper = None  # Accurate transcriber
        
        # State
        self.is_speaking = False
        self.tts_thread = None
        self.interrupt_requested = False
        self.last_query = None
        self.last_response = None
        
        # Initialize Vosk (interrupt detection)
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'vosk-model-small-en-us-0.15')
            self.vosk = VoskInterruptDetector(model_path)
            self.logger.info("✓ Vosk interrupt detector ready")
        except Exception as e:
            self.logger.warning(f"Vosk not available: {e}")
        
        # Initialize Whisper (accurate transcription)
        try:
            self.whisper = WhisperTranscriber(model_size="tiny")
            self.logger.info("✓ Whisper transcriber ready")
        except Exception as e:
            self.logger.warning(f"Whisper not available: {e}")
    
    def _on_interrupt(self, detected_text: str):
        """Called when Vosk detects user speaking"""
        if self.is_speaking:
            self.logger.info(f"🛑 User interrupted! Stopping TTS...")
            self.interrupt_requested = True
            self.stop_speaking()
    
    def speak(self, text: str, interruptible: bool = True):
        """
        Speak text with optional interrupt monitoring.
        
        Args:
            text: Text to speak
            interruptible: If True, Vosk monitors for interrupts
        """
        self.interrupt_requested = False
        self.is_speaking = True
        
        # Start Vosk monitoring if enabled
        if interruptible and self.vosk:
            self.vosk.start_monitoring(self._on_interrupt)
        
        # Speak in thread so we can interrupt
        def speak_thread():
            try:
                self.tts.speak_with_tags(text)
            except Exception as e:
                self.logger.error(f"TTS error: {e}")
            finally:
                self.is_speaking = False
                if self.vosk:
                    self.vosk.stop_monitoring()
        
        self.tts_thread = threading.Thread(target=speak_thread, daemon=True)
        self.tts_thread.start()
        
        # Wait for completion or interrupt
        while self.is_speaking and not self.interrupt_requested:
            time.sleep(0.1)
    
    def stop_speaking(self):
        """Force stop TTS"""
        self.is_speaking = False
        self.tts.stop()
    
    def listen(self, prompt: str = "Listening...") -> str:
        """
        Listen for user input using Whisper.
        
        Returns:
            Transcribed text
        """
        if not self.whisper:
            self.logger.error("Whisper not available")
            return ""
        
        print(f"\n🎤 {prompt}")
        
        # Record and transcribe with Whisper
        text = self.whisper.record_and_transcribe(duration=5.0)
        
        if text:
            print(f"🗣️ You said: '{text}'")
            self.last_query = text
        
        return text
    
    def say(self, text: str):
        """Simple speak without tags"""
        self.tts.speak(text)
    
    def get_context(self) -> dict:
        """Get conversation context"""
        return {
            'last_query': self.last_query,
            'last_response': self.last_response
        }
