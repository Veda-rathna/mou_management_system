from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
from datetime import datetime, timedelta


class MOU(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('expired', 'Expired'),
    )
    
    title = models.CharField(max_length=255)
    partner_name = models.CharField(max_length=255)
    partner_organization = models.CharField(max_length=255, blank=True, null=True)
    partner_contact = models.EmailField(blank=True, null=True)
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    pdf_file = models.FileField(upload_to='mous/')
    clauses = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_mous')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'MOU'
        verbose_name_plural = 'MOUs'

    def __str__(self):
        return f"{self.title} - {self.partner_name}"

    def get_absolute_url(self):
        return reverse('mous:mou_detail', kwargs={'pk': self.pk})

    @property
    def is_expired(self):
        return self.expiry_date < datetime.now().date()

    @property
    def expires_soon(self):
        """Check if MOU expires within 90 days"""
        return (self.expiry_date - datetime.now().date()).days <= 90

    def save(self, *args, **kwargs):
        # Auto-update status based on expiry date
        if self.is_expired and self.status == 'approved':
            self.status = 'expired'
        super().save(*args, **kwargs)


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('created', 'Created'),
        ('accessed', 'Accessed'),
        ('signed', 'Signed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('updated', 'Updated'),
        ('pdf_uploaded', 'PDF Uploaded'),
        ('link_generated', 'Link Generated'),
        ('link_accessed', 'Link Accessed'),
    )
    
    mou = models.ForeignKey(MOU, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)  # For external users
    user_email = models.EmailField(blank=True, null=True)  # For external users
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        user_display = self.user.username if self.user else (self.user_name or 'Anonymous')
        return f"{self.mou.title} - {self.get_action_display()} by {user_display}"


class ShareLink(models.Model):
    mou = models.ForeignKey(MOU, on_delete=models.CASCADE, related_name='share_links')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    access_count = models.IntegerField(default=0)
    max_access_count = models.IntegerField(default=10)  # Limit access attempts

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Share link for {self.mou.title} - {self.token}"

    @property
    def is_expired(self):
        return datetime.now() > self.expires_at.replace(tzinfo=None)

    @property
    def is_valid(self):
        return (self.is_active and 
                not self.is_expired and 
                self.access_count < self.max_access_count)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Default expiration: 7 days from creation
            self.expires_at = datetime.now() + timedelta(days=7)
        super().save(*args, **kwargs)


class PartnerSubmission(models.Model):
    """Model to store partner submissions via shared links"""
    share_link = models.ForeignKey(ShareLink, on_delete=models.CASCADE, related_name='submissions')
    partner_name = models.CharField(max_length=255)
    partner_organization = models.CharField(max_length=255)
    partner_email = models.EmailField()
    partner_phone = models.CharField(max_length=20, blank=True, null=True)
    updated_pdf = models.FileField(upload_to='partner_submissions/', blank=True, null=True)
    signature_data = models.TextField(blank=True, null=True)  # Base64 encoded signature
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission by {self.partner_name} for {self.share_link.mou.title}"
