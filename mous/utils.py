import re
import pdfplumber
from datetime import datetime
from django.utils import timezone
from .models import ActivityLog


def get_client_ip(request):
    """Get the client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def extract_pdf_data(pdf_path):
    """Extract text and key information from PDF"""
    extracted_data = {
        'full_text': '',
        'clauses': [],
        'dates': [],
        'extracted_expiry_date': None
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + '\n'
            
            extracted_data['full_text'] = full_text
            
            # Extract clauses (paragraphs starting with numbers or "Clause")
            clause_patterns = [
                r'(?:Clause\s+\d+[.:]\s*)(.*?)(?=\n\n|\nClause|\n\d+\.|\Z)',
                r'(?:^\d+\.\s+)(.*?)(?=\n\n|\n\d+\.|\Z)',
                r'(?:Article\s+\d+[.:]\s*)(.*?)(?=\n\n|\nArticle|\n\d+\.|\Z)'
            ]
            
            clauses = []
            for pattern in clause_patterns:
                matches = re.findall(pattern, full_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
                clauses.extend([match.strip() for match in matches if match.strip()])
            
            extracted_data['clauses'] = clauses
            
            # Extract dates
            date_patterns = [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',  # MM/DD/YYYY or DD/MM/YYYY
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # YYYY/MM/DD
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
            ]
            
            dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                dates.extend(matches)
            
            extracted_data['dates'] = dates
            
            # Try to identify expiry date
            expiry_keywords = ['expiry', 'expires', 'expiration', 'valid until', 'term ends', 'termination']
            for keyword in expiry_keywords:
                pattern = rf'{keyword}[:\s]*([^\n]*(?:\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{4}}|\d{{4}}[/-]\d{{1,2}}[/-]\d{{1,2}}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{{1,2}},?\s+\d{{4}}|\d{{1,2}}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{{4}})[^\n]*)'
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    extracted_data['extracted_expiry_date'] = match.group(1).strip()
                    break
            
    except Exception as e:
        extracted_data['error'] = str(e)
    
    return extracted_data


def log_activity(mou, action, user=None, user_name=None, user_email=None, ip_address=None, description=None):
    """Log activity for an MOU"""
    ActivityLog.objects.create(
        mou=mou,
        action=action,
        user=user,
        user_name=user_name,
        user_email=user_email,
        ip_address=ip_address,
        description=description
    )


def parse_date_string(date_str):
    """Parse date string to datetime object"""
    date_formats = [
        '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
        '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d',
        '%B %d, %Y', '%B %d %Y',
        '%d %B %Y', '%d %B, %Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return None


def generate_mou_summary(mou):
    """Generate a summary of MOU for emails and reports"""
    summary = {
        'title': mou.title,
        'partner': mou.partner_name,
        'organization': mou.partner_organization,
        'status': mou.get_status_display(),
        'expiry_date': mou.expiry_date,
        'days_until_expiry': (mou.expiry_date - datetime.now().date()).days,
        'is_expired': mou.is_expired,
        'expires_soon': mou.expires_soon,
        'created_at': mou.created_at,
        'updated_at': mou.updated_at
    }
    return summary
