import asyncio
import edge_tts
import sys
import os

# Suppress Pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time

# Standalone TTS script using Edge TTS (Best FREE Neural Voice)
# Voice: en-US-JennyNeural (Human-like female)

async def main():
    if len(sys.argv) < 2:
        return

    text = sys.argv[1]
    
    # Tunable parameters
    # rate like "+0%" or "-10%"
    # Revision Mode Default: +25% (Fast paced)
    rate_val = "+25%"
    if len(sys.argv) > 2:
        try:
            r = int(sys.argv[2])
            # strict mapping logic if passed explicitly
            if r < 140: rate_val = "+10%"
            elif r >= 140 and r < 160: rate_val = "+25%"
            elif r >= 160: rate_val = "+50%"
        except: pass
        
    voice = "en-US-JennyNeural" # High quality female neural
    output_file = os.path.join(os.path.dirname(__file__), "temp_speech.mp3")

    try:
        # 1. Generate Audio
        communicate = edge_tts.Communicate(text, voice, rate=rate_val)
        await communicate.save(output_file)
        
        # Ensure file exists and has size
        timeout = 0
        while not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            await asyncio.sleep(0.1)
            timeout += 1
            if timeout > 30: break # 3s timeout
            
        if not os.path.exists(output_file):
            return

        # 2. Play Audio
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
        except Exception as e:
            # If MP3 fails, it might be empty/corrupt
            pass
            
        # Stop and Unload
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
        # 3. Cleanup (Force delete with retry)
        for _ in range(3):
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
                break
            except:
                await asyncio.sleep(0.1)
        
    except Exception as e:
        print(f"EdgeTTS Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
