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

### 🤖 AI-Powered Clause Analysis
- **Intelligent Risk Scoring**: Automated risk assessment (0-10 scale) for each MOU
- **Clause-by-Clause Analysis**: Detailed analysis of contract clauses (liability, termination, IP, etc.)
- **Risk Flag Detection**: Automatic identification of high-risk terms and missing clauses
- **Compliance Assessment**: Automated compliance status determination
- **Smart Recommendations**: AI-generated suggestions for contract improvement
- **BERT Model Integration**: Uses pre-trained transformer models for legal text analysis
- **Confidence Scoring**: Transparency in AI decision-making with confidence levels
- **Bulk Processing**: Analyze multiple MOUs simultaneously

## Technology Stack

- **Backend**: Django 4.2.7 (Python)
- **Database**: PostgreSQL (configurable to SQLite for development)
- **Task Queue**: Celery with Redis
- **PDF Processing**: pdfplumber, PyPDF2
- **AI/ML**: Transformers, PyTorch, Sentence-Transformers, spaCy (optional)
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

### Step 4: AI Analysis Setup (Optional)

The system includes an AI-powered clause analysis feature that uses BERT models for intelligent contract analysis. This feature can be enabled for enhanced MOU analysis capabilities.

#### Enable AI Analysis
```bash
# Install AI dependencies
pip install -r requirements_ai.txt

# Or install manually:
pip install transformers>=4.21.0 torch>=1.12.0 sentence-transformers>=2.2.2 spacy>=3.4.0

# Download spaCy English model
python -m spacy download en_core_web_sm

# Setup AI analysis system
python manage.py setup_ai_analysis --install-deps --download-models --test-analysis

# Create sample AI analysis data for testing
python manage.py create_sample_ai_data
```

#### Run AI Analysis on Existing MOUs
```bash
# Analyze specific MOU by ID
python manage.py analyze_existing_mous --mou-id 1

# Analyze first 10 MOUs without analysis
python manage.py analyze_existing_mous --limit 10

# Analyze all MOUs (use with caution for large datasets)
python manage.py analyze_existing_mous --all

# Force re-analysis of MOUs that already have analysis
python manage.py analyze_existing_mous --force --limit 5
```

#### AI Analysis Features
- **Risk Scoring**: Automated risk assessment on a 0-10 scale
- **Clause Analysis**: Individual analysis of contract sections
- **Risk Flags**: Identification of problematic clauses
- **Compliance Check**: Automated compliance status determination
- **Recommendations**: AI-generated improvement suggestions

#### System Requirements for AI
- **RAM**: Minimum 8GB (16GB recommended for BERT models)
- **Storage**: Additional 2-5GB for model files
- **Processing**: Background analysis via Celery workers

> **Note**: The system works fully without AI dependencies. AI analysis is an optional enhancement that can be enabled later.

### Step 5: Run the Application
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

#### 🤖 AI Analysis Features (If Enabled)

7. **View AI Analysis**: MOUs display risk levels, compliance status, and detailed analysis
8. **Risk Assessment**: Each MOU shows color-coded risk levels (Low/Medium/High)
9. **Clause Analysis**: Detailed breakdown of individual contract clauses
10. **Risk Flags**: Automatic identification of problematic terms
11. **Bulk Analysis**: Use "Analyze All MOUs" button for batch processing
12. **Manual Trigger**: Click "Run AI Analysis" on individual MOUs

**AI Analysis Dashboard Features:**
- Overall risk score with visual indicators (0-10 scale)
- Compliance status badges (Compliant, Review Required, Non-Compliant)
- Individual clause risk assessment
- Risk flags with severity levels (Low, Medium, High, Critical)
- AI-generated recommendations for contract improvement
- Analysis metadata (confidence scores, model version, processing time)

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

### 🤖 AI Analysis Models

#### AIAnalysis Model
- Links to MOU with one-to-one relationship
- Overall risk score (0-10) with automatic risk level calculation
- Compliance status tracking (Compliant/Review Required/Non-Compliant)
- JSON storage for detailed analysis data and recommendations
- Processing metadata (model version, processing time, confidence scores)
- Support for model versioning and analysis history

#### ClauseAnalysis Model
- Individual clause analysis with clause type classification
- Risk scoring and confidence assessment for each clause
- Support for various clause types (liability, termination, IP, confidentiality, etc.)
- Position tracking within documents
- Risk factor identification and improvement suggestions
- Similar clause references and key term extraction

#### RiskFlag Model
- Specific risk identification with severity classification
- Multiple risk types (legal, financial, compliance, operational, reputational)
- Flag resolution tracking with user assignment
- Confidence scoring for AI-generated flags
- Support for manual flag creation and management

#### AIModelMetrics Model
- Performance tracking for AI models
- Daily analysis statistics and processing metrics
- Success/failure rate monitoring
- Confidence score aggregation
- System performance optimization data

## 🧠 AI Architecture & BERT Integration

### AI Processing Pipeline
1. **PDF Text Extraction**: Extract and preprocess text from uploaded MOUs
2. **Clause Segmentation**: Intelligent identification and categorization of contract clauses
3. **BERT Analysis**: Use pre-trained transformer models for text classification
4. **Risk Assessment**: Multi-factor risk scoring algorithm
5. **Compliance Check**: Rule-based compliance validation
6. **Flag Generation**: Automatic identification of problematic terms
7. **Recommendation Engine**: AI-powered suggestions for improvement

### BERT Models Used
- **Primary Model**: `nlpaueb/legal-bert-base-uncased` for legal text understanding
- **Fallback Model**: `bert-base-uncased` for general text classification
- **Sentence Embeddings**: `all-MiniLM-L6-v2` for clause similarity analysis
- **Named Entity Recognition**: spaCy `en_core_web_sm` for entity extraction

### AI Features Implementation
```python
# Example AI analysis trigger
from mous.tasks import analyze_mou_with_ai

# Analyze single MOU
result = analyze_mou_with_ai.delay(mou_id=1)

# Bulk analysis
from mous.management.commands.analyze_existing_mous import Command
command = Command()
command.handle(all=True, limit=50)
```

### Performance Considerations
- **Model Caching**: Models cached in memory for faster processing
- **Background Processing**: All AI analysis runs via Celery workers
- **Batch Processing**: Optimized for analyzing multiple MOUs
- **Fallback Mechanisms**: Graceful degradation when AI libraries unavailable
- **Resource Management**: Configurable memory limits and processing timeouts

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

## AI-Powered Clause Analysis Integration

### Implementation Strategy

The AI-powered clause analysis feature enhances the MOU management system with intelligent document processing, risk assessment, and automated insights.

#### Phase 1: Basic NLP Integration
```python
# AI Dependencies to add to requirements.txt
transformers>=4.21.0
torch>=1.12.0
spacy>=3.4.0
nltk>=3.7
sentence-transformers>=2.2.2
openai>=0.27.0  # Optional: For GPT integration
```

#### Phase 2: Core AI Features

##### 1. Clause Classification & Extraction
- **Technology**: BERT-based models for legal text classification
- **Purpose**: Automatically identify and categorize different types of clauses
- **Implementation**: 
  ```python
  # Example clause categories
  CLAUSE_TYPES = {
      'termination': 'Termination and cancellation clauses',
      'payment': 'Payment and financial obligations',
      'liability': 'Liability and indemnification',
      'confidentiality': 'Non-disclosure and confidentiality',
      'intellectual_property': 'IP rights and licensing',
      'dispute_resolution': 'Dispute resolution mechanisms',
      'governing_law': 'Governing law and jurisdiction',
      'force_majeure': 'Force majeure provisions',
  }
  ```

##### 2. Risk Assessment Engine
- **Scoring System**: 1-10 risk scale for each clause type
- **Risk Factors**:
  - Unusual termination conditions
  - Unlimited liability exposure
  - Vague performance metrics
  - Missing dispute resolution
  - Unfavorable payment terms
- **Output**: Risk dashboard with actionable recommendations

##### 3. Semantic Search & Similarity Analysis
- **Technology**: Sentence transformers for semantic embeddings
- **Features**:
  - Find similar clauses across MOUs
  - Identify inconsistencies in standard terms
  - Suggest clause improvements based on best practices

#### Phase 3: Advanced AI Features

##### 1. Intelligent Clause Recommendations
```python
class ClauseRecommendationEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_base = self.load_clause_templates()
    
    def suggest_improvements(self, clause_text, clause_type):
        # Analyze clause and suggest improvements
        similarity_scores = self.compare_with_best_practices(clause_text)
        return self.generate_recommendations(similarity_scores, clause_type)
```

##### 2. Contract Compliance Checker
- **Regulatory Compliance**: Check against industry standards
- **Internal Policy**: Validate against company policies
- **Template Adherence**: Ensure consistency with approved templates

##### 3. Automated Risk Flagging
- **Real-time Analysis**: Flag high-risk clauses during document upload
- **Priority Scoring**: Categorize risks by urgency and impact
- **Approval Workflows**: Route high-risk MOUs for additional review

### Technical Implementation

#### 1. AI Service Architecture
```python
# mous/ai_services.py
from typing import Dict, List, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class ClauseAnalyzer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('nlpaueb/legal-bert-base-uncased')
        self.model = AutoModelForSequenceClassification.from_pretrained('nlpaueb/legal-bert-base-uncased')
        self.clause_embeddings = {}
    
    def analyze_document(self, pdf_text: str) -> Dict:
        """Comprehensive document analysis"""
        clauses = self.extract_clauses(pdf_text)
        analysis = {
            'clauses': [],
            'risk_score': 0,
            'recommendations': [],
            'compliance_status': 'pending'
        }
        
        for clause in clauses:
            clause_analysis = self.analyze_clause(clause)
            analysis['clauses'].append(clause_analysis)
            analysis['risk_score'] += clause_analysis['risk_score']
        
        analysis['risk_score'] = min(analysis['risk_score'] / len(clauses), 10)
        analysis['recommendations'] = self.generate_recommendations(analysis)
        
        return analysis
    
    def analyze_clause(self, clause_text: str) -> Dict:
        """Individual clause analysis"""
        # Tokenize and analyze
        inputs = self.tokenizer(clause_text, return_tensors="pt", max_length=512, truncation=True)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Extract insights
        clause_type = self.classify_clause_type(clause_text)
        risk_factors = self.identify_risk_factors(clause_text, clause_type)
        
        return {
            'text': clause_text,
            'type': clause_type,
            'confidence': float(torch.max(predictions)),
            'risk_score': self.calculate_risk_score(risk_factors),
            'risk_factors': risk_factors,
            'suggestions': self.generate_clause_suggestions(clause_text, clause_type)
        }
```

#### 2. Database Schema Extensions
```python
# New AI-related models
class AIAnalysis(models.Model):
    mou = models.OneToOneField(MOU, on_delete=models.CASCADE, related_name='ai_analysis')
    overall_risk_score = models.DecimalField(max_digits=3, decimal_places=1)
    analysis_date = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=50)
    analysis_data = models.JSONField(default=dict)  # Store full analysis
    recommendations = models.JSONField(default=list)
    compliance_flags = models.JSONField(default=list)

class ClauseAnalysis(models.Model):
    ai_analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE, related_name='clauses')
    clause_text = models.TextField()
    clause_type = models.CharField(max_length=50)
    confidence_score = models.DecimalField(max_digits=4, decimal_places=3)
    risk_score = models.DecimalField(max_digits=3, decimal_places=1)
    risk_factors = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    start_position = models.IntegerField(null=True, blank=True)
    end_position = models.IntegerField(null=True, blank=True)

class RiskFlag(models.Model):
    mou = models.ForeignKey(MOU, on_delete=models.CASCADE, related_name='risk_flags')
    flag_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    description = models.TextField()
    clause_reference = models.ForeignKey(ClauseAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 3. Integration with Existing Workflow
```python
# Enhanced PDF processing with AI
def extract_pdf_data_with_ai(pdf_path):
    """Enhanced PDF extraction with AI analysis"""
    # Existing PDF extraction
    basic_data = extract_pdf_data(pdf_path)
    
    # AI Analysis
    analyzer = ClauseAnalyzer()
    ai_analysis = analyzer.analyze_document(basic_data['text'])
    
    # Combine results
    enhanced_data = {
        **basic_data,
        'ai_analysis': ai_analysis,
        'risk_score': ai_analysis['risk_score'],
        'compliance_status': ai_analysis['compliance_status']
    }
    
    return enhanced_data
```

### User Interface Enhancements

#### 1. AI Analysis Dashboard
- **Risk Overview**: Visual risk score with color-coded indicators
- **Clause Breakdown**: Interactive clause explorer with risk highlighting
- **Recommendations Panel**: Actionable insights and suggestions
- **Compliance Checker**: Status indicators for various compliance requirements

#### 2. Enhanced MOU Detail View
```html
<!-- AI Analysis Section -->
<div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">AI Analysis Results</h6>
        <span class="badge bg-{{ risk_color }}">Risk Score: {{ mou.ai_analysis.overall_risk_score }}/10</span>
    </div>
    <div class="card-body">
        <!-- Risk factors, recommendations, compliance status -->
    </div>
</div>
```

### Implementation Phases

#### Phase 1 (2-4 weeks): Foundation
1. Set up AI infrastructure (models, dependencies)
2. Implement basic clause extraction and classification
3. Create AI analysis database models
4. Build basic risk scoring

#### Phase 2 (4-6 weeks): Core Features
1. Develop comprehensive clause analysis
2. Implement risk assessment engine
3. Create recommendation system
4. Build AI dashboard interface

#### Phase 3 (6-8 weeks): Advanced Features
1. Add semantic search capabilities
2. Implement compliance checking
3. Build advanced analytics and reporting
4. Optimize performance and accuracy

### Future Enhancements

### Planned Features
- Advanced search with full-text indexing
- Mobile application
- API for third-party integrations
- Advanced reporting and analytics
- Multi-language support
- Blockchain integration for immutable audit trails
- Voice-to-text clause dictation
- Real-time collaboration features

### AI Integration Roadmap
- **GPT Integration**: Advanced natural language understanding
- **Computer Vision**: OCR improvements for scanned documents
- **Predictive Analytics**: Forecast contract outcomes
- **Automated Negotiation**: AI-assisted clause negotiation
- **Legal Research**: Integration with legal databases
- **Multi-language Analysis**: Support for international contracts

---

For additional support or questions, please contact the development team or refer to the project documentation.
