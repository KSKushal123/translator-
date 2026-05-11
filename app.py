from flask import Flask, render_template, request, jsonify, send_file
from deep_translator import GoogleTranslator
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

if __name__ == '__main__':
    app.run(debug=True)
