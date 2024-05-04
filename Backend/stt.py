from gtts import gTTS
import speech_recognition as sr
import os

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    os.system("afplay output.mp3")
    os.remove("output.mp3")

def beep():
    os.system("afplay /System/Library/Sounds/Ping.aiff")

def listen_for_word(word):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for the word '{}'...".format(word))
        while True:
            try:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                spoken_text = recognizer.recognize_sphinx(audio).lower()

                print("You said: {}".format(spoken_text))

                if word in spoken_text:
                    print("Word '{}' detected! Beeping...".format(word))
                    beep()
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print("Error with the speech recognition service; {0}".format(e))

if __name__ == "__main__":
    target_word = "example"  # Change this to the word you want to detect
    speak("Please say the word '{}'.".format(target_word))
    listen_for_word(target_word)
