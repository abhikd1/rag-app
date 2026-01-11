"""
Advanced Interaction Engine
Implements a Full-Duplex Conversational State Machine.
Handles: Turn-taking, Input Aggregation, Smart Interrupts, and Self-Healing.
"""

import time
import threading
import queue
import re
from enum import Enum, auto
from typing import Optional, Callable, Dict

from src.core.logging.logger import LoggerFactory
from src.audio.async_engine import engine as audio_engine
from src.audio.vosk_detector import VoskInterruptDetector
from src.audio.whisper_transcriber import WhisperTranscriber

class InteractionState(Enum):
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    SPEAKING = auto()
    PAUSED = auto()  # User is thinking (brief silence)
    INTERRUPTED = auto()

class InteractionEngine:
    """
    The Brain of the Audio System.
    Manages the flow of conversation using a sophisticated state machine.
    """
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
        
        # --- SUB-SYSTEMS ---
        self.audio_out = audio_engine
        self.transcriber = WhisperTranscriber(model_size="tiny") # Google fallback
        # Delay Vosk init to ensure thread safety during complex startups
        self.vosk_path = self._get_vosk_path()
        self.detector = None # Lazy loaded
        
        # --- STATE MACHINE ---
        self.state = InteractionState.IDLE
        self.state_lock = threading.Lock()
        
        # --- INPUT BUFFERING ---
        self.speech_buffer = []
        self.last_speech_time = 0
        self.silence_threshold = 1.2  # Seconds to wait before deciding "User is done"
        
        # --- EVENTS & QUEUES ---
        self.input_queue = queue.Queue()
        self.interrupt_event = threading.Event()
        self.shutdown_event = threading.Event()

        # --- SMART THRESHOLDS ---
        self.min_query_length = 5
        self.ignore_phrases = {'ok', 'okay', 'yes', 'yep', 'uh-huh', 'right'}

        self.logger.info("🧠 Interaction Engine Initialized (State Machine Ready)")

    def _get_vosk_path(self):
        import os
        return os.path.join(os.path.dirname(__file__), 'vosk-model-small-en-us-0.15')

    def start(self):
        """Ignition sequence"""
        self.detector = VoskInterruptDetector(self.vosk_path)
        
        # Start the background state monitor
        self.monitor_thread = threading.Thread(target=self._state_monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("🚀 Engine Started. Entering Full-Duplex Mode.")

    def _transition(self, new_state: InteractionState):
        """Safe state transition"""
        with self.state_lock:
            if self.state != new_state:
                self.logger.debug(f"State Transition: {self.state.name} -> {new_state.name}")
                self.state = new_state

    def speak(self, text: str, interruptible: bool = True):
        """
        Output speech with interrupt capability.
        """
        self._transition(InteractionState.SPEAKING)
        self.interrupt_event.clear()
        
        # 1. Start Interrupt Monitor
        if interruptible:
            self.detector.start_monitoring(self._handle_barge_in)
            
        # 2. Add to Audio Queue (Async Engine)
        self.audio_out.speak(text)
        
        # 3. Wait for playback to finish (or interrupt)
        while not self.audio_out.queue.empty() or self.audio_out.is_playing:
            if self.interrupt_event.is_set():
                self.logger.info("🛑 Playback aborted by interrupt")
                break
            time.sleep(0.1)
            
        # 4. Cleanup
        if interruptible:
            self.detector.stop_monitoring()
            
        if not self.interrupt_event.is_set():
            self._transition(InteractionState.IDLE)

    def _handle_barge_in(self, text: str):
        """
        Callback for Vosk Interrupts.
        Decides whether to kill audio or ignore.
        """
        text = text.lower().strip()
        
        # Filter Ignored Phrases (Backchanneling)
        if text in self.ignore_phrases:
            return
            
        # Filter Short Noise
        if len(text) < 4:
            return
            
        # VALID INTERRUPT
        self.logger.info(f"⚡ Barge-In Detected: '{text}'")
        self.audio_out.stop() # Kill Audio Instantly
        self.interrupt_event.set()
        self._transition(InteractionState.INTERRUPTED)
        
        # We immediately queue a listen task to capture the FULL command
        # Logic: If they interrupted, they have something to say right now.
        # But we don't want to use the 'text' from Vosk (it's partial).
        # We trigger the main loop to listen properly.

    def listen_smart(self, prompt: str = "Listening...") -> Optional[str]:
        """
        Smart Listening with Input Aggregation.
        Handles pauses and hesitations gracefully.
        """
        self._transition(InteractionState.LISTENING)
        print(f"\n🎤 {prompt}")
        
        full_query = ""
        
        # Attempt 1: Listen
        fragment = self.transcriber.record_and_transcribe(duration=5.0)
        if not fragment:
            self._transition(InteractionState.IDLE)
            return None
            
        full_query += " " + fragment
        
        # Smart Logic: Check if user is unfinished
        # (Heuristic: Ends with 'and', 'so', 'because', or very short)
        if self._needs_continuation(fragment):
            print("   (Listening for more...)")
            fragment2 = self.transcriber.record_and_transcribe(duration=3.0)
            if fragment2:
                full_query += " " + fragment2
                
        final_text = full_query.strip()
        
        # --- LOCAL COMMAND INTERCEPTION ---
        # Handle speed/system commands locally without hitting LLM
        lower_text = final_text.lower()
        if 'faster' in lower_text or 'speed up' in lower_text:
            print(">> Adjusting Speed: FASTER 🐇")
            self.audio_out.set_speed('faster')
            self.audio_out.speak("Ok, speaking faster.")
            return None # Don't send to LLM
            
        if 'slower' in lower_text or 'slow down' in lower_text:
            print(">> Adjusting Speed: SLOWER 🐢")
            self.audio_out.set_speed('normal')
            self.audio_out.speak("Ok, slowing down.")
            return None
            
        if 'insane mode' in lower_text:
            print(">> Adjusting Speed: INSANE 🔥")
            self.audio_out.set_speed('insane')
            self.audio_out.speak("Buckle up!")
            return None
        # ----------------------------------
        
        if final_text:
            print(f"🗣️ You said: '{final_text}'")
            self._transition(InteractionState.PROCESSING)
            return final_text
        
        self._transition(InteractionState.IDLE)
        return None

    def _needs_continuation(self, text: str) -> bool:
        """Hueristic to see if user sentence is incomplete"""
        text = text.lower().strip()
        if not text: return False
        
        connectors = ['and', 'but', 'so', 'because', 'then', 'if', 'when']
        if any(text.endswith(c) for c in connectors):
            return True
        
        # If text is extremely short, might be a partial capture
        if len(text.split()) < 3:
            return True
            
        return False

    def _state_monitor_loop(self):
        """Background thread to keep engine healthy"""
        while not self.shutdown_event.is_set():
            # Future: Check for frozen threads or audio deadlocks here
            time.sleep(1.0)

    def shutdown(self):
        self.shutdown_event.set()
        self.audio_out.stop()

# Instantiate the engine
interaction_engine = InteractionEngine()
