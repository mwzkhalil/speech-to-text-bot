from flask import Flask, request, jsonify
from audio_recorder_streamlit import audio_recorder
from faster_whisper import WhisperModel
from openai import OpenAI

app = Flask(__name__)

######### Transcriber ###########

model_size = "large-v3"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# Transcribe audio function
def transcribe_audio(audio_file_path, beam_size=5):
    segments, info = model.transcribe(audio_file_path, beam_size=beam_size)
    transcribed_text = ""

    for segment in segments:
        transcribed_text += segment.text + " "

    return transcribed_text

client = OpenAI(api_key="")

# Analyze transcription function
def analyze_transcription(transcription):
    response = client.chat.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant to retrieve important information from a given message. Each variable should have its own line."},
            {"role": "user", "content": "Retrieve name, issue and phone number from the following text: {}".format(transcription)}
            ],
        temperature=0.2
    )
    return response

# Routes
@app.route('/record-audio', methods=['POST'])
def record_audio():
    audio_bytes = request.data
    with open("recorded_audio.wav", "wb") as f:
        f.write(audio_bytes)
    return "Audio recorded successfully!"

@app.route('/transcribe-audio', methods=['POST'])
def transcribe_audio_route():
    audio_file_path = "recorded_audio.wav"
    transcription = transcribe_audio(audio_file_path)
    return transcription

@app.route('/analyze-transcription', methods=['POST'])
def analyze_transcription_route():
    transcription = request.data.decode("utf-8")
    response = analyze_transcription(transcription)
    return response.choices[0]["message"]["content"]

if __name__ == '__main__':
    app.run(debug=True)
