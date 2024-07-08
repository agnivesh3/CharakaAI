import json
import os
import logging
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Set up logging
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_folder, 'complete_translation_transliteration.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_json(file_path):
    logging.debug(f"Attempting to load JSON from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logging.debug(f"Successfully loaded JSON from {file_path}")
        return data
    except Exception as e:
        logging.error(f"Error loading JSON from {file_path}: {e}")
        raise

def save_json(data, file_path):
    logging.debug(f"Attempting to save JSON to {file_path}")
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        logging.info(f"JSON saved successfully to {file_path}")
    except Exception as e:
        logging.error(f"Error saving JSON to {file_path}: {e}")
        raise

def translate_text(client, text, target_language='en'):
    logging.debug(f"Attempting to translate text: {text[:50]}...")
    try:
        result = client.translate(text, target_language=target_language, format_='text')
        translation = result['translatedText']
        logging.debug(f"Successfully translated text")
        return translation
    except Exception as e:
        logging.error(f"Error translating text: {e}")
        return None

def transliterate_sanskrit(text):
    logging.debug(f"Attempting to transliterate text: {text[:50]}...")
    try:
        transliterated = transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)
        logging.debug(f"Successfully transliterated text")
        return transliterated
    except Exception as e:
        logging.error(f"Error transliterating text: {e}")
        return None

def process_verses(input_json, output_json, credentials_path):
    logging.info(f"Starting process_verses with input: {input_json}, output: {output_json}")
    try:
        # Set up the translation client
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = translate.Client(credentials=credentials)

        data = load_json(input_json)

        for verse in data['book']['sanskrit_verses']:
            sanskrit_text = verse['sanskrit']

            transliteration = transliterate_sanskrit(sanskrit_text)
            translation = translate_text(client, sanskrit_text)

            verse['transliteration'] = transliteration
            verse['translation'] = translation

            logging.info(f"Processed verse {verse['verse_number']}")

        save_json(data, output_json)
        logging.info(f"Processed JSON saved to {output_json}")
    except Exception as e:
        logging.error(f"Error in process_verses: {e}")
        raise

if __name__ == "__main__":
    input_json = "ExtractedFromOCR/S1C5/charaka_samhita_output.json"
    output_json = "ExtractedFromOCR/S1C5/charaka_samhita_translated.json"
    credentials_path = "csprocessor-service-account.json"

    try:
        process_verses(input_json, output_json, credentials_path)
        logging.info("Processing completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
