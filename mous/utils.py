import re
import pdfplumber
from datetime import datetime
from django.utils import timezone
from .models import ActivityLog

# Import AI services with fallback
try:
    from .ai_services import analyze_mou_document
    HAS_AI_SERVICES = True
except ImportError:
    HAS_AI_SERVICES = False


def get_client_ip(request):
    """Get the client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def extract_pdf_data(pdf_path):
    """Extract text and key information from PDF with optional AI analysis"""
    extracted_data = {
        'full_text': '',
        'clauses': [],
        'dates': [],
        'extracted_expiry_date': None,
        'ai_analysis': None
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
            
            # Perform AI analysis if available
            if HAS_AI_SERVICES and full_text.strip():
                try:
                    ai_result = analyze_mou_document(full_text)
                    extracted_data['ai_analysis'] = ai_result
                except Exception as ai_error:
                    extracted_data['ai_analysis'] = {
                        'error': str(ai_error),
                        'overall_risk_score': 5.0,  # Default medium risk
                        'recommendations': ['AI analysis unavailable - manual review recommended']
                    }
            
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
    
    # Add AI analysis summary if available
    if hasattr(mou, 'ai_analysis') and mou.ai_analysis:
        ai_analysis = mou.ai_analysis
        summary['ai_risk_score'] = float(ai_analysis.overall_risk_score) if ai_analysis.overall_risk_score else None
        summary['ai_risk_level'] = ai_analysis.risk_level
        summary['compliance_status'] = ai_analysis.get_compliance_status_display()
        summary['high_risk_clauses'] = ai_analysis.get_high_risk_clauses().count()
        summary['total_recommendations'] = len(ai_analysis.recommendations) if ai_analysis.recommendations else 0
    
    return summary


def create_ai_analysis_from_data(mou, ai_data):
    """
    Create AIAnalysis and related objects from AI analysis data
    
    Args:
        mou: MOU instance
        ai_data: Dictionary containing AI analysis results
    
    Returns:
        AIAnalysis instance
    """
    if not HAS_AI_SERVICES:
        return None
    
    # Import here to avoid circular imports
    from .ai_models import AIAnalysis, ClauseAnalysis, RiskFlag
    
    try:
        # Create or update AI analysis
        ai_analysis, created = AIAnalysis.objects.get_or_create(
            mou=mou,
            defaults={
                'overall_risk_score': ai_data.get('overall_risk_score', 0),
                'compliance_status': ai_data.get('compliance_status', 'pending'),
                'analysis_data': ai_data,
                'recommendations': ai_data.get('recommendations', []),
                'compliance_flags': ai_data.get('compliance_flags', []),
                'summary_stats': ai_data.get('summary_stats', {}),
                'status': 'completed'
            }
        )
        
        if not created:
            # Update existing analysis
            ai_analysis.overall_risk_score = ai_data.get('overall_risk_score', ai_analysis.overall_risk_score)
            ai_analysis.compliance_status = ai_data.get('compliance_status', ai_analysis.compliance_status)
            ai_analysis.analysis_data = ai_data
            ai_analysis.recommendations = ai_data.get('recommendations', [])
            ai_analysis.compliance_flags = ai_data.get('compliance_flags', [])
            ai_analysis.summary_stats = ai_data.get('summary_stats', {})
            ai_analysis.status = 'completed'
            ai_analysis.save()
        
        # Clear existing clause analyses
        ai_analysis.clauses.all().delete()
        
        # Create clause analyses
        for clause_data in ai_data.get('clauses', []):
            ClauseAnalysis.objects.create(
                ai_analysis=ai_analysis,
                clause_text=clause_data.get('text', ''),
                clause_type=clause_data.get('type', 'unknown'),
                confidence_score=clause_data.get('confidence', 0),
                risk_score=clause_data.get('risk_score', 0),
                sentiment=clause_data.get('sentiment', 'neutral'),
                risk_factors=clause_data.get('risk_factors', []),
                suggestions=clause_data.get('suggestions', []),
                key_terms=clause_data.get('key_terms', [])
            )
        
        # Create risk flags for high-risk items
        create_risk_flags_from_analysis(mou, ai_analysis, ai_data)
        
        return ai_analysis
        
    except Exception as e:
        # Log error but don't fail
        print(f"Error creating AI analysis: {str(e)}")
        return None


def create_risk_flags_from_analysis(mou, ai_analysis, ai_data):
    """Create RiskFlag objects from AI analysis results"""
    if not HAS_AI_SERVICES:
        return
    
    from .ai_models import RiskFlag
    
    # Clear existing unresolved risk flags
    RiskFlag.objects.filter(mou=mou, is_resolved=False).delete()
    
    # Create flags for high-risk clauses
    for clause_analysis in ai_analysis.clauses.filter(risk_score__gt=7):
        for risk_factor in clause_analysis.risk_factors:
            severity = 'high' if clause_analysis.risk_score > 8 else 'medium'
            
            RiskFlag.objects.create(
                mou=mou,
                clause_analysis=clause_analysis,
                flag_type='legal_risk',
                severity=severity,
                title=f"High-risk {clause_analysis.clause_type} clause",
                description=f"Risk factor identified: {risk_factor}",
                confidence_score=clause_analysis.confidence_score
            )
    
    # Create flags for overall document issues
    if ai_analysis.overall_risk_score and ai_analysis.overall_risk_score > 8:
        RiskFlag.objects.create(
            mou=mou,
            flag_type='legal_risk',
            severity='critical',
            title="Overall high-risk document",
            description=f"Document has overall risk score of {ai_analysis.overall_risk_score}/10",
            confidence_score=0.9
        )
    
    # Create compliance flags
    if ai_analysis.compliance_status == 'non_compliant':
        RiskFlag.objects.create(
            mou=mou,
            flag_type='compliance_risk',
            severity='high',
            title="Compliance issues detected",
            description="Document may not meet compliance requirements",
            confidence_score=0.8
        )


def get_ai_insights_for_dashboard():
    """Get AI-powered insights for dashboard display"""
    if not HAS_AI_SERVICES:
        return {}
    
    from .ai_models import AIAnalysis, RiskFlag
    from django.db.models import Avg, Count
    
    try:
        insights = {
            'total_analyses': AIAnalysis.objects.count(),
            'avg_risk_score': AIAnalysis.objects.aggregate(
                avg_score=Avg('overall_risk_score')
            )['avg_score'] or 0,
            'high_risk_documents': AIAnalysis.objects.filter(overall_risk_score__gt=7).count(),
            'compliance_issues': AIAnalysis.objects.filter(compliance_status='non_compliant').count(),
            'unresolved_flags': RiskFlag.objects.filter(is_resolved=False).count(),
            'recent_high_risk': AIAnalysis.objects.filter(
                overall_risk_score__gt=7,
                analysis_date__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()
        }
        
        return insights
        
    except Exception as e:
        print(f"Error getting AI insights: {str(e)}")
        return {}


def schedule_ai_reanalysis(mou):
    """Schedule AI reanalysis for an MOU (for use with Celery)"""
    if not HAS_AI_SERVICES:
        return False
    
    # Import here to avoid circular imports
    from .tasks import analyze_mou_with_ai
    
    try:
        # Schedule background task for AI analysis
        analyze_mou_with_ai.delay(mou.id)
        return True
    except Exception as e:
        print(f"Error scheduling AI analysis: {str(e)}")
        return False
