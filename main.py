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
arduino = serial.Serial('COM7', 9600)  # Replace 'COM3' with your Arduino's port

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def record_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Starting ...")
        while True:
            try:
                print("Listening...")
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

def send_to_google_api(user_input, instruction):
    try:
        # Combine the instruction with the user input
        combined_input = f"{instruction}\n\n{user_input}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=combined_input  # Pass the combined input here
        )
        if response and hasattr(response, 'text'):
            cleaned_response = clean_google_response(response.text)
            return cleaned_response
        else:
            print("Invalid response from Google API.")
            return "Sorry, I couldn't process your request."
    except Exception as e:
        print(f"Error communicating with Google API: {e}")
        return "Sorry, there was an error processing your request."

def text_to_speech(text):
    tts = gTTS(text)
    tts.save("response.mp3")
    print("Response saved as response.mp3")

def send_to_arduino(message):
    formatted_message = f'{message.strip()}'  # Ensure the message is trimmed
    print(f"Sending to Arduino: {formatted_message}")  # Print the message in the terminal
    arduino.write(formatted_message.encode())  # Send the message to Arduino
    time.sleep(2)  # Wait for Arduino to process
    response = arduino.readline().decode('utf-8').strip()  # Read the response from Arduino
    print(f"Arduino response: {response}")  # Print the response in the terminal
    return response

if __name__ == "__main__":
    while True:
        user_input = record_voice()
        if user_input and user_input.lower() == "exit":
            print("Exiting program...")
            break

        instructs = "Instructions: The user input should be about rotating the fan. Based on the user's input, choose one of the following options that best matches and do not include the number: 1. fan on, 2. fan off, 3. left, 4. right, 5. center, 6. low, 7. medium, 8. high, 9. full left, 10. full right, 11. stop sweep, 12. sweep. This is the user input: "

        if user_input:
            google_response = send_to_google_api(user_input, instruction=instructs)
            print(f"Google API Response: {google_response}")    
            arduino_response = send_to_arduino(google_response)