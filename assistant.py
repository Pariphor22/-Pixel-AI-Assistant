import os
from urllib import response
from google import genai
from openai import models
import requests
import pyttsx3
import webbrowser
import speech_recognition as sr
import threading
from ddgs import DDGS
from tqdm import gui
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

print("ENV file exists:", env_path.exists())
print("Gemini key loaded:", bool(os.getenv("gemini_api_key")))


load_dotenv()
Gemini_api_key = os.getenv("gemini_api_key")
News_api_key = os.getenv("news_api_key")

if not Gemini_api_key:
    raise ValueError("gemini_api_key not found in .env file.")

client = genai.Client(api_key=Gemini_api_key)

try:
    import musics
except ImportError:
    musics = None  # Fallback if musics module isn't created
   



try:
    print("1. Starting...")

    client = genai.Client(api_key=Gemini_api_key)

    print("2. Client created")
    print("3. Sending request...")

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents="Hello Pixel"
    )

    print("4. Response received")
    print(response.text)

except Exception as e:
    print("\nGEMINI ERROR")
    print("Error type:", type(e).__name__)
    print("Error:", e)


class PixelAssistant:

    

    def __init__(self, gui):
        self.gui = gui
        self.recognizer = sr.Recognizer()

        self.recognizer.dynamic_energy_threshold = True

        self.recognizer.pause_threshold = 0.8

        self.speaking_lock = threading.Lock()

        self.engine = pyttsx3.init()

        self.engine.setProperty("rate", 170)
      
        self.client = genai.Client(api_key=Gemini_api_key)

    def ask_ai(self, question):
     try:
        print("Pixel AI:", question)

        response = self.client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=f"""
You are Pixel, a friendly personal desktop assistant.

Answer the user's question clearly and naturally.
Keep answers short and direct.

User's question:
{question}
"""
        )

        if response and response.text:
            print("Gemini response received.")
            return response.text.strip()

        return "I didn't get a response from Gemini."

     except Exception as e:
        print("Gemini Error:", type(e).__name__, e)
        return "Sorry, Gemini is temporarily unavailable."
     
    def speak(self, text):
     if not text:
        return

     print("Pixel:", text)

     self.gui.root.after(0, self.gui.speaking)
     self.gui.root.after(0, lambda: self.gui.add_bot(text))

     try:
        print("Stopping engine...")
        self.engine.stop()

        print("Speaking...")
        self.engine.say(str(text))

        print("Running...")
        self.engine.runAndWait()

        print("Finished speaking.")

     except Exception as e:
        print("TTS Error:", e)

     self.gui.root.after(0, self.gui.idle)

    

    # Read News
    \
    def read_news(self):
        self.speak("Fetching the latest news headlines.")

        news_api_key = os.environ.get("news_api_key")

        try:
            r = requests.get(
                "https://newsdata.io/api/1/latest",
                params={
                    "country": "in",
                    "language": "en",
                    "apikey": news_api_key
                },
                timeout=8
            )
            data = r.json()
            articles = data.get("results", [])[:3]

            if not articles:
                self.speak("No news articles found.")
                return

            for article in articles:
                headline = article.get("title", "Untitled")
                self.speak(headline)

        except Exception as e:
            print("News error:", e)
            self.speak("Unable to fetch news at the moment.")

    # -------------------------
    # Command Processor
    # -------------------------
    def process_command(self, command):
        command = command.lower().strip()
        print("Processing Command:", command)
        
        if "open google" in command:
            self.speak("Opening Google")
            webbrowser.open("https://google.com")

        elif "open youtube" in command:
            self.speak("Opening YouTube")
            webbrowser.open("https://youtube.com")

        elif "open linkedin" in command:
            self.speak("Opening LinkedIn")
            webbrowser.open("https://linkedin.com")

        elif "open instagram" in command:
            self.speak("Opening Instagram")
            webbrowser.open("https://instagram.com")
        
        elif command.lower() in ["pixel", "hi pixel", "hello pixel","okk","hi","hey"]:
            self.speak("Yes")

        elif command.startswith("play"):
            song = command.replace("play", "").strip()
            if musics and hasattr(musics, "music") and song in musics.music:
                self.speak(f"Playing {song}")
                webbrowser.open(musics.music[song])
            else:
                self.speak(f"Searching for {song} on YouTube")
                webbrowser.open(f"https://www.youtube.com/results?search_query={song}")

        elif "news" in command:
         self.read_news()
        elif (
             "tell me" in command
              or "what is" in command
              or "who is" in command
              or "how to" in command
              or "how" in command
              or "can you" in command
              or "explain" in command
              or "what" in command
             ):

             clean_question = command

             for phrase in [
             "tell me",
             "what is",
             "who is",
             "how to",
              "how",
             "can you",
             "explain"
           ]:
              clean_question = clean_question.replace(phrase, "", 1).strip()
              self.gui.set_status("Status : Thinking...")
              self.gui.thinking()

              self.speak("Let me find that out for you.")

              answer = self.ask_ai(clean_question)

              self.speak(answer)
        
        
        elif (
            "today" in command
            or "latest" in command
            or "current" in command
            or "news" in command
            or "who won" in command
            or "score" in command
            or "price" in command
            or "weather" in command
         ):

         self.speak("Searching the web.")

         result = self.latest_search(command)

         self.speak(result)
        

            
        else:
            self.speak("I heard: " + command + ". But I don't have a command set for that yet.")

    # -------------------------
    # Main Voice Listening Loop
    # -------------------------
    def run(self):
        self.speak("Pixel active and listening.")

        while True:
            try:
                if hasattr(self.gui, "set_status"):
                    self.gui.root.after(0, lambda: self.gui.set_status("Listening..."))
                if hasattr(self.gui, "listening"):
                    self.gui.root.after(0, self.gui.listening)

                

                with sr.Microphone() as source:
                    print("\n[Listening for speech...]")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                    audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=8)

                print("[Processing speech...]")
                text = self.recognizer.recognize_google(audio, language="en-IN")
                print("Recognized Text:", text)
                if text == "pixel" or "Pixel":
                    self.speak("Yes")
                # Show user input in GUI
                if hasattr(self.gui, "add_user"):
                    self.gui.root.after(0, lambda t=text: self.gui.add_user(t))

                # Process command directly
                self.process_command(text)

            except sr.WaitTimeoutError:
                # No speech detected within timeout period, loop again
                continue

            except sr.UnknownValueError:
                print("Speech was not recognized clearly.")
                continue

            except Exception as e:
                print("Mic Error:", e)
                if hasattr(self.gui, "idle"):
                    self.gui.root.after(0, self.gui.idle)