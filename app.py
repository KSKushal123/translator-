from flask import Flask, render_template, request, jsonify, send_file
from deep_translator import GoogleTranslator
import speech_recognition as sr
from gtts import gTTS
import io
import wave

app = Flask(__name__)

def translate_text(text: str, target_lang: str) -> str:
    """
    Translates English text to a target language.
    """
    try:
        translated_text = GoogleTranslator(source='en', target=target_lang).translate(text)
        return translated_text
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text'].strip()
    target_lang = data.get('target_lang', 'kn')
    if not text:
        return jsonify({'translation': ''})
        
    translation = translate_text(text, target_lang)
    return jsonify({'translation': translation})

@app.route('/tts', methods=['GET'])
def tts():
    text = request.args.get('text', '')
    lang = request.args.get('lang', 'kn')
    
    if not text:
        return "No text provided", 400
        
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return send_file(fp, mimetype='audio/mpeg')
    except Exception as e:
        return str(e), 500

@app.route('/stt', methods=['POST'])
def stt():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    recognizer = sr.Recognizer()
    
    # Tune for speed: fixed threshold avoids slow dynamic calibration
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.5
    recognizer.dynamic_energy_threshold = False
    
    try:
        # Read WAV bytes directly — avoids any ffprobe/ffmpeg dependency.
        # The browser encodes audio as 16kHz mono 16-bit PCM WAV before upload,
        # so we can parse it with Python's built-in wave module.
        wav_bytes = audio_file.read()
        with wave.open(io.BytesIO(wav_bytes)) as wf:
            sample_rate = wf.getframerate()
            sample_width = wf.getsampwidth()
            pcm_data = wf.readframes(wf.getnframes())

        audio_data = sr.AudioData(pcm_data, sample_rate, sample_width)
        text = recognizer.recognize_google(audio_data, language='en-US')
        return jsonify({'text': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Could not request results; {e}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
