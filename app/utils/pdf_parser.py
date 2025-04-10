import pdfplumber
import PyPDF2
from datetime import datetime
import re
import os
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter

def extract_pdf_info(pdf_path):
    """
    Extract information from a PDF file including text, dates, and organization names
    """
    result = {
        'text': '',
        'start_date': None,
        'end_date': None,
        'organizations': []
    }
    
    # Extract text using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        
        result['text'] = text
    
    # Extract dates using regex
    date_patterns = [
        r'(?:effective|start|commencement)\s+date.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4})',
        r'(?:expiry|end|termination)\s+date.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4})',
        r'valid\s+(?:for|until).*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4})',
        r'period\s+of\s+(\d+)\s+(?:year|month)'
    ]
    
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Process dates based on the pattern matched
            if 'effective' in match.group(0).lower() or 'start' in match.group(0).lower() or 'commencement' in match.group(0).lower():
                date_str = match.group(1)
                try:
                    # Try to parse the date
                    result['start_date'] = parse_date(date_str)
                except:
                    pass
            elif 'expiry' in match.group(0).lower() or 'end' in match.group(0).lower() or 'termination' in match.group(0).lower() or 'valid until' in match.group(0).lower():
                date_str = match.group(1)
                try:
                    result['end_date'] = parse_date(date_str)
                except:
                    pass
            elif 'period' in match.group(0).lower():
                # Handle period specification (e.g., "period of 5 years")
                duration = int(match.group(1))
                unit = 'year' if 'year' in match.group(0).lower() else 'month'
                
                if result['start_date']:
                    if unit == 'year':
                        result['end_date'] = datetime(
                            result['start_date'].year + duration,
                            result['start_date'].month,
                            result['start_date'].day
                        ).date()
                    else:  # month
                        # Simple calculation, not accounting for varying month lengths
                        year_add = (result['start_date'].month + duration - 1) // 12
                        month = (result['start_date'].month + duration - 1) % 12 + 1
                        result['end_date'] = datetime(
                            result['start_date'].year + year_add,
                            month,
                            result['start_date'].day
                        ).date()
    
    # Extract organization names
    org_pattern = r'(?:between|party[:\s]|organization[:\s]|institution[:\s]|university[:\s]|company[:\s]).*?([A-Z][A-Za-z\s,\.]+)(?:and|,|\n)'
    matches = re.finditer(org_pattern, text, re.IGNORECASE)
    for match in matches:
        org_name = match.group(1).strip()
        if org_name and len(org_name) > 3:  # Avoid short matches
            result['organizations'].append(org_name)
    
    return result

def parse_date(date_str):
    """
    Parse date string in various formats
    """
    # Try different date formats
    formats = [
        '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y',
        '%d %B %Y', '%B %d, %Y', '%d %b %Y', '%b %d, %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    # If all formats fail, raise exception
    raise ValueError(f"Could not parse date: {date_str}")

def add_signature_to_pdf(pdf_path, signature_path, output_path):
    """
    Add a signature image to the last page of a PDF
    """
    # Read the original PDF
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    # Copy all pages except the last one
    for i in range(len(reader.pages) - 1):
        writer.add_page(reader.pages[i])
    
    # Get the last page
    last_page = reader.pages[-1]
    
    # Create a new PDF with the signature
    c = canvas.Canvas("temp_signature.pdf")
    
    # Get page dimensions
    page_width = float(last_page.mediabox.width)
    page_height = float(last_page.mediabox.height)
    
    # Position the signature at the bottom right
    signature_img = ImageReader(signature_path)
    img_width, img_height = signature_img.getSize()
    
    # Scale the signature if it's too large
    max_width = page_width / 3
    max_height = page_height / 6
    
    if img_width > max_width:
        ratio = max_width / img_width
        img_width = max_width
        img_height = img_height * ratio
    
    if img_height > max_height:
        ratio = max_height / img_height
        img_height = max_height
        img_width = img_width * ratio
    
    # Draw the signature
    c.drawImage(
        signature_img, 
        page_width - img_width - 50,  # 50 points from right edge
        50,  # 50 points from bottom
        width=img_width, 
        height=img_height
    )
    
    c.save()
    
    # Merge the signature with the last page
    signature_pdf = PdfReader("temp_signature.pdf")
    last_page.merge_page(signature_pdf.pages[0])
    
    # Add the modified last page
    writer.add_page(last_page)
    
    # Write the output PDF
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    
    # Clean up temporary file
    if os.path.exists("temp_signature.pdf"):
        os.remove("temp_signature.pdf")
