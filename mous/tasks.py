from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime
from .models import MOU, ActivityLog
from .utils import generate_mou_summary
import logging

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
