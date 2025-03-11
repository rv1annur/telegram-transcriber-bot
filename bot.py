import telebot
import requests
import os
from pydub import AudioSegment
import openai
from googletrans import Translator

# Load API keys from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
openai.api_key = OPENAI_KEY

def download_audio(file_id):
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    
    response = requests.get(file_url)
    audio_path = "audio.ogg"
    
    with open(audio_path, "wb") as f:
        f.write(response.content)
    
    return audio_path

def convert_to_wav(input_path):
    output_path = "audio.wav"
    audio = AudioSegment.from_ogg(input_path)
    audio.export(output_path, format="wav")
    return output_path

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

def translate_text(text):
    translator = Translator()
    translated = translator.translate(text, dest="en")
    return translated.text

@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    bot.send_message(message.chat.id, "Processing your voice message...")

    audio_path = download_audio(message.voice.file_id)
    wav_path = convert_to_wav(audio_path)

    try:
        text = transcribe_audio(wav_path)
        translated_text = translate_text(text)
        bot.send_message(message.chat.id, f"Transcription: {translated_text}")
    except Exception as e:
        bot.send_message(message.chat.id, "Error: " + str(e))
    
    os.remove(audio_path)
    os.remove(wav_path)

bot.polling()
