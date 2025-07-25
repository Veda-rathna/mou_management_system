# Generated by Django 4.2.7 on 2025-07-22 13:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mous', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analysis_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('model_version', models.CharField(default='1.0.0', max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending Analysis'), ('completed', 'Analysis Completed'), ('failed', 'Analysis Failed'), ('outdated', 'Outdated - Needs Reanalysis')], default='pending', max_length=20)),
                ('overall_risk_score', models.DecimalField(blank=True, decimal_places=2, help_text='Risk score from 0-10, where 10 is highest risk', max_digits=4, null=True)),
                ('compliance_status', models.CharField(choices=[('compliant', 'Compliant'), ('review_required', 'Review Required'), ('non_compliant', 'Non-Compliant'), ('unknown', 'Unknown'), ('pending', 'Pending Analysis')], default='pending', max_length=20)),
                ('analysis_data', models.JSONField(default=dict, help_text='Complete AI analysis results in JSON format')),
                ('recommendations', models.JSONField(default=list, help_text='List of AI-generated recommendations')),
                ('compliance_flags', models.JSONField(default=list, help_text='List of compliance issues flagged by AI')),
                ('summary_stats', models.JSONField(default=dict, help_text='Summary statistics about the analysis')),
                ('processing_time_seconds', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('error_message', models.TextField(blank=True, help_text='Error message if analysis failed')),
                ('mou', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ai_analysis', to='mous.mou')),
            ],
            options={
                'verbose_name': 'AI Analysis',
                'verbose_name_plural': 'AI Analyses',
                'ordering': ['-analysis_date'],
            },
        ),
        migrations.CreateModel(
            name='ClauseAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clause_text', models.TextField(help_text='Full text of the analyzed clause')),
                ('clause_type', models.CharField(choices=[('termination', 'Termination'), ('payment', 'Payment & Financial'), ('liability', 'Liability & Indemnification'), ('confidentiality', 'Confidentiality & NDA'), ('intellectual_property', 'Intellectual Property'), ('dispute_resolution', 'Dispute Resolution'), ('governing_law', 'Governing Law'), ('force_majeure', 'Force Majeure'), ('performance', 'Performance Requirements'), ('warranties', 'Warranties & Representations'), ('general', 'General Provisions'), ('unknown', 'Unknown/Other')], default='unknown', max_length=50)),
                ('start_position', models.IntegerField(blank=True, null=True)),
                ('end_position', models.IntegerField(blank=True, null=True)),
                ('clause_number', models.CharField(blank=True, max_length=20)),
                ('confidence_score', models.DecimalField(blank=True, decimal_places=4, help_text='AI confidence score (0-1)', max_digits=5, null=True)),
                ('risk_score', models.DecimalField(blank=True, decimal_places=2, help_text='Risk score from 0-10', max_digits=4, null=True)),
                ('sentiment', models.CharField(choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative'), ('unknown', 'Unknown')], default='neutral', max_length=20)),
                ('risk_factors', models.JSONField(default=list, help_text='List of identified risk factors')),
                ('suggestions', models.JSONField(default=list, help_text='AI-generated suggestions for improvement')),
                ('key_terms', models.JSONField(default=list, help_text='Important terms and entities identified in the clause')),
                ('similar_clauses', models.JSONField(default=list, help_text='References to similar clauses in other MOUs')),
                ('ai_analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clauses', to='mous.aianalysis')),
            ],
            options={
                'verbose_name': 'Clause Analysis',
                'verbose_name_plural': 'Clause Analyses',
                'ordering': ['clause_number', 'start_position'],
            },
        ),
        migrations.CreateModel(
            name='RiskFlag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag_type', models.CharField(choices=[('legal_risk', 'Legal Risk'), ('financial_risk', 'Financial Risk'), ('compliance_risk', 'Compliance Risk'), ('operational_risk', 'Operational Risk'), ('reputational_risk', 'Reputational Risk'), ('missing_clause', 'Missing Standard Clause'), ('vague_terms', 'Vague or Ambiguous Terms'), ('unfavorable_terms', 'Unfavorable Terms')], max_length=50)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('confidence_score', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('clause_analysis', models.ForeignKey(blank=True, help_text='Specific clause that triggered this flag (if applicable)', null=True, on_delete=django.db.models.deletion.CASCADE, to='mous.clauseanalysis')),
                ('mou', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='risk_flags', to='mous.mou')),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_risk_flags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Risk Flag',
                'verbose_name_plural': 'Risk Flags',
                'ordering': ['-severity', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIModelMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('model_version', models.CharField(max_length=50)),
                ('documents_analyzed', models.IntegerField(default=0)),
                ('clauses_analyzed', models.IntegerField(default=0)),
                ('total_processing_time', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('average_confidence', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('high_risk_flags_generated', models.IntegerField(default=0)),
                ('analysis_failures', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'AI Model Metrics',
                'verbose_name_plural': 'AI Model Metrics',
                'ordering': ['-date'],
                'unique_together': {('date', 'model_version')},
            },
        ),
    ]
