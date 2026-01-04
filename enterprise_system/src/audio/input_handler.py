"""
Audio Input Handler - Speech-to-Text
Captures voice commands and queries from microphone.
"""

import speech_recognition as sr
from typing import Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.logging.logger import LoggerFactory


class AudioInputHandler:
    """
    Handles speech-to-text input with command detection.
    
    Voice commands from ChatGPT conversation:
    - NEXT - Move forward
    - SIMPLER - Request simpler explanation
    - EXAMPLE - Add example
    - REPEAT - Replay section
    - TEST - Generate quiz
    - STOP - Pause audio
    """
    
    # Command vocabulary (fixed, from ChatGPT conversation)
    COMMANDS = ['next', 'simpler', 'example', 'repeat', 'test', 'stop']
    
    def __init__(self, timeout: int = 10, phrase_limit: int = 20):
        """
        Initialize speech recognition.
        
        Args:
            timeout: Max seconds to wait for speech
            phrase_limit: Max seconds for a phrase
        """
        self.logger = LoggerFactory.get_logger(__name__)
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.timeout = timeout
        self.phrase_limit = phrase_limit
        
        try:
            self.microphone = sr.Microphone()
            # We delay initialization/calibration to the listen() method 
            # so we don't hold the resource when not needed
            self.logger.info("Speech recognition initialized (Resource Safe Mode)")
        except Exception as e:
            self.logger.error(f"Failed to initialize microphone: {e}")
            
    def _calibrate(self):
        """Calibrate mic before listening"""
        if not self.microphone:
            return
            
        with self.microphone as source:
            self.logger.info("Calibrating...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Settings for patience/speed balance
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 300 
            self.recognizer.pause_threshold = 1.2
            self.recognizer.non_speaking_duration = 1.0

    def listen(self, prompt: str = "Listening...") -> Optional[str]:
        """
        Listen for user speech.
        Explicitly opens and closes mic resource.
        """
        if not self.microphone:
            return None
        
        print(f"\n🎤 {prompt}")
        
        try:
            # We re-calibrate briefly on each turn to ensure connection
            # This effectively "opens" the mic fresh each time
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_limit
                )
            
            # Mic is automatically closed here after 'with' block
            
            text = self.recognizer.recognize_google(audio)
            self.logger.info(f"Recognized: {text}")
            return text
            
        except Exception as e:
            # Log error but don't crash
            return None
        
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            print("⚠️ Could not understand. Please speak clearly.")
            return None
        
        except sr.RequestError as e:
            self.logger.error(f"Recognition service error: {e}")
            print("⚠️ Recognition service unavailable (need internet for Google API)")
            return None
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
    
    def detect_command(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if text contains a voice command.
        
        Args:
            text: Recognized speech text
            
        Returns:
            (is_command, command_name) tuple
        """
        if not text:
            return False, None
        
        text_lower = text.lower().strip()
        
        # Check for each command (keyword matching, no NLP)
        for command in self.COMMANDS:
            if command in text_lower:
                self.logger.info(f"Detected command: {command}")
                return True, command.upper()
        
        return False, None
    
    def listen_for_command(self) -> Optional[str]:
        """
        Listen specifically for a command.
        
        Returns:
            Command name or None
        """
        text = self.listen("Say a command (NEXT, SIMPLER, EXAMPLE, REPEAT, TEST, STOP)")
        
        if not text:
            return None
        
        is_command, command = self.detect_command(text)
        
        if is_command:
            return command
        else:
            # Not a command, return the text as a query
            return text
    
    def listen_for_query(self) -> Optional[str]:
        """
        Listen for a general query (page number, question, etc.)
        
        Returns:
            Query text or None
        """
        text = self.listen("Ask your question or say a page number")
        return text
