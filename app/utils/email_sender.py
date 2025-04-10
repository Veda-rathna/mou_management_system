import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from flask import render_template, current_app, url_for
import threading
import time
import schedule

from app import db
from app.models.mou import MOU
from app.config import Config

def send_email(subject, recipient, html_body):
    """
    Send an email using SMTP
    """
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = Config.MAIL_DEFAULT_SENDER
    msg['To'] = recipient
    
    # Attach HTML content
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        
        # Send the email
        server.sendmail(Config.MAIL_DEFAULT_SENDER, recipient, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_upload_link_email(mou):
    """
    Send an email with the upload link to the partner organization
    """
    subject = f"MOU Upload Link - {mou.title}"
    recipient = mou.party_b.email
    
    # Generate the upload URL
    upload_url = url_for('upload.upload_mou', link_id=mou.upload_link_id, _external=True)
    
    # Render the email template
    html_body = render_template(
        'email/upload_link.html',
        mou=mou,
        upload_url=upload_url,
        expiry_date=mou.link_expiry.strftime('%Y-%m-%d %H:%M:%S')
    )
    
    return send_email(subject, recipient, html_body)

def send_expiry_reminder(mou):
    """
    Send a reminder email for MOUs that are about to expire
    """
    subject = f"MOU Expiry Reminder - {mou.title}"
    recipient = mou.party_a.email
    
    # Render the email template
    html_body = render_template(
        'email/expiry_reminder.html',
        mou=mou,
        days_remaining=mou.days_until_expiry()
    )
    
    # Also send to party B
    send_email(subject, mou.party_b.email, html_body)
    
    return send_email(subject, recipient, html_body)

def check_expiring_mous():
    """
    Check for MOUs that are about to expire and send reminders
    """
    # Calculate the date for MOUs expiring in the configured number of days
    reminder_date = datetime.now().date() + timedelta(days=Config.REMINDER_DAYS_BEFORE_EXPIRY)
    
    # Find MOUs expiring on that date
    expiring_mous = MOU.query.filter(
        MOU.end_date == reminder_date,
        MOU.status == 'active'
    ).all()
    
    # Send reminders
    for mou in expiring_mous:
        send_expiry_reminder(mou)
        
        # Log the reminder
        from app.models.audit import AuditLog
        audit_log = AuditLog(
            mou_id=mou.id,
            action='expiry_reminder',
            details=f'Sent expiry reminder email'
        )
        db.session.add(audit_log)
    
    db.session.commit()

def run_scheduler():
    """
    Run the scheduler in a separate thread
    """
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def schedule_expiry_reminders():
    """
    Schedule the daily check for expiring MOUs
    """
    # Schedule the check to run daily at midnight
    schedule.every().day.at("00:00").do(check_expiring_mous)
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
