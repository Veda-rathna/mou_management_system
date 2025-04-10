# MOU Management System

A smart, link-based legal automation system for managing Memorandums of Understanding (MOUs) between institutions.

## Features

- **Secure Upload Links**: Generate unique, time-limited links for external organizations to upload MOUs
- **Digital Signature**: Allow partners to sign documents digitally
- **PDF Analysis**: Extract key information from uploaded PDFs
- **OCR Support**: Process scanned documents using Tesseract OCR
- **Smart Clause Extraction**: Automatically identify and extract key legal clauses
- **Signature Verification**: Basic AI-powered signature authenticity checking
- **Email Reminders**: Automatic notifications for expiring MOUs
- **Admin Dashboard**: Comprehensive management interface

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **PDF Processing**: pdfplumber, PyMuPDF
- **OCR**: pytesseract + Tesseract OCR Engine
- **NLP**: spaCy for clause extraction
- **Signature Verification**: TensorFlow
- **Email**: SMTP integration

## Installation

1. Clone the repository:
   \`\`\`
   git clone https://github.com/yourusername/mou-management-system.git
   cd mou-management-system
   \`\`\`

2. Create and activate a virtual environment:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

4. Install Tesseract OCR:
   - On Ubuntu: `sudo apt-get install tesseract-ocr`
   - On Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - On macOS: `brew install tesseract`

5. Create a `.env` file based on `.env.example`:
   \`\`\`
   cp .env.example .env
   \`\`\`
   Then edit the `.env` file with your configuration.

6. Initialize the database:
   \`\`\`
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   \`\`\`

7. Create an admin user:
   \`\`\`
   flask create-admin
   \`\`\`

8. Run the application:
   \`\`\`
   flask run
   \`\`\`

## Deployment

The application can be deployed on various platforms:

- **Render**: Deploy the Flask application with a PostgreSQL database
- **Railway**: Easy deployment with PostgreSQL integration
- **Replit**: Free hosting for educational purposes

## License

This project is licensed under the MIT License - see the LICENSE file for details.
\`\`\`

```python file="requirements.txt" type="code"
Flask==2.2.3
Flask-SQLAlchemy==3.0.3
Flask-Migrate==4.0.4
Flask-Login==0.6.2
Werkzeug==2.2.3
pdfplumber==0.9.0
PyMuPDF==1.22.3
pytesseract==0.3.10
pdf2image==1.16.3
spacy==3.5.3
tensorflow==2.12.0
Pillow==9.5.0
schedule==1.2.0
python-dotenv==1.0.0
gunicorn==20.1.0
psycopg2-binary==2.9.6
email-validator==2.0.0.post2
