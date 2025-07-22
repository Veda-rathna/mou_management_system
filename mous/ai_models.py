"""
AI-related models for MOU Management System
"""

from django.db import models
from django.contrib.auth.models import User
from .models import MOU


class AIAnalysis(models.Model):
    """Stores AI analysis results for MOUs"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('completed', 'Analysis Completed'),
        ('failed', 'Analysis Failed'),
        ('outdated', 'Outdated - Needs Reanalysis'),
    ]
    
    COMPLIANCE_CHOICES = [
        ('compliant', 'Compliant'),
        ('review_required', 'Review Required'),
        ('non_compliant', 'Non-Compliant'),
        ('unknown', 'Unknown'),
        ('pending', 'Pending Analysis'),
    ]
    
    mou = models.OneToOneField(
        MOU, 
        on_delete=models.CASCADE, 
        related_name='ai_analysis'
    )
    
    # Analysis metadata
    analysis_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    model_version = models.CharField(max_length=50, default='1.0.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Analysis results
    overall_risk_score = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Risk score from 0-10, where 10 is highest risk"
    )
    
    compliance_status = models.CharField(
        max_length=20, 
        choices=COMPLIANCE_CHOICES, 
        default='pending'
    )
    
    # JSON fields for detailed analysis data
    analysis_data = models.JSONField(
        default=dict,
        help_text="Complete AI analysis results in JSON format"
    )
    
    recommendations = models.JSONField(
        default=list,
        help_text="List of AI-generated recommendations"
    )
    
    compliance_flags = models.JSONField(
        default=list,
        help_text="List of compliance issues flagged by AI"
    )
    
    summary_stats = models.JSONField(
        default=dict,
        help_text="Summary statistics about the analysis"
    )
    
    # Processing metadata
    processing_time_seconds = models.DecimalField(
        max_digits=8, 
        decimal_places=3, 
        null=True, 
        blank=True
    )
    
    error_message = models.TextField(
        blank=True, 
        help_text="Error message if analysis failed"
    )
    
    class Meta:
        verbose_name = "AI Analysis"
        verbose_name_plural = "AI Analyses"
        ordering = ['-analysis_date']
    
    def __str__(self):
        return f"AI Analysis for {self.mou.title} - {self.get_status_display()}"
    
    @property
    def risk_level(self):
        """Return human-readable risk level"""
        if not self.overall_risk_score:
            return "Unknown"
        
        score = float(self.overall_risk_score)
        if score >= 8:
            return "High"
        elif score >= 6:
            return "Medium"
        elif score >= 4:
            return "Low"
        else:
            return "Very Low"
    
    @property
    def risk_color(self):
        """Return Bootstrap color class for risk level"""
        risk_level = self.risk_level
        colors = {
            "High": "danger",
            "Medium": "warning", 
            "Low": "info",
            "Very Low": "success",
            "Unknown": "secondary"
        }
        return colors.get(risk_level, "secondary")
    
    def get_high_risk_clauses(self):
        """Get clauses with risk score > 7"""
        return self.clauses.filter(risk_score__gt=7)
    
    def get_clause_type_distribution(self):
        """Get distribution of clause types"""
        from django.db.models import Count
        return self.clauses.values('clause_type').annotate(count=Count('clause_type'))


class ClauseAnalysis(models.Model):
    """Individual clause analysis within an AI analysis"""
    
    CLAUSE_TYPE_CHOICES = [
        ('termination', 'Termination'),
        ('payment', 'Payment & Financial'),
        ('liability', 'Liability & Indemnification'),
        ('confidentiality', 'Confidentiality & NDA'),
        ('intellectual_property', 'Intellectual Property'),
        ('dispute_resolution', 'Dispute Resolution'),
        ('governing_law', 'Governing Law'),
        ('force_majeure', 'Force Majeure'),
        ('performance', 'Performance Requirements'),
        ('warranties', 'Warranties & Representations'),
        ('general', 'General Provisions'),
        ('unknown', 'Unknown/Other'),
    ]
    
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('unknown', 'Unknown'),
    ]
    
    ai_analysis = models.ForeignKey(
        AIAnalysis, 
        on_delete=models.CASCADE, 
        related_name='clauses'
    )
    
    # Clause content and metadata
    clause_text = models.TextField(help_text="Full text of the analyzed clause")
    clause_type = models.CharField(
        max_length=50, 
        choices=CLAUSE_TYPE_CHOICES,
        default='unknown'
    )
    
    # Position in document (optional)
    start_position = models.IntegerField(null=True, blank=True)
    end_position = models.IntegerField(null=True, blank=True)
    clause_number = models.CharField(max_length=20, blank=True)
    
    # AI analysis results
    confidence_score = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        null=True,
        blank=True,
        help_text="AI confidence score (0-1)"
    )
    
    risk_score = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        null=True,
        blank=True, 
        help_text="Risk score from 0-10"
    )
    
    sentiment = models.CharField(
        max_length=20, 
        choices=SENTIMENT_CHOICES,
        default='neutral'
    )
    
    # Detailed analysis data
    risk_factors = models.JSONField(
        default=list,
        help_text="List of identified risk factors"
    )
    
    suggestions = models.JSONField(
        default=list,
        help_text="AI-generated suggestions for improvement"
    )
    
    key_terms = models.JSONField(
        default=list,
        help_text="Important terms and entities identified in the clause"
    )
    
    similar_clauses = models.JSONField(
        default=list,
        help_text="References to similar clauses in other MOUs"
    )
    
    class Meta:
        verbose_name = "Clause Analysis"
        verbose_name_plural = "Clause Analyses"
        ordering = ['clause_number', 'start_position']
    
    def __str__(self):
        return f"{self.get_clause_type_display()} clause (Risk: {self.risk_score})"
    
    @property
    def risk_level(self):
        """Return human-readable risk level"""
        if not self.risk_score:
            return "Unknown"
        
        score = float(self.risk_score)
        if score >= 8:
            return "High"
        elif score >= 6:
            return "Medium"
        elif score >= 4:
            return "Low"
        else:
            return "Very Low"
    
    @property
    def truncated_text(self):
        """Return truncated clause text for display"""
        if len(self.clause_text) > 150:
            return self.clause_text[:147] + "..."
        return self.clause_text


class RiskFlag(models.Model):
    """Specific risk flags identified by AI analysis"""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    FLAG_TYPE_CHOICES = [
        ('legal_risk', 'Legal Risk'),
        ('financial_risk', 'Financial Risk'),
        ('compliance_risk', 'Compliance Risk'),
        ('operational_risk', 'Operational Risk'),
        ('reputational_risk', 'Reputational Risk'),
        ('missing_clause', 'Missing Standard Clause'),
        ('vague_terms', 'Vague or Ambiguous Terms'),
        ('unfavorable_terms', 'Unfavorable Terms'),
    ]
    
    mou = models.ForeignKey(
        MOU, 
        on_delete=models.CASCADE, 
        related_name='risk_flags'
    )
    
    clause_analysis = models.ForeignKey(
        ClauseAnalysis, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Specific clause that triggered this flag (if applicable)"
    )
    
    # Flag details
    flag_type = models.CharField(max_length=50, choices=FLAG_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Resolution tracking
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_risk_flags'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # AI confidence in this flag
    confidence_score = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Risk Flag"
        verbose_name_plural = "Risk Flags"
        ordering = ['-severity', '-created_at']
    
    def __str__(self):
        return f"{self.get_severity_display()} {self.get_flag_type_display()}: {self.title}"
    
    @property
    def severity_color(self):
        """Return Bootstrap color class for severity"""
        colors = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger', 
            'critical': 'dark'
        }
        return colors.get(self.severity, 'secondary')
    
    def resolve(self, user, notes=""):
        """Mark this flag as resolved"""
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()


class AIModelMetrics(models.Model):
    """Track AI model performance and usage metrics"""
    
    date = models.DateField(auto_now_add=True)
    model_version = models.CharField(max_length=50)
    
    # Usage metrics
    documents_analyzed = models.IntegerField(default=0)
    clauses_analyzed = models.IntegerField(default=0)
    total_processing_time = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    
    # Performance metrics
    average_confidence = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    high_risk_flags_generated = models.IntegerField(default=0)
    
    # Error tracking
    analysis_failures = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "AI Model Metrics"
        verbose_name_plural = "AI Model Metrics"
        unique_together = ['date', 'model_version']
        ordering = ['-date']
    
    def __str__(self):
        return f"AI Metrics for {self.date} (v{self.model_version})"
