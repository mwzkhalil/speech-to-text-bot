import telebot
from pydub import AudioSegment
import requests
import os
import json

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

# Replace these with your actual API endpoints
TEXT_API_ENDPOINT = "http://localhost:5000/transcribe-audio"
AUDIO_API_ENDPOINT = "http://localhost:5000/record-audio"
ANALYZE_API_ENDPOINT = "http://localhost:5000/analyze-transcription"

@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    # Send received text to the API
    try:
        response = requests.post(TEXT_API_ENDPOINT, data=message.text.encode("utf-8"))
        if response.status_code == 200:
            # Send the response back to the user
            bot.send_message(message.chat.id, response.text)
        else:
            bot.send_message(message.chat.id, "Sorry, there was an error processing your request.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

@bot.message_handler(content_types=['voice'])
def handle_voice_messages(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save the voice note locally in .oga format
        voice_file_path = 'voice_note.oga'
        with open(voice_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Prepare files for the POST request
        files = {
            'audio': (voice_file_path, open(voice_file_path, 'rb'), 'audio/ogg'),
        }
        
        # Sending POST request to the Flask server with the audio file
        response = requests.post(AUDIO_API_ENDPOINT, files=files)
        
        if response.status_code == 200:
            # Send the response back to the user
            bot.send_message(message.chat.id, response.text)
        else:
            bot.send_message(message.chat.id, "Sorry, there was an error processing your audio.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")
    finally:
        # Cleanup temporary files
        if os.path.exists(voice_file_path):
            os.remove(voice_file_path)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        response = requests.post(ANALYZE_API_ENDPOINT, data=message.text.encode("utf-8"))
        if response.status_code == 200:
            # Send the response back to the user
            bot.send_message(message.chat.id, response.text)
        else:
            bot.send_message(message.chat.id, "Sorry, there was an error processing your request.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

# Start polling
bot.polling(timeout=30)

