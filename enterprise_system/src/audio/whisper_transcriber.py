"""
Google-based accurate transcription (Replacement for Whisper).
Used AFTER Vosk detects speech for high-accuracy conversion.
Switched to Google API because Whisper requires FFmpeg which is missing.
"""

import speech_recognition as sr
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.logging.logger import LoggerFactory


class WhisperTranscriber:
    """
    High-accuracy speech transcription using Google Speech Recognition.
    (Kept class name 'WhisperTranscriber' for compatibility with controller)
    """
    
    def __init__(self, model_size: str = "tiny"):
        """
        Initialize Google Recognizer.
        """
        self.logger = LoggerFactory.get_logger(__name__)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        try:
            # Calibrate slightly on init
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.logger.info(f"✓ Google Speech Recognizer ready (Fallback for Whisper)")
        except Exception as e:
            self.logger.error(f"Failed to load SpeechRecognizer: {e}")
    
    def record_and_transcribe(self, duration: float = 5.0, sample_rate: int = 16000) -> str:
        """
        Record audio from mic and transcribe using Google API.
        
        Args:
            duration: Max recording duration (soft limit)
            
        Returns:
            Transcribed text
        """
        try:
            self.logger.info(f"🎤 Listening for command...")
            
            with self.microphone as source:
                # Listen with a timeout
                audio = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=10.0)
            
            self.logger.info("Processing speech...")
            # Transcribe
            text = self.recognizer.recognize_google(audio)
            
            self.logger.info(f"📝 Transcribed: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return "" # Speech unintelligible
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return ""
