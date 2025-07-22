# MOU Management System

A comprehensive Django-based web application for managing Memoranda of Understanding (MOUs). This system provides a user-friendly interface to create, manage, track, and digitally sign MOUs with automated notifications and PDF processing capabilities.

## Features

### Core Features
- **Dashboard**: Overview of all MOUs with statistics and recent activities
- **MOU Management**: Create, edit, view, and delete MOUs
- **Digital Signatures**: External partners can sign MOUs via secure links
- **PDF Processing**: Automatic extraction of clauses and metadata from PDF documents
- **Activity Tracking**: Comprehensive logging of all MOU-related activities
- **Email Notifications**: Automated reminders for expiring MOUs
- **Secure Sharing**: Generate time-limited, secure links for external partners

### Advanced Features
- **Status Management**: Draft, Pending, Approved, Expired status workflow
- **Expiry Tracking**: Automatic alerts for MOUs expiring within 90 days
- **Partner Management**: Store partner contact information and organization details
- **File Management**: Secure PDF upload and storage
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Search & Filter**: Advanced filtering and search capabilities

## Technology Stack

- **Backend**: Django 4.2.7 (Python)
- **Database**: PostgreSQL (configurable to SQLite for development)
- **Task Queue**: Celery with Redis
- **PDF Processing**: pdfplumber, PyPDF2
- **Frontend**: Bootstrap 5, HTML5 Canvas for signatures
- **Email**: Django's email framework with SMTP support
- **File Storage**: Django FileField (local/cloud storage)

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite used by default)
- Redis (for Celery tasks)

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd mou_management_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration
Create a `.env` file in the root directory:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=mou_management
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# File Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
```

### Step 3: Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py create_sample_data
```

### Step 4: Run the Application
```bash
# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker (for background tasks)
celery -A mou_management worker --loglevel=info

# In another terminal, start Celery beat (for scheduled tasks)
celery -A mou_management beat --loglevel=info
```

The application will be available at `http://localhost:8000`

## Usage

### For Administrators

1. **Login**: Access the system at `http://localhost:8000` with your admin credentials
2. **Dashboard**: View overview of all MOUs, statistics, and recent activities
3. **Create MOU**: Click "Create New MOU" to add a new MOU with partner details
4. **Manage MOUs**: View, edit, approve/reject MOUs from the MOU list
5. **Generate Share Links**: Create secure links for partners to sign MOUs
6. **Monitor Activities**: Track all actions through activity logs

### For External Partners

1. **Access**: Receive a secure link from the organization
2. **Review**: View MOU details and download the PDF document
3. **Sign**: Fill in partner information and provide digital signature
4. **Submit**: Upload updated documents (if needed) and submit

## Key Models

### MOU Model
- Basic information (title, description, partner details)
- Status management (draft, pending, approved, expired)
- File storage for PDF documents
- Automatic expiry tracking
- JSON storage for extracted clauses

### Activity Log
- Comprehensive tracking of all MOU activities
- User identification (internal/external)
- IP address logging
- Detailed descriptions

### Share Link
- UUID-based secure tokens
- Expiration management
- Access count tracking
- Security controls

### Partner Submission
- Partner information collection
- Digital signature storage
- Updated document uploads
- Submission tracking

## Background Tasks

### Automated Email Reminders
- Daily checks for expiring MOUs
- Categorized notifications (urgent, warning, info)
- HTML and text email formats

### PDF Data Extraction
- Automatic clause extraction from uploaded PDFs
- Date recognition and parsing
- Structured data storage

### Status Management
- Automatic expiry status updates
- Share link cleanup
- Activity maintenance

## Security Features

- **Authentication**: Django's built-in authentication system
- **CSRF Protection**: Cross-site request forgery protection
- **Secure File Upload**: PDF validation and size limits
- **Token-based Access**: Time-limited, unique tokens for external access
- **IP Logging**: Activity tracking with IP addresses
- **HTTPS Ready**: Production-ready security configurations

## API Endpoints

The system provides RESTful URLs for all operations:
- `/` - Dashboard
- `/mous/` - MOU list with filtering/search
- `/mous/create/` - Create new MOU
- `/mous/<id>/` - MOU detail view
- `/mous/<id>/edit/` - Edit MOU
- `/sign/<token>/` - Public signing interface
- `/admin/` - Django admin interface

## Customization

### Email Templates
Customize email templates in `templates/emails/`:
- `expiry_reminder.html` - HTML email template
- `expiry_reminder.txt` - Plain text email template

### PDF Processing
Modify `mous/utils.py` to customize:
- Clause extraction patterns
- Date parsing formats
- Data extraction logic

### Frontend Styling
Update templates in `templates/` directory:
- Bootstrap 5 components
- Custom CSS in `static/css/`
- JavaScript enhancements

## Production Deployment

### Using Docker
```bash
# Build Docker image
docker build -t mou-management .

# Run with docker-compose
docker-compose up -d
```

### Manual Deployment
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up Nginx as reverse proxy
4. Use Gunicorn as WSGI server
5. Configure SSL certificates
6. Set up monitoring and logging

## Monitoring & Maintenance

### Health Checks
- Database connectivity
- Celery task queue status
- File storage accessibility
- Email service functionality

### Regular Tasks
- Database backups
- Log rotation
- Share link cleanup
- Performance monitoring

## Support & Documentation

### API Documentation
Access the admin interface at `/admin/` for model documentation and data management.

### Error Handling
- Comprehensive error logging
- User-friendly error pages
- Email notifications for critical errors

### Troubleshooting
- Check Django and Celery logs
- Verify database connections
- Ensure Redis is running
- Validate email configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Future Enhancements

### Planned Features
- AI-powered clause analysis
- Advanced search with full-text indexing
- Mobile application
- API for third-party integrations
- Advanced reporting and analytics
- Multi-language support

### AI Integration Roadmap
- Natural Language Processing for clause analysis
- Risk assessment and flagging
- Automated contract review
- Intelligent recommendations

---

For additional support or questions, please contact the development team or refer to the project documentation.
