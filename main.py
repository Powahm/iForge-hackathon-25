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
import wave
import re

# Initialize serial communication with Arduino
arduino = serial.Serial('COM3', 9600)  # Replace 'COM3' with your Arduino's port

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def record_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        while True:
            try:
                audio = recognizer.listen(source, timeout=5)  # Adjusted to stop recording when the user stops talking
                print("Recognizing...")
                
                # Save the audio to a file
                '''
                with open("user_input.wav", "wb") as audio_file:
                    audio_file.write(audio.get_wav_data())
                print("Audio saved as user_input.wav")
                '''

                text = recognizer.recognize_google(audio)
                print(f"Understood: {text}")
                return text
            except sr.UnknownValueError:
                print("Sorry, could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except sr.WaitTimeoutError:
                print("Listening timed out.")
                break

def clean_google_response(response):
    # Remove asterisks and other special characters
    return re.sub(r'[^\w\s]', '', response)

def send_to_google_api(user_input):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_input,
    )
    cleaned_response = clean_google_response(response.text)
    return cleaned_response

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
        text_to_speech(google_response)