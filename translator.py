from deep_translator import GoogleTranslator

def translate_english_to_kannada(text: str) -> str:
    """
    Translates English text to Kannada.
    """
    try:
        # 'en' is the code for English, 'kn' is the code for Kannada
        translated_text = GoogleTranslator(source='en', target='kn').translate(text)
        return translated_text
    except Exception as e:
        return f"An error occurred during translation: {e}"

if __name__ == "__main__":
    print("=== English to Kannada Translator ===")
    print("Type 'exit' or 'quit' to stop the translator.")
    
    while True:
        try:
            text = input("\nEnter English text: ")
            if text.strip().lower() in ['exit', 'quit']:
                print("Exiting translator. Goodbye!")
                break
            
            if not text.strip():
                continue
                
            translation = translate_english_to_kannada(text)
            print(f"Kannada translation: {translation}")
        except KeyboardInterrupt:
            print("\nExiting translator. Goodbye!")
            break
