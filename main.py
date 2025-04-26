# To run this code you need to install the following dependencies:
# pip install google-genai speechrecognition gtts pyserial

import base64
from google import genai
from google.genai import types
import os
import speech_recognition as sr
from gtts import gTTS
import serial
import time

# Initialize serial communication with Arduino
arduino = serial.Serial('COM3', 9600)  # Replace 'COM3' with your Arduino's port

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def record_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

def send_to_google_api(user_input):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_input,
    )
    return response.text

def text_to_speech(text):
    tts = gTTS(text)
    tts.save("response.mp3")
    print("Response saved as response.mp3")

def send_to_arduino(message):
    arduino.write(message.encode())
    time.sleep(2)  # Wait for Arduino to process
    response = arduino.readline().decode('utf-8').strip()
    print(f"Arduino response: {response}")
    return response

if __name__ == "__main__":
    user_input = record_voice()
    if user_input:
        google_response = send_to_google_api(user_input)
        print(f"Google API Response: {google_response}")
        arduino_response = send_to_arduino(google_response)
        text_to_speech(arduino_response)