from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime
from .models import MOU, ActivityLog
from .utils import generate_mou_summary, create_ai_analysis_from_data
import logging

# Import AI services if available
try:
    from .ai_services import analyze_mou_document
    HAS_AI_SERVICES = True
except ImportError:
    HAS_AI_SERVICES = False

logger = logging.getLogger(__name__)


@shared_task
def send_expiry_reminder():
    """
    Celery task to send email reminders for MOUs expiring within 90 days
    """
    try:
        # Calculate the date 90 days from now
        ninety_days_later = timezone.now().date() + timedelta(days=90)
        
        # Get MOUs that expire within 90 days and are approved
        expiring_mous = MOU.objects.filter(
            expiry_date__lte=ninety_days_later,
            expiry_date__gte=timezone.now().date(),
            status='approved'
        )
        
        if not expiring_mous.exists():
            logger.info("No MOUs expiring within 90 days found.")
            return f"No MOUs expiring within 90 days."
        
        # Group MOUs by expiry timeframe
        urgent_mous = []  # Expiring within 30 days
        warning_mous = []  # Expiring within 30-60 days
        info_mous = []  # Expiring within 60-90 days
        
        for mou in expiring_mous:
            days_until_expiry = (mou.expiry_date - timezone.now().date()).days
            
            if days_until_expiry <= 30:
                urgent_mous.append(mou)
            elif days_until_expiry <= 60:
                warning_mous.append(mou)
            else:
                info_mous.append(mou)
        
        # Prepare email content
        context = {
            'urgent_mous': urgent_mous,
            'warning_mous': warning_mous,
            'info_mous': info_mous,
            'total_count': len(expiring_mous),
            'current_date': timezone.now().date()
        }
        
        # Render email template
        html_message = render_to_string('emails/expiry_reminder.html', context)
        plain_message = render_to_string('emails/expiry_reminder.txt', context)
        
        # Send email to administrators
        recipient_list = [settings.EMAIL_HOST_USER] if settings.EMAIL_HOST_USER else ['admin@example.com']
        
        send_mail(
            subject=f'MOU Expiry Reminder - {len(expiring_mous)} MOUs expiring soon',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@moumanagement.com',
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Expiry reminder sent for {len(expiring_mous)} MOUs")
        return f"Expiry reminder sent for {len(expiring_mous)} MOUs"
        
    except Exception as e:
        logger.error(f"Error sending expiry reminder: {str(e)}")
        return f"Error sending expiry reminder: {str(e)}"


@shared_task
def extract_mou_data_task(mou_id):
    """
    Background task to extract data from MOU PDF
    """
    try:
        from .utils import extract_pdf_data
        
        mou = MOU.objects.get(id=mou_id)
        
        if mou.pdf_file:
            extracted_data = extract_pdf_data(mou.pdf_file.path)
            mou.clauses = extracted_data
            mou.save()
            
            # Log activity
            ActivityLog.objects.create(
                mou=mou,
                action='pdf_processed',
                description=f"PDF data extraction completed. Found {len(extracted_data.get('clauses', []))} clauses."
            )
            
            logger.info(f"PDF data extracted for MOU {mou.id}")
            return f"PDF data extracted successfully for MOU {mou.id}"
        else:
            return f"No PDF file found for MOU {mou.id}"
            
    except MOU.DoesNotExist:
        error_msg = f"MOU with id {mou_id} does not exist"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error extracting PDF data for MOU {mou_id}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def update_expired_mous():
    """
    Task to automatically update status of expired MOUs
    """
    try:
        expired_mous = MOU.objects.filter(
            expiry_date__lt=timezone.now().date(),
            status='approved'
        )
        
        count = 0
        for mou in expired_mous:
            mou.status = 'expired'
            mou.save()
            
            # Log activity
            ActivityLog.objects.create(
                mou=mou,
                action='auto_expired',
                description="Automatically marked as expired due to expiry date"
            )
            count += 1
        
        if count > 0:
            logger.info(f"Updated {count} MOUs to expired status")
        
        return f"Updated {count} MOUs to expired status"
        
    except Exception as e:
        error_msg = f"Error updating expired MOUs: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def send_custom_notification(mou_id, recipient_email, subject, message):
    """
    Send custom notification email for specific MOU
    """
    try:
        mou = MOU.objects.get(id=mou_id)
        
        context = {
            'mou': mou,
            'mou_summary': generate_mou_summary(mou),
            'custom_message': message
        }
        
        html_message = render_to_string('emails/custom_notification.html', context)
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@moumanagement.com',
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Log activity
        ActivityLog.objects.create(
            mou=mou,
            action='notification_sent',
            description=f"Custom notification sent to {recipient_email}"
        )
        
        logger.info(f"Custom notification sent for MOU {mou.id} to {recipient_email}")
        return f"Notification sent successfully to {recipient_email}"
        
    except MOU.DoesNotExist:
        error_msg = f"MOU with id {mou_id} does not exist"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error sending notification: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def cleanup_expired_share_links():
    """
    Clean up expired share links
    """
    try:
        from .models import ShareLink
        
        expired_links = ShareLink.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        
        count = expired_links.count()
        expired_links.update(is_active=False)
        
        logger.info(f"Deactivated {count} expired share links")
        return f"Deactivated {count} expired share links"
        
    except Exception as e:
        error_msg = f"Error cleaning up expired share links: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def analyze_mou_with_ai(mou_id):
    """
    Celery task to perform AI analysis on an MOU document
    
    Args:
        mou_id: ID of the MOU to analyze
        
    Returns:
        String indicating success or failure
    """
    if not HAS_AI_SERVICES:
        return "AI services not available"
    
    try:
        from time import time
        start_time = time()
        
        # Get the MOU
        mou = MOU.objects.get(id=mou_id)
        
        # Check if PDF file exists and is readable
        if not mou.pdf_file:
            return f"No PDF file found for MOU {mou_id}"
        
        # Extract text from PDF
        from .utils import extract_pdf_data
        pdf_data = extract_pdf_data(mou.pdf_file.path)
        
        if not pdf_data.get('full_text'):
            return f"Could not extract text from PDF for MOU {mou_id}"
        
        # Perform AI analysis
        ai_result = analyze_mou_document(pdf_data['full_text'], mou.title)
        
        # Calculate processing time
        processing_time = time() - start_time
        ai_result['processing_time'] = processing_time
        
        # Create AI analysis record
        ai_analysis = create_ai_analysis_from_data(mou, ai_result)
        
        if ai_analysis:
            ai_analysis.processing_time_seconds = processing_time
            ai_analysis.save()
            
            # Log activity
            ActivityLog.objects.create(
                mou=mou,
                action='ai_analyzed',
                description=f"AI analysis completed with risk score: {ai_result.get('overall_risk_score', 'N/A')}"
            )
            
            # Send notification if high risk detected
            if ai_result.get('overall_risk_score', 0) > 8:
                send_high_risk_notification.delay(mou_id)
            
            logger.info(f"AI analysis completed for MOU {mou_id} in {processing_time:.2f} seconds")
            return f"AI analysis completed successfully for MOU {mou_id}"
        else:
            return f"Failed to save AI analysis for MOU {mou_id}"
        
    except MOU.DoesNotExist:
        error_msg = f"MOU with ID {mou_id} not found"
        logger.error(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"Error analyzing MOU {mou_id}: {str(e)}"
        logger.error(error_msg)
        
        # Update AI analysis status to failed if it exists
        try:
            from .ai_models import AIAnalysis
            ai_analysis, created = AIAnalysis.objects.get_or_create(
                mou_id=mou_id,
                defaults={'status': 'failed', 'error_message': str(e)}
            )
            if not created:
                ai_analysis.status = 'failed'
                ai_analysis.error_message = str(e)
                ai_analysis.save()
        except Exception:
            pass  # Don't fail if we can't update the status
        
        return error_msg


@shared_task
def send_high_risk_notification(mou_id):
    """
    Send notification when high-risk MOU is detected
    
    Args:
        mou_id: ID of the high-risk MOU
    """
    try:
        mou = MOU.objects.get(id=mou_id)
        
        # Check if MOU has AI analysis
        if not hasattr(mou, 'ai_analysis') or not mou.ai_analysis:
            return f"No AI analysis found for MOU {mou_id}"
        
        ai_analysis = mou.ai_analysis
        
        # Prepare email context
        context = {
            'mou': mou,
            'ai_analysis': ai_analysis,
            'risk_score': ai_analysis.overall_risk_score,
            'risk_level': ai_analysis.risk_level,
            'recommendations': ai_analysis.recommendations,
            'high_risk_clauses': ai_analysis.get_high_risk_clauses(),
            'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'
        }
        
        # Send email to relevant users (admin, legal team, etc.)
        subject = f"High-Risk MOU Detected: {mou.title}"
        
        # HTML email
        html_message = render_to_string('emails/high_risk_notification.html', context)
        
        # Plain text email
        text_message = render_to_string('emails/high_risk_notification.txt', context)
        
        # Get recipient emails (you can customize this based on your needs)
        recipients = []
        if mou.created_by and mou.created_by.email:
            recipients.append(mou.created_by.email)
        
        # Add admin emails
        from django.contrib.auth.models import User
        admin_emails = User.objects.filter(is_staff=True, email__isnull=False).values_list('email', flat=True)
        recipients.extend(admin_emails)
        
        if recipients:
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=list(set(recipients))  # Remove duplicates
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            # Log activity
            ActivityLog.objects.create(
                mou=mou,
                action='high_risk_alert_sent',
                description=f"High-risk notification sent to {len(recipients)} recipients"
            )
            
            logger.info(f"High-risk notification sent for MOU {mou_id} to {len(recipients)} recipients")
            return f"High-risk notification sent successfully for MOU {mou_id}"
        else:
            return f"No recipients found for high-risk notification of MOU {mou_id}"
        
    except MOU.DoesNotExist:
        error_msg = f"MOU with ID {mou_id} not found"
        logger.error(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"Error sending high-risk notification for MOU {mou_id}: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def batch_analyze_mous():
    """
    Batch analyze all MOUs that don't have AI analysis yet
    """
    if not HAS_AI_SERVICES:
        return "AI services not available"
    
    try:
        # Find MOUs without AI analysis
        mous_without_analysis = MOU.objects.filter(ai_analysis__isnull=True, pdf_file__isnull=False)
        
        count = 0
        for mou in mous_without_analysis[:10]:  # Limit to 10 at a time to avoid overload
            analyze_mou_with_ai.delay(mou.id)
            count += 1
        
        logger.info(f"Scheduled AI analysis for {count} MOUs")
        return f"Scheduled AI analysis for {count} MOUs"
        
    except Exception as e:
        error_msg = f"Error in batch AI analysis: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def update_ai_model_metrics():
    """
    Update AI model performance metrics
    """
    if not HAS_AI_SERVICES:
        return "AI services not available"
    
    try:
        from .ai_models import AIModelMetrics, AIAnalysis
        from django.db.models import Avg, Count, Sum
        from datetime import date
        
        # Get today's metrics
        today = date.today()
        model_version = "1.0.0"  # You can make this dynamic
        
        # Calculate metrics for today
        today_analyses = AIAnalysis.objects.filter(analysis_date__date=today)
        
        metrics, created = AIModelMetrics.objects.get_or_create(
            date=today,
            model_version=model_version,
            defaults={
                'documents_analyzed': today_analyses.count(),
                'clauses_analyzed': sum(a.clauses.count() for a in today_analyses),
                'total_processing_time': sum(float(a.processing_time_seconds or 0) for a in today_analyses),
                'average_confidence': today_analyses.aggregate(
                    avg_conf=Avg('clauses__confidence_score')
                )['avg_conf'] or 0,
                'high_risk_flags_generated': sum(a.risk_flags.filter(severity='high').count() for a in today_analyses),
                'analysis_failures': AIAnalysis.objects.filter(
                    analysis_date__date=today,
                    status='failed'
                ).count()
            }
        )
        
        if not created:
            # Update existing metrics
            metrics.documents_analyzed = today_analyses.count()
            metrics.clauses_analyzed = sum(a.clauses.count() for a in today_analyses)
            metrics.total_processing_time = sum(float(a.processing_time_seconds or 0) for a in today_analyses)
            metrics.average_confidence = today_analyses.aggregate(
                avg_conf=Avg('clauses__confidence_score')
            )['avg_conf'] or 0
            metrics.high_risk_flags_generated = sum(a.risk_flags.filter(severity='high').count() for a in today_analyses)
            metrics.analysis_failures = AIAnalysis.objects.filter(
                analysis_date__date=today,
                status='failed'
            ).count()
            metrics.save()
        
        logger.info(f"Updated AI model metrics for {today}")
        return f"Updated AI model metrics for {today}"
        
    except Exception as e:
        error_msg = f"Error updating AI model metrics: {str(e)}"
        logger.error(error_msg)
        return error_msg
