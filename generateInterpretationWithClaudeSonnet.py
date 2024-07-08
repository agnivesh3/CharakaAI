import json
import requests
import logging
import time
import os
from requests.exceptions import RequestException

def call_claude_api(prompt, retries=3, delay=5):
    api_url = "https://api.anthropic.com/v1/messages"
    api_key = "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"  # Replace with your actual API key

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "anthropic-version": "2023-06-01"
    }

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000
    }

    for attempt in range(retries):
        try:
            logger.debug(f"Sending API request, attempt {attempt + 1}")
            response = requests.post(api_url, headers=headers, json=data)
            response.raise_for_status()
            logger.debug("API request successful")
            content = response.json()['content']
            logger.debug(f"API response: {content}")
            return content
        except RequestException as e:
            logger.error(f"API request failed: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Max retries reached. Giving up.")
                raise

def process_verses(json_data):
    verses = json_data['sanskrit_verses']
    verse_groups = json_data['verse_groups']

    results = []

    for i, group in enumerate(verse_groups):
        logger.info(f"Processing verse group {i+1}/{len(verse_groups)}: {group}")

        try:
            if '-' in group:
                start, end = map(int, group.split('-'))
                group_verses = [v for v in verses if start <= v['verse_number'] <= end]
            else:
                group_verses = [v for v in verses if v['verse_number'] == int(group)]

            if not group_verses:
                raise ValueError(f"No verses found for group {group}")

            sanskrit_text = "\n".join([verse['sanskrit'] for verse in group_verses])

            prompt = f"""As an expert in Sanskrit, Ayurvedic literature, and academic writing, please provide a comprehensive and consistent analysis of the following Sanskrit verse(s) from the Charaka Samhita:

{sanskrit_text}

Please adhere to the following guidelines to ensure consistency and suitability for compilation into a book:

1. Translation:
Provide a clear and accurate English translation of the Sanskrit text. Maintain a consistent style of translation throughout, balancing literalness with readability. Use parentheses for clarifying words not in the original text.

2. Vocabulary and Key Terms:
Identify and explain 3-5 significant or specialized terms used in the verse(s). Focus on Ayurvedic concepts, herbs, or medical practices. Provide the Sanskrit term followed by its English translation and a brief explanation. Maintain consistency in terminology across verses.

3. Context and Significance:
In 2-3 sentences, explain the context of these verse(s) within the Charaka Samhita and broader Ayurvedic literature. Discuss their importance to Ayurvedic medicine or philosophy, maintaining a consistent perspective on the text's significance.

4. Detailed Interpretation:
Provide a thorough interpretation of the verse(s), consistently addressing:
   a) The main ideas or concepts presented (1-2 paragraphs)
   b) Medical or philosophical principles discussed (1 paragraph)
   c) Practical applications or implications of the information (1 paragraph)
   d) How this information fits into the broader context of Ayurvedic knowledge (1-2 sentences)

5. Ayurvedic Principles and Applications:
In 1-2 paragraphs, discuss how the concepts in these verse(s) relate to core Ayurvedic principles (such as the tridosha theory, panchamahabhutas, or specific diagnostic/treatment methods). Explain their practical applications in traditional Ayurvedic medicine, including any specific treatments, formulations, or diagnostic methods mentioned or implied in the verses.

6. Conclusion:
In 3-4 sentences, summarize the key points and overall significance of these verse(s). Ensure this conclusion could serve as a standalone summary if extracted.

Throughout your analysis:
- Maintain a formal, academic tone suitable for a scholarly publication.
- Use consistent terminology and phrasing for recurring concepts.
- Provide brief Sanskrit citations (in parentheses) for key terms or concepts to maintain connection with the original text.
- Ensure each section flows logically into the next, creating a cohesive narrative.
- Aim for clarity and accessibility while maintaining depth of analysis.

Your response should be detailed yet clear, suitable for readers with varying levels of familiarity with Ayurveda or Sanskrit literature, while still providing valuable insights for more knowledgeable readers.
"""

            logger.debug(f"Sending prompt for verse group {group}")
            response = call_claude_api(prompt)
            logger.debug(f"Received response for verse group {group}")

            # Extract the text from the response
            if isinstance(response, list) and len(response) > 0 and 'text' in response[0]:
                response_text = response[0]['text']
            else:
                logger.warning(f"Unexpected response format for verse group {group}")
                response_text = "Response not in expected format"

            # Split the response into sections
            sections = {}
            current_section = ""
            for line in response_text.split('\n'):
                if line.strip() in ["1. Translation:", "2. Vocabulary and Key Terms:", "3. Context and Significance:", "4. Detailed Interpretation:", "5. Ayurvedic Principles and Applications:", "6. Conclusion:"]:
                    current_section = line.strip()[3:-1]  # Remove number and colon
                    sections[current_section] = ""
                elif current_section:
                    sections[current_section] += line + "\n"

            results.append({
                "verses": group,
                "sanskrit": sanskrit_text,
                "translation": sections.get("Translation", "Translation not available").strip(),
                "vocabulary": sections.get("Vocabulary and Key Terms", "Vocabulary not available").strip(),
                "context": sections.get("Context and Significance", "Context not available").strip(),
                "interpretation": sections.get("Detailed Interpretation", "Interpretation not available").strip(),
                "ayurvedic_principles": sections.get("Ayurvedic Principles and Applications", "Ayurvedic principles and applications not available").strip(),
                "conclusion": sections.get("Conclusion", "Conclusion not available").strip()
            })

        except Exception as e:
            logger.error(f"Error processing verse group {group}: {e}", exc_info=True)
            results.append({
                "verses": group,
                "sanskrit": f"Error occurred: {str(e)}",
                "translation": "Error occurred",
                "vocabulary": "Error occurred",
                "context": "Error occurred",
                "interpretation": "Error occurred",
                "ayurvedic_principles": "Error occurred",
                "conclusion": "Error occurred"
            })

    return results

def main():
    try:
        logger.info("Starting script execution")

        # Load the JSON data
        logger.info(f"Loading JSON data from {INPUT_FILE}")
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        logger.info("JSON data loaded successfully")

        # Extract the 'book' part of the JSON
        book_data = json_data['book']

        # Process the verses
        logger.info("Beginning verse processing")
        results = process_verses(book_data)
        logger.info("Verse processing complete")

        # Prepare the output JSON
        output_json = {
            "timestamp": json_data["timestamp"],
            "book": {
                "title": book_data["title"],
                "volume": book_data["volume"],
                "section": book_data["section"],
                "chapter": book_data["chapter"],
                "chapter_name": book_data["chapter_name"],
            },
            "translations": results
        }

        # Save the results
        logger.info(f"Saving results to JSON file: {OUTPUT_JSON_FILE}")
        with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_json, f, ensure_ascii=False, indent=2)

        # Create formatted text output
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = f"{i}. Verses {result['verses']}:\n\nSanskrit:\n{result['sanskrit']}\n\nTranslation:\n{result['translation']}\n\nVocabulary and Key Terms:\n{result['vocabulary']}\n\nContext and Significance:\n{result['context']}\n\nDetailed Interpretation:\n{result['interpretation']}\n\nAyurvedic Principles and Applications:\n{result['ayurvedic_principles']}\n\nConclusion:\n{result['conclusion']}"
            formatted_results.append(formatted_result)

        logger.info(f"Saving results to text file: {OUTPUT_TEXT_FILE}")
        with open(OUTPUT_TEXT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n\n" + "="*50 + "\n\n".join(formatted_results))

        logger.info("Results saved successfully")
        logger.info("Script execution completed successfully")

    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)

# File path variables
BASE_FOLDER_INPUT = 'ExtractedFromOCR'
BASE_FOLDER_OUTPUT = 'InterpretationByClaude'
CHAPTER_FOLDER = 'S1C3'  # This might change for different chapters
INPUT_FILE = os.path.join(BASE_FOLDER_INPUT, CHAPTER_FOLDER, 'charaka_samhita_output.json')

OUTPUT_FOLDER = os.path.join(BASE_FOLDER_OUTPUT, CHAPTER_FOLDER, 'output')
LOG_FOLDER = os.path.join(BASE_FOLDER_OUTPUT, CHAPTER_FOLDER, 'logs')

OUTPUT_JSON_FILE = os.path.join(OUTPUT_FOLDER, 'charaka_samhita_translated_detailed_full.json')
OUTPUT_TEXT_FILE = os.path.join(OUTPUT_FOLDER, 'charaka_samhita_translated_detailed_full.txt')
LOG_FILE = os.path.join(LOG_FOLDER, 'charaka_samhita_translation_detailed_full.log')

# Create folders if they don't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# Set up logging to write to a file
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    main()
