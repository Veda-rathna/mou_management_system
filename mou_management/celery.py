import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mou_management.settings')

app = Celery('mou_management')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'send-expiry-reminders': {
        'task': 'mous.tasks.send_expiry_reminder',
        'schedule': 86400.0,  # Run daily (24 hours)
        'options': {'expires': 3600}  # Task expires after 1 hour
    },
    'update-expired-mous': {
        'task': 'mous.tasks.update_expired_mous',
        'schedule': 43200.0,  # Run twice daily (12 hours)
        'options': {'expires': 1800}  # Task expires after 30 minutes
    },
    'cleanup-expired-share-links': {
        'task': 'mous.tasks.cleanup_expired_share_links',
        'schedule': 86400.0,  # Run daily (24 hours)
        'options': {'expires': 1800}  # Task expires after 30 minutes
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
