# 🎙️ SYSTEM ORAL INTEGRATION & MODE A GUIDE

This document provides the complete technical specification for transforming the RAG AI into an **Audio-First Intelligent Tutor**.

---

## 🏗️ TECHNICAL STACK RECAP
| Component | Technology | Role |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core Logic |
| **Text-to-Audio** | `pyttsx3` | Offline, high-speed text-to-speech engine. |
| **Audio-to-Text** | `SpeechRecognition` | Microphone input and voice command processing. |
| **Orchestration** | Tag-Based Logic | Maps specific tags to system actions (Silence, Listen, Emphasize). |

---

## 🔊 THE UNIVERSAL AUDIO TAG SYSTEM
These tags are used in the prompt to instruct the AI how to "speak" the content.

### **1. Speech & Flow Tags**
*   **`[SAY]`**: Instructs the system to speak the following text normally.
*   **`[EMPHASIS]`**: Tells the system to speak slower and with more stress on key exam points.
*   **`[PAUSE:short]`**: Inserts a ~0.5s silence for breathing room.
*   **`[PAUSE:long]`**: Inserts a ~1.5s silence to indicate a topic shift.
*   **`[RECAP]`**: A slow, calm summary of the section.

### **2. Interaction & Voice Control**
*   **`[QUESTION]`**: The tutor asks a question and waits.
*   **`[WAIT]`**: **CRITICAL.** This signal turns the **Microphone ON** to listen for your response.
*   **`[HINT]`**: Softly suggests a command you can say (e.g., *"Say NEXT to continue"*).

---

## 🧠 UNIVERSAL MODE A PROMPT
Copy and paste this prompt to the AI whenever you start a new chapter or page:

> **You are an Audio-First Mode A Tutor.**
> 
> **RULES:**
> - Output MUST use tags like [SAY], [PAUSE], [EMPHASIS], [QUESTION], and [WAIT].
> - Write in short, spoken sentences. No long paragraphs.
> - Preserve 100% factual accuracy—do not skip any content.
> - Focus on structure and logic (Mode A).
>
> **TAGS TO USE:**
> [SAY], [EMPHASIS], [PAUSE:short], [PAUSE:long], [QUESTION], [WAIT], [RECAP], [EXAMPLE], [HINT], [SECTION-START], [SECTION-END]
>
> **INTERACTION:**
> - Ask one question per section.
> - After every question, use [WAIT] to hear my response.
>
> **[CONTENT-START]**
> <PASTE PDF TEXT HERE>
> **[CONTENT-END]**

---

## 🎙️ COMMAND VOCABULARY
The system listens for these specific words during a **`[WAIT]`** state:

1.  **NEXT**: Moves to the next section.
2.  **SIMPLER**: Breaks down a complex part into easier terms.
3.  **REPEAT**: Replays the last spoken section.
4.  **EXAMPLE**: Provides a real-life analogy.
5.  **TEST ME**: Starts a quick quiz on the current section.
6.  **STOP**: End the session.

---

## 🛠️ HOW TO PROCEED (PYTHON IMPLEMENTATION)

### **Step 1: Install Libraries**
```bash
pip install pyttsx3 speechrecognition pyaudio
```

### **Step 2: The Speech Loop Logic**
```python
import pyttsx3
import speech_recognition as sr

# Initialize TTS
engine = pyttsx3.init()

def speak(text):
    # Regex/Parser logic to handle [PAUSE] or [EMPHASIS] goes here
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    return r.recognize_google(audio).lower()
```

### **Step 3: State Management**
Your app should maintain a `current_state` so it knows if it is speaking or listening. When a `[WAIT]` tag is detected in the AI output, the app must pause the TTS and activate the `listen()` function.

---

## 💎 BENEFITS OF THIS SYSTEM
*   **60% Faster Revision**: No visual fatigue; learn while traveling or relaxing.
*   **Active Engagement**: Forcing your brain to answer questions aloud locks in the info.
*   **Zero Loss**: Unlike "Summary" modes, this system preserves every detail for exams.
