from flask import Flask, render_template, request, jsonify, send_file
from deep_translator import GoogleTranslator
import speech_recognition as sr
from gtts import gTTS
import io

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
    filename = audio_file.filename or 'audio.webm'
    recognizer = sr.Recognizer()
    
    # Tune recognizer for speed
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.5
    recognizer.dynamic_energy_threshold = False
    
    try:
        # Handle compressed formats (webm, ogg) by converting to WAV via pydub
        if filename.endswith(('.webm', '.ogg')):
            from pydub import AudioSegment
            import tempfile, os
            
            # Save uploaded file to a temp file
            with tempfile.NamedTemporaryFile(suffix=f'.{filename.rsplit(".", 1)[-1]}', delete=False) as tmp_in:
                audio_file.save(tmp_in)
                tmp_in_path = tmp_in.name
            
            try:
                # Convert to WAV (mono, 16kHz for faster processing)
                audio_segment = AudioSegment.from_file(tmp_in_path)
                audio_segment = audio_segment.set_channels(1).set_frame_rate(16000)
                
                wav_buffer = io.BytesIO()
                audio_segment.export(wav_buffer, format='wav')
                wav_buffer.seek(0)
                
                with sr.AudioFile(wav_buffer) as source:
                    audio_data = recognizer.record(source)
            finally:
                os.unlink(tmp_in_path)
        else:
            # Direct WAV handling (original path)
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
            
        # Transcribe using Google Web Speech API
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
