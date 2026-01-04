"""
Audio Output Handler - Text-to-Speech
Converts tagged text responses into spoken audio with proper pauses and emphasis.
"""

import pyttsx3
import time
import re
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.logging.logger import LoggerFactory


class AudioOutputHandler:
    """
    Handles text-to-speech output with tag-based audio control.
    
    Supported tags from ChatGPT conversation:
    - [SAY] - Normal speech
    - [PAUSE:short] - 0.5s pause
    - [PAUSE:long] - 1.5s pause
    - [EMPHASIS] - Slower, stressed speech
    - [QUESTION] - Ask user, prepare to listen
    - [WAIT] - Stop and listen for input
    - [RECAP] - Calm summary tone
    - [EXAMPLE] - Friendly tone
    """
    
    def __init__(self, rate: int = 130, volume: float = 0.80):
        """
        Initialize TTS engine with Microsoft Aria (female, natural voice).
        Optimized for maximum naturalness and long listening sessions.
        
        Args:
            rate: Speech rate (130 = very natural, conversational)
            volume: Volume level (0.80 = gentle on ears)
        """
        self.logger = LoggerFactory.get_logger(__name__)
        self.engine = None
        self.rate = rate
        self.volume = volume
        self.is_speaking = False
        self.tts_thread = None
        
        try:
            # Force Windows SAPI5 driver
            self.engine = pyttsx3.init(driverName='sapi5')
            
            # Find and set any female voice (Zira, Aria, Eva, etc.)
            voices = self.engine.getProperty('voices')
            female_voice = None
            
            print("\n🎤 Available Voices on your System:")
            for v in voices:
                print(f"  - {v.name} ({v.id})")
                if 'zira' in v.name.lower():
                    female_voice = v
                elif 'aria' in v.name.lower():
                    female_voice = v # Prefer Aria if found
                elif 'eva' in v.name.lower() and not female_voice:
                    female_voice = v
            
            if female_voice:
                self.engine.setProperty('voice', female_voice.id)
                self.logger.info(f"✓ Using Female Voice: {female_voice.name}")
                print(f"✅ Selected Voice: {female_voice.name}")
            else:
                self.logger.warning("⚠ No specific female voice found, using default")
                print("⚠ No female voice found (Zira/Aria). Using default.")
            
            # Optimized settings for natural female voice
            self.engine.setProperty('rate', rate)  # Slower = more natural
            self.engine.setProperty('volume', volume)  # Gentle volume
            
            self.logger.info(f"TTS initialized (Natural Female, rate={rate}, volume={volume})")
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {e}")
    
    def speak(self, text: str, wait: bool = True):
        """
        Speak using a separate subprocess to guarantee audio isolation.
        """
        # Clean text first (remove ===, ---, etc.)
        speech_text = self._clean_for_audio(text)
        
        import subprocess
        import os
        
        script_path = os.path.join(os.path.dirname(__file__), 'speak.py')
        
        try:
            print(f"🔊 Speaking: {speech_text[:50]}...")
            subprocess.run(
                [sys.executable, script_path, speech_text, str(self.rate), str(self.volume)],
                check=False
            )
        except Exception as e:
            self.logger.error(f"Speech error: {e}")

    def _clean_for_audio(self, text: str) -> str:
        """
        Aggressively clean text for audio output.
        Removes markdown, emojis, and visual symbols.
        """
        # 1. Remove Emojis (Regex for common emoji ranges)
        import re
        # This matches most emoji characters
        clean = re.sub(r'[^\x00-\x7F]+', '', text)
        
        # 2. Remove Markdown Headers (### Title -> Title)
        clean = re.sub(r'#+\s*', '', clean)
        
        # 3. Remove Bold/Italic stars/underscores (*text* -> text)
        clean = re.sub(r'[\*_`]', '', clean)
        
        # 4. Remove Visual Separators (===, ---)
        clean = re.sub(r'[=\-]{3,}', ' ', clean)
        
        # 5. Remove Bullets that sound weird (-, >)
        # We replace them with a pause or just space
        clean = re.sub(r'^\s*[-•>]\s*', '', clean, flags=re.MULTILINE)
        
        # 6. Normalize whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def speak_with_tags(self, tagged_text: str) -> bool:
        """
        Process text with tags and speak with proper pauses and emphasis.
        """
        # Engine is created locally in self.speak(), so no check needed here
        
        # Split by lines to process tags
        lines = tagged_text.split('\n')
        
        # Buffering logic for smooth speech
        buffer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for control tags (Wait, Pause, Emphasis)
            # These require breaking the flow
            is_special = any(tag in line for tag in ['[PAUSE', '[WAIT]', '[EMPHASIS]', '[QUESTION]'])
            
            if is_special:
                # 1. Flush existing buffer first (Speak what we have smoothly)
                if buffer:
                    combined_text = " ".join(buffer)
                    print(combined_text) # Show on console as requested
                    self.speak(combined_text)
                    buffer = []
                
                # 2. Handle the special line
                if '[WAIT]' in line:
                    self.logger.info("Reached [WAIT] tag")
                    return True
                elif '[PAUSE' in line:
                    time.sleep(0.5)
                else:
                    # Speak special line individually
                    clean_text = self._remove_tags(line)
                    if clean_text:
                        print(clean_text)
                        self.speak(clean_text)
            else:
                # Normal text - add to buffer
                clean_text = self._remove_tags(line)
                if clean_text:
                    buffer.append(clean_text)
        
        # Flush remaining buffer
        if buffer:
            combined_text = " ".join(buffer)
            print(combined_text)
            self.speak(combined_text)
            
        return False
    
    def _remove_tags(self, text: str) -> str:
        """Remove all control tags from text"""
        tags = [
            r'\[SAY\]',
            r'\[PAUSE:short\]',
            r'\[PAUSE:long\]',
            r'\[EMPHASIS\]',
            r'\[QUESTION\]',
            r'\[WAIT\]',
            r'\[RECAP\]',
            r'\[EXAMPLE\]',
            r'\[TEST\]',
            r'\[SECTION-START\]',
            r'\[SECTION-END\]',
            r'\[HINT\]',
            r'\[COMMAND\]'
        ]
        
        clean = text
        for tag in tags:
            clean = re.sub(tag, '', clean)
        
        return clean.strip()
    
    def stop(self):
        """Stop current speech"""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
            except Exception as e:
                self.logger.error(f"Error stopping speech: {e}")
    
    def set_rate(self, rate: int):
        """Change speech rate"""
        if self.engine:
            self.engine.setProperty('rate', rate)
            self.rate = rate
    
    def set_volume(self, volume: float):
        """Change volume (0.0 to 1.0)"""
        if self.engine:
            self.engine.setProperty('volume', volume)
            self.volume = volume
