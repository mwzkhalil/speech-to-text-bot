from flask import Flask, request, jsonify
from audio_recorder_streamlit import audio_recorder
from faster_whisper import WhisperModel
from transformers import AutoTokenizer
import transformers


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

#specify the model you want to use
model = "meta-llama/Meta-Llama-3-8B"

#load the pretrained tokenizer
tokenizer = AutoTokenizer.from_pretrained(model)

#make it ready for text generation
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

def get_response_llama2(prompt):

  sequences = pipeline(prompt,
      do_sample=True,
      return_full_text=False,
      top_k=10,
      num_return_sequences=1,
      eos_token_id=tokenizer.eos_token_id,
      max_length=4096,
  )
  return sequences[0]['generated_text']

systems = {"role": "system", "content": "You are an assistant to retrieve important information from a given message. Each variable should have its own line."}
    # Ensure the input is a list of messages
    if isinstance(inp, str):
        user_message = {"role": "user", "content": inp}
        new_inp = [systems, user_message]
    elif isinstance(inp, list):
        new_inp = [systems] + inp
    else:
        raise ValueError("Input should be a string or a list of messages")
    
    # print("inp : \n", new_inp)
    # new_inp = inp
    # new_inp.insert(0,systems)
    # print("inp : \n ",new_inp)
    completion = get_response_llama2(
    new_inp
    )
    return completion

# Analyze transcription function
def analyze_transcription(transcription):
    systems = {"role": "system", "content": "You are an assistant to retrieve important information from a given message. Each variable should have its own line."}
    # Ensure the input is a list of messages
    if isinstance(inp, str):
        user_message = {"role": "user", "content": inp}
        new_inp = [systems, user_message]
    elif isinstance(inp, list):
        new_inp = [systems] + inp
    else:
        raise ValueError("Input should be a string or a list of messages")
    
    # print("inp : \n", new_inp)
    # new_inp = inp
    # new_inp.insert(0,systems)
    # print("inp : \n ",new_inp)
    response = get_response_llama2(
    new_inp
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
