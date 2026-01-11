"""
Vosk-based interrupt detection for Gemini-style conversation.
Monitors microphone in background and detects when user starts speaking.
"""

import vosk
import sounddevice as sd
import queue
import json
import threading
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.logging.logger import LoggerFactory


class VoskInterruptDetector:
    """
    Lightweight speech detector using Vosk.
    Runs in background to detect when user starts speaking.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize Vosk detector.
        
        Args:
            model_path: Path to Vosk model (will auto-download if None)
        """
        self.logger = LoggerFactory.get_logger(__name__)
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.interrupt_callback = None
        self.listen_thread = None
        
        # Auto-download small model if not provided
        if model_path is None:
            model_path = self._get_or_download_model()
        
        try:
            self.logger.info(f"Loading Vosk model from: {model_path}")
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            self.recognizer.SetWords(True)
            self.logger.info("✓ Vosk interrupt detector initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Vosk: {e}")
    
    def _get_or_download_model(self) -> str:
        """Get or download Vosk small model"""
        model_dir = os.path.join(os.path.dirname(__file__), 'vosk-model-small-en-us-0.15')
        
        if os.path.exists(model_dir):
            return model_dir
        
        self.logger.info("Vosk model not found. Please download manually:")
        self.logger.info("1. Download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        self.logger.info(f"2. Extract to: {model_dir}")
        raise FileNotFoundError(f"Vosk model not found at {model_dir}")
    
    def start_monitoring(self, interrupt_callback):
        """
        Start background monitoring for speech.
        
        Args:
            interrupt_callback: Function to call when speech detected
        """
        if self.is_listening:
            return
        
        self.interrupt_callback = interrupt_callback
        self.is_listening = True
        
        # Start audio stream
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        
        self.logger.info("🎤 Vosk monitoring started (interrupt ready)")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=1.0)
        self.logger.info("Vosk monitoring stopped")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            self.logger.warning(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def _listen_loop(self):
        """Main listening loop (runs in background thread)"""
        try:
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self._audio_callback
            ):
                while self.is_listening:
                    try:
                        data = self.audio_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue
                    
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').strip()
                        
                        # Only interrupt for significant speech (filter noise/echo)
                        # Increased threshold to prevent self-interruption from TTS echo
                        if text and len(text) > 4 and self.interrupt_callback:
                            self.logger.info(f"🛑 Interrupt detected: '{text}'")
                            self.interrupt_callback(text)
                    
        except Exception as e:
            self.logger.error(f"Vosk listen loop error: {e}")
