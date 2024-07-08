Here is a more professional version of your README notes:

---

# CharakaAI - Processing Workflow

## Steps to Process the Book

### 1. Extract Chapters into Individual PDFs

Manually extract each chapter of the book into its own PDF file and place them in the `Book` folder.

### 2. Split PDFs into Individual Pages

The script `BookToImageSplitToEachPage.py` will split each PDF into individual page PNG files for easier processing.

**Instructions:**
- Modify the following parameters:
  - PDF name in line 73.
  - Folder name in line 74 based on the chapter name.
  - Specify the pages in the book to be processed. By default, it processes 10 pages.
- Logs are written to `logs/pdf_to_image_extraction.log`.
- Run the script using the command:
  ```sh
  python3 BookToImageSplitToEachPage.py --start_page 1 --end_page 12
  ```

### 3. Generate Base JSON from Images

The script `ImageToBaseJson.py` will process all the images created in the previous step and generate a base JSON file. This JSON will contain Sanskrit verses and their logical groupings based on the provided English translation. This serves as a baseline for subsequent steps to generate transliteration and translation using the GCP Translate API.

**Instructions:**
- Modify the following parameters:
  - Folder path in line 169 according to the chapter being processed.
  - Section name, chapter name, and chapter description in lines 146, 147, and 148 respectively.
- Logs are written to `logs/charaka_samhita_processing_timestamp.log`.
- Run the script using the command:
  ```sh
  python3 ImageToBaseJson.py
  ```

### 4. Generate Complete JSON with Transliteration and Translation

The script `GenerateCompleteJson.py` will use the base JSON from the previous step, apply `indic_transliteration` for transliteration, and use the Google Translate API to translate the Sanskrit verses into English.

**Instructions:**
- Modify the input and output JSON paths in lines 88 and 89.
- Install `indic-transliteration` using:
  ```sh
  pip3 install indic-transliteration
  ```
- Logs are written to `logs/complete_translation_transliteration.log`.
- Run the script using the command:
  ```sh
  python3 GenerateCompleteJson.py
  ```

### 5. Generate Complete Interpretation by Claude Sonnet 3.5

This Python script generateInterpretationByClaudeSonnet.py processes Sanskrit verses from the Charaka Samhita, leveraging the Claude AI model for translation and in-depth analysis. Here's an overview of its functionality:

1. **Input Processing**: Reads Sanskrit verses from a JSON file in a specified directory structure.

2. **Claude AI Integration**:
   - Utilizes the Claude API (version 3-5-sonnet-20240620) for verse analysis.
   - Sends carefully crafted prompts to Claude for each verse or verse group.
   - The prompt instructs Claude to provide:
     a. An accurate English translation
     b. Explanation of key Sanskrit terms and concepts
     c. Context and significance within Ayurvedic literature
     d. Detailed interpretation of the verses
     e. Discussion of related Ayurvedic principles and applications
     f. A concise conclusion summarizing key points

3. **API Interaction**:
   - Implements a robust API calling function with retry mechanism.
   - Handles potential API errors and network issues gracefully.

4. **Response Processing**:
   - Parses Claude's responses into structured sections.
   - Organizes the AI-generated content into a comprehensive analysis format.

5. **Output Generation**:
   - Creates two output files:
     a. A detailed JSON file containing all analyses
     b. A formatted text file for easier reading

6. **Logging**: Maintains a detailed log of the entire process, including API interactions and any errors encountered.

This script demonstrates an advanced application of AI in scholarly text analysis, showcasing how Claude can be used for complex tasks like translating and interpreting ancient medical texts. It provides a framework for processing large volumes of Sanskrit text, making it valuable for researchers and scholars in Ayurvedic studies.

**Instructions:**
- Modify the input path for the JSON according to the chapter number.
- Logs are written to `InterpretationByClaude/logs/Chapter number`.
- Run the script using the command:
  ```sh
  python3 generateInterpretationByClaudeSonnet.py
  ```

---

These steps will guide you through processing your book into a structured format with transliterations, translations, and interpretations.
