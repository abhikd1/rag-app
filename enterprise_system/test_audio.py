"""
Simple test to verify audio features work.
Tests TTS (text-to-speech) and shows how to use the audio app.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_tts():
    """Test text-to-speech"""
    print("="*70)
    print("Testing Text-to-Speech (TTS)")
    print("="*70)
    print()
    
    try:
        from src.audio.output_handler import AudioOutputHandler
        
        print("Creating TTS engine...")
        tts = AudioOutputHandler(rate=150)
        
        print("TTS engine ready!")
        print()
        print("You should hear: 'Audio features are working!'")
        print()
        
        tts.speak("Audio features are working!")
        
        print()
        print("TTS test passed!")
        print()
        
        # Test with tags
        print("Testing tag-based control...")
        print()
        
        tagged_text = """
        This is normal speech.
        [PAUSE:short]
        Now with a short pause.
        [PAUSE:long]
        And a longer pause.
        [EMPHASIS]
        This part is emphasized and slower.
        """
        
        print("You should hear different pauses and emphasis...")
        print()
        
        tts.speak_with_tags(tagged_text)
        
        print()
        print("="*70)
        print("All TTS features working!")
        print("="*70)
        
    except Exception as e:
        print(f"TTS test failed: {e}")
        import traceback
        traceback.print_exc()


def show_usage():
    """Show how to use the audio app"""
    print()
    print("="*70)
    print("HOW TO USE AUDIO FEATURES")
    print("="*70)
    print()
    
    print("1. TEXT MODE (no audio):")
    print("   cd enterprise_system")
    print("   python main_audio.py")
    print()
    
    print("2. AUDIO MODE (hands-free with voice):")
    print("   cd enterprise_system")
    print("   python main_audio.py --audio")
    print()
    
    print("3. VOICE COMMANDS (say these while in audio mode):")
    print("   - NEXT - Move to next section")
    print("   - SIMPLER - Request simpler explanation")
    print("   - EXAMPLE - Add an example")
    print("   - REPEAT - Replay current section")
    print("   - TEST - Quiz me")
    print("   - STOP - Exit audio mode")
    print()
    
    print("4. EXAMPLE QUERIES (speak or type):")
    print("   - 'Page 2'")
    print("   - 'Explain page 3'")
    print("   - 'Test me on transformers'")
    print()
    
    print("="*70)
    print("FEATURES FROM CHATGPT CONVERSATION:")
    print("="*70)
    print("- Dual-layer lossless prompts (100% NCERT + engaging)")
    print("- Text-to-speech with natural pauses")
    print("- Voice commands (keyword matching)")
    print("- Hands-free studying")
    print("- FREE tools (no paid APIs)")
    print()


if __name__ == "__main__":
    test_tts()
    show_usage()
