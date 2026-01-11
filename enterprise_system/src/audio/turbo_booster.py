"""
Advanced Turbo Booster (V3.0) - Auto-Study Mode
Automatically types 'yes' to continue study sessions unless interrupted.
"""
import msvcrt
import time

class TurboBooster:
    def __init__(self, controller):
        self.controller = controller
        self.auto_play = True  # Default to YES continuation
        self.triggers = [
            "shall we continue", "ready for", "continue to", "move on",
            "next part", "would you like", "proceed", "go to", "ready?"
        ]

    def process_and_listen(self, last_response: str) -> str:
        """
        Decision engine for Auto-Continuation.
        """
        # 1. Manual Interrupt Check
        if msvcrt.kbhit():
            key = msvcrt.getch().lower()
            if key == b's':
                print("\n🛑 [TURBO] PAUSED. Switching to Human Mode.")
                self.auto_play = False
                return self.controller.listen("User in control...")
            elif key == b't':
                self.auto_play = True
                print("\n🔥 [TURBO] RESUMED. Auto-Pilot active.")

        # 2. Logic for Auto-Continuation
        if self.auto_play and last_response:
            # Check the tail of the message for question marks or continuation keywords
            tail = last_response[-200:].lower()
            needs_continue = any(t in tail for t in self.triggers) or '?' in tail
            
            if needs_continue:
                print("\n" + "🚀"*10)
                print("🦅 [TURBO PILOT] AUTO-YES DETECTED!")
                print("🦅 ACTION: Pressing 'YES' to continue study flow.")
                print("🚀"*10 + "\n")
                
                # Auditory cue
                self.controller.say("Next part.")
                time.sleep(0.5)
                
                return "yes"

        # 3. Default Listen
        prompt = "🎤 Studying... (Auto-Pilot ON)" if self.auto_play else "🎤 Waiting for you..."
        return self.controller.listen(prompt)

    def set_auto(self, status: bool):
        self.auto_play = status
        mode = "AUTO" if status else "MANUAL"
        print(f"⚙️ Booster Mode: {mode}")
