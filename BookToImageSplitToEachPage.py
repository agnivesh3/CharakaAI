import os
import logging
import argparse
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
from PIL import Image
import io

# Configure logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'pdf_to_image_extraction.log'),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "csprocessor-service-account.json"

# Initialize the Document AI client
try:
    project_id = "1039812532642"
    location = "us"
    processor_id = "1fb139ed60959696"

    client_options = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    documentai_client = documentai.DocumentProcessorServiceClient(client_options=client_options)

    # The full resource name of the processor
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    logging.info("Initialized Document AI client")
except Exception as e:
    logging.error(f"Error initializing Document AI client: {e}")
    print(f"Error initializing Document AI client: {e}")
    exit(1)

def process_document(file_path: str, start_page: int, end_page: int) -> documentai.Document:
    try:
        with open(file_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        raw_document = documentai.RawDocument(content=pdf_content, mime_type="application/pdf")
        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document,
            process_options=documentai.ProcessOptions(
                individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
                    pages=[i for i in range(start_page, end_page + 1)]
                )
            )
        )
        result = documentai_client.process_document(request=request)

        logging.info(f"Document processing complete. Pages processed: {len(result.document.pages)}")
        return result.document
    except Exception as e:
        logging.error(f"Error processing document {file_path}: {str(e)}")
        return None

def save_pages_as_images(document: documentai.Document, output_folder: str, start_page: int) -> None:
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, page in enumerate(document.pages):
        image = Image.open(io.BytesIO(page.image.content))
        image_path = os.path.join(output_folder, f"page_{start_page + i:04d}.png")
        image.save(image_path)
        logging.info(f"Saved {image_path}")

def main(start_page: int, end_page: int):
    pdf_path = "Book/S1-Chapter5.pdf"
    image_output_folder = "ExtractedImage/S1-Chapter5"

    logging.info(f"Starting PDF to image extraction for pages {start_page} to {end_page}")

    document = process_document(pdf_path, start_page, end_page)
    if document is None:
        logging.error("Failed to process PDF document")
        return

    save_pages_as_images(document, image_output_folder, start_page)

    logging.info("PDF to image extraction completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract images from Charaka Samhita PDF")
    parser.add_argument("--start_page", type=int, default=1, help="Starting page number (default: 1)")
    parser.add_argument("--end_page", type=int, default=10, help="Ending page number (default: 2)")

    args = parser.parse_args()

    main(args.start_page, args.end_page)
