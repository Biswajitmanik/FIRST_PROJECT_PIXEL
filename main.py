import speech_recognition as sr
import webbrowser
import requests
from openai import OpenAI
from gtts import gTTS
import pygame, os, time, uuid, traceback

# === Setup ===
recognizer = sr.Recognizer()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# API keys
NEWS_API = "YOUR_NEWS_API_KEY_HERE"
OPENAI_API = "YOUR_OPENAI_API_KEY_HERE"

# Chrome path
CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"

# Wake word variations
WAKE_WORDS = {"pixel", "pic-cell", "pic-cel", "pix-el", "pixal"}

# Noise/filler words
FILLER_WORDS = {"um", "uh", "ah", "ok", "okay", "hmm", "mm", "yeah", "right"}

# === Speak function ===
def speak(text):
    try:
        filename = f"temp_{uuid.uuid4().hex}.mp3"
        tts = gTTS(text)
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
        time.sleep(0.1)
        os.remove(filename)
    except Exception as e:
        print("Speak error:", e)

# === AI function ===
def aiProcess(command):
    try:
        client = OpenAI(api_key=OPENAI_API)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful virtual assistant named Pixel. Keep answers short and clear."},
                {"role": "user", "content": command},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("AI error:", e)
        traceback.print_exc()
        return "Sorry, I couldn't process that."

# === Command handling ===
def processCommand(c):
    command_words = c.lower().split()
    if all(word in FILLER_WORDS for word in command_words) or len(command_words) < 2:
        print(f"Ignored noise/filler: {c}")
        return

    print("Command received:")
    for w in command_words:
        print(w)

    # Websites
    sites = {
        "google": "https://google.com",
        "youtube": "https://youtube.com",
        "facebook": "https://facebook.com",
        "linkedin": "https://linkedin.com",
        "github": "https://github.com",
        "instagram": "https://instagram.com",
        "amazon": "https://amazon.com",
        "flipkart": "https://flipkart.com",
        "twitter": "https://twitter.com",
    }

    for site in sites:
        if site in c.lower():
            try:
                webbrowser.get(CHROME_PATH).open(sites[site])
                speak(f"Opening {site}")
            except Exception as e:
                print("Browser error:", e)
                speak(f"Sorry, I couldn’t open {site}")
            return

    # News
    if "news" in c.lower():
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API}")
            if r.status_code == 200:
                for article in r.json().get("articles", [])[:3]:
                    speak(article["title"])
            else:
                speak("Sorry, I can’t fetch the news right now.")
        except Exception as e:
            print("News error:", e)
            speak("Could not fetch news.")
        return

    # AI fallback
    speak(aiProcess(c))

# === Main loop ===
if __name__ == "__main__":
    speak("Initialization PIXEL...")

    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

            try:
                text = recognizer.recognize_google(audio).strip().lower()
                print("You said:", text)
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                speak("Speech recognition service unavailable.")
                continue

            # Check if wake word is in the text
            if any(word in text for word in WAKE_WORDS):
                speak("Sir, how can I assist you?")
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("Pixel active, listening for command...")
                    try:
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                        command = recognizer.recognize_google(audio).strip()
                        if command:
                            processCommand(command)
                    except sr.UnknownValueError:
                        speak("Sorry, I didn't catch that.")
                    except sr.RequestError:
                        speak("Speech recognition service unavailable.")

        except Exception as e:
            print("Main loop error:", e)
            traceback.print_exc()
