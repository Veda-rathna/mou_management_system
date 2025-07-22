MOU Management Application Design Document
1. Overview
The MOU Management Application is a web-based platform designed to streamline the management of Memoranda of Understanding (MOUs) for an organization. It provides a user-friendly interface to view, manage, and track MOUs, including their expiry dates, details, and associated files. The app supports secure sharing of MOUs via links, digital signature integration, activity tracking, automated clause extraction, and email notifications for upcoming expirations. Built with Django and basic HTML templates, the application prioritizes simplicity, scalability, and extensibility for future AI-driven features.
2. Features
2.1 MOU Dashboard

Card-Based Interface: Displays a list of MOUs as cards, each showing key details (e.g., title, partner name, expiry date, status).
Sorting and Filtering: Users can sort MOUs by expiry date, status, or partner name and filter by active, expired, or pending MOUs.
Responsive Design: Cards are styled using Bootstrap for a clean, mobile-friendly layout.

2.2 MOU Detailed View

Details Display: Clicking a card reveals a detailed view of the MOU, including:
Partner organization details.
Expiry date and status.
Legal clauses (extracted and stored).
Associated PDF file (viewable/downloadable).
Activity log (creation, access, updates, approval timestamps).


File Access: Securely view or download the MOU PDF.

2.3 MOU Sharing and Signing

Link Generation: Generate a unique, secure link for each MOU to share with external parties (e.g., partners ready to sign).
External User Interface:
Accessible via the generated link without requiring login.
Allows uploading an updated MOU PDF.
Form to input partner details (e.g., name, organization, contact info).
Digital signature integration using a library like django-docuSign or a custom canvas-based signature solution.


Security: Links are time-bound (e.g., expire after 7 days) and protected with a unique token.

2.4 MOU Approval Workflow

Approval Process: Organization members can review and approve/reject MOUs submitted via the shared link.
Activity Tracking: Logs all actions (e.g., MOU created, link accessed, PDF uploaded, signed, approved/rejected) with timestamps and user details.

2.5 Data Extraction

PDF Parsing: Automatically extracts key information from uploaded MOU PDFs, including:
Expiry date.
Legal clauses.
Partner details (if present in structured text).


Library: Uses PyPDF2 or pdfplumber for text extraction, with regex-based parsing for structured data.

2.6 Email Notifications

Expiry Reminders: Sends automated email reminders to organization members 3 months before an MOU expires.
Email Content: Includes MOU title, partner name, expiry date, and a link to the detailed view.
Implementation: Uses Django’s send_mail with a Celery task for asynchronous email delivery.

2.7 Future AI Integration

Legal Clause Analysis: Planned feature to use AI (e.g., NLP models) to analyze legal clauses and identify potential disadvantages or risks in MOUs.
Extensibility: Store extracted clauses in a structured format (e.g., JSON) to support future AI processing.

3. Technical Architecture
3.1 Tech Stack

Backend: Django (Python) for handling business logic, authentication, and API endpoints.
Frontend: Basic HTML templates with Bootstrap for styling and responsiveness.
Database: PostgreSQL for robust data storage and querying.
File Storage: Django’s FileField with storage on a local filesystem or cloud service (e.g., AWS S3 for production).
PDF Processing: PyPDF2 or pdfplumber for extracting text from MOU PDFs.
Digital Signatures: django-docuSign or a custom JavaScript-based signature solution using HTML5 Canvas.
Email: Django’s send_mail with Celery for asynchronous email tasks.
Task Queue: Celery with Redis for handling background tasks (e.g., email sending, PDF parsing).
Deployment: Docker for containerization, Gunicorn as the WSGI server, and Nginx as a reverse proxy.

3.2 Database Schema

MOU Model:
id: Primary key.
title: String (MOU title).
partner_name: String.
expiry_date: DateTime.
status: Choices (Draft, Pending, Approved, Expired).
pdf_file: FileField (stores the MOU PDF).
clauses: JSONField (stores extracted legal clauses).
created_at, updated_at: Timestamps.


ActivityLog Model:
mou: ForeignKey to MOU.
action: String (e.g., Created, Accessed, Signed, Approved).
user: ForeignKey to User (or null for external users).
timestamp: DateTime.


ShareLink Model:
mou: ForeignKey to MOU.
token: UUID (unique link identifier).
expires_at: DateTime (link expiration).


User Model: Django’s built-in User model for organization members.

3.3 Key Components

Views:
MouListView: Displays the card-based dashboard.
MouDetailView: Shows detailed MOU information and activity log.
MouShareView: Generates and manages shareable links.
MouSignView: Handles external user interactions (PDF upload, form, signature).
MouApproveView: Manages approval/rejection by organization members.


Templates:
mou_list.html: Card-based dashboard with sorting/filtering.
mou_detail.html: Detailed MOU view with PDF embed and activity log.
mou_sign.html: External user form for PDF upload and signature.


Tasks:
send_expiry_reminder: Celery task to check for MOUs expiring in 3 months and send emails.
extract_mou_data: Background task to parse PDF and extract clauses/expiry date.



4. Implementation Details
4.1 Setup and Configuration

Initialize a Django project with PostgreSQL.
Configure Django settings for file storage, email (e.g., SMTP with Gmail or SendGrid), and Celery with Redis.
Install dependencies: django, psycopg2, PyPDF2, pdfplumber, celery, redis, django-bootstrap5.

4.2 MOU Dashboard

Use Django’s ListView to render MOUs as cards.
Implement sorting/filtering with Django querysets and URL parameters.
Style cards with Bootstrap (e.g., card class with hover effects).

4.3 MOU Detailed View

Use DetailView to display MOU details.
Embed PDF using <embed> tag or provide a download link.
Display activity log as a table, querying the ActivityLog model.

4.4 Sharing and Signing

Generate unique tokens using uuid and store in ShareLink.
Create a public MouSignView accessible via token-based URL.
Use HTML5 Canvas for digital signatures or integrate django-docuSign for production-grade signing.
Validate uploaded PDFs and store them securely.

4.5 Data Extraction

Use pdfplumber to extract text from PDFs.
Apply regex patterns to identify expiry dates (e.g., dd/mm/yyyy, Month dd, yyyy) and clauses (e.g., sections starting with “Clause” or numbered paragraphs).
Store extracted data in the MOU model’s clauses JSONField.

4.6 Email Notifications

Create a Celery task to query MOUs with expiry dates within 3 months.
Use Django’s send_mail to send HTML emails with MOU details and a link to the detailed view.
Schedule the task to run daily using Celery Beat.

4.7 Security

Use Django’s authentication for organization members.
Implement token-based access for external links with expiration.
Sanitize uploaded PDFs to prevent malicious content.
Use HTTPS in production to secure data transmission.

5. Deployment

Containerize the app using Docker for consistent environments.
Use Gunicorn as the application server and Nginx as a reverse proxy.
Deploy to a cloud provider (e.g., AWS, Heroku) with PostgreSQL and Redis services.
Configure environment variables for sensitive settings (e.g., SECRET_KEY, email credentials).

6. Future Enhancements

AI Integration: Use an NLP model (e.g., Hugging Face Transformers) to analyze legal clauses and flag potential risks. Store clauses in a format compatible with AI processing (e.g., JSON).
Advanced Search: Add full-text search for MOUs using Django’s SearchVector with PostgreSQL.
Audit Trail: Enhance activity logging with more granular details (e.g., IP addresses, user roles).

7. Sample Code Snippets
7.1 Models (models.py)
from django.db import models
from django.contrib.auth.models import User
import uuid

class MOU(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('expired', 'Expired'),
    )
    title = models.CharField(max_length=255)
    partner_name = models.CharField(max_length=255)
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    pdf_file = models.FileField(upload_to='mous/')
    clauses = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ActivityLog(models.Model):
    mou = models.ForeignKey(MOU, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ShareLink(models.Model):
    mou = models.ForeignKey(MOU, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()

7.2 Celery Task for Email Reminders (tasks.py)
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import MOU

@shared_task
def send_expiry_reminder():
    three_months_later = timezone.now().date() + timedelta(days=90)
    mous = MOU.objects.filter(expiry_date=three_months_later, status='approved')
    for mou in mous:
        send_mail(
            subject=f'MOU Expiry Reminder: {mou.title}',
            message=f'The MOU with {mou.partner_name} expires on {mou.expiry_date}.',
            from_email='no-reply@organization.com',
            recipient_list=['admin@organization.com'],
            html_message=f'<p>MOU: {mou.title}<br>Partner: {mou.partner_name}<br>Expiry: {mou.expiry_date}</p>'
        )

7.3 MOU List Template (mou_list.html)
{% extends 'base.html' %}
{% block content %}
<div class="container">
    <h1>MOU Dashboard</h1>
    <div class="row">
        {% for mou in mous %}
        <div class="col-md-4">
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">{{ mou.title }}</h5>
                    <p class="card-text">Partner: {{ mou.partner_name }}</p>
                    <p class="card-text">Expiry: {{ mou.expiry_date }}</p>
                    <p class="card-text">Status: {{ mou.get_status_display }}</p>
                    <a href="{% url 'mou_detail' mou.id %}" class="btn btn-primary">View Details</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}

8. Assumptions

Users have basic authentication (Django’s built-in auth system).
PDFs contain structured text for extraction (e.g., expiry dates in recognizable formats).
Email server is configured for sending notifications.
Digital signatures are implemented using a simple canvas-based solution for MVP; production may require a third-party service like DocuSign.

9. Risks and Mitigation

PDF Parsing Errors: Mitigate by validating extracted data and allowing manual overrides.
Security: Use Django’s CSRF protection, validate uploads, and enforce HTTPS.
Scalability: Use Celery for background tasks and PostgreSQL for efficient querying.
AI Integration: Design the database to store clauses in a flexible format for future NLP processing.
