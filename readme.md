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

### 5. Generate Complete Interpretation by Claude

The script `generateCompleteInterpretationByClaudeSonnet.py` will send each verse to Claude for full interpretation. Claude API credentials and payment are required for this step.

**Instructions:**
- Modify the input path for the JSON according to the chapter number.
- Logs are written to `InterpretationByClaude/logs/Chapter number`.
- Run the script using the command:
  ```sh
  python3 generateInterpretationByClaudeSonnet.py
  ```

---

These steps will guide you through processing your book into a structured format with transliterations, translations, and interpretations.
