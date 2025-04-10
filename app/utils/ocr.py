import pytesseract
from PIL import Image
import pdf2image
import os
import tempfile
from app.config import Config

def process_scanned_pdf(pdf_path):
    """
    Process a scanned PDF using OCR to extract text
    """
    result = {
        'text': '',
        'start_date': None,
        'end_date': None,
        'organizations': []
    }
    
    # Set Tesseract command if specified in config
    if Config.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
    
    # Create a temporary directory for the images
    with tempfile.TemporaryDirectory() as temp_dir:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)
        
        # Process each page
        full_text = ""
        for i, image in enumerate(images):
            # Save the image temporarily
            image_path = os.path.join(temp_dir, f'page_{i}.png')
            image.save(image_path, 'PNG')
            
            # Perform OCR
            text = pytesseract.image_to_string(Image.open(image_path))
            full_text += text + "\n"
    
    result['text'] = full_text
    
    # Use the pdf_parser to extract dates and organizations from the OCR text
    from app.utils.pdf_parser import extract_pdf_info
    
    # Create a temporary text file with the OCR results
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(full_text.encode('utf-8'))
        temp_file_path = temp_file.name
    
    try:
        # Extract information as if it were a text file
        extracted_info = extract_pdf_info(temp_file_path)
        result.update(extracted_info)
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    
    return result
