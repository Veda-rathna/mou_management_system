"""
Management command to create sample AI analysis data for testing
Usage: python manage.py create_sample_ai_data
"""

from django.core.management.base import BaseCommand
from mous.models import MOU
from decimal import Decimal
import json


class Command(BaseCommand):
    help = 'Create sample AI analysis data for testing purposes'

    def handle(self, *args, **options):
        try:
            # Import AI models
            from mous.ai_models import AIAnalysis, ClauseAnalysis, RiskFlag
            
            # Get MOUs without AI analysis
            mous_without_analysis = MOU.objects.filter(ai_analysis__isnull=True)[:5]
            
            if not mous_without_analysis:
                self.stdout.write(
                    self.style.WARNING('No MOUs found without AI analysis')
                )
                return
                
            sample_analyses = [
                {
                    'risk_score': 2.5,
                    'risk_level': 'low',
                    'compliance': 'compliant',
                    'summary': 'This MOU shows excellent compliance with standard terms and minimal risk factors.',
                    'recommendations': [
                        'Consider adding specific performance metrics',
                        'Include regular review schedules'
                    ],
                    'clauses': [
                        {'type': 'termination', 'content': 'Standard termination clause', 'risk': 1.5},
                        {'type': 'liability', 'content': 'Limited liability provisions', 'risk': 2.0},
                        {'type': 'confidentiality', 'content': 'Mutual confidentiality terms', 'risk': 1.0},
                    ],
                    'flags': []
                },
                {
                    'risk_score': 5.2,
                    'risk_level': 'medium',
                    'compliance': 'review_required',
                    'summary': 'This MOU contains some clauses that require attention and review.',
                    'recommendations': [
                        'Review liability limitations',
                        'Clarify intellectual property rights',
                        'Add dispute resolution mechanism'
                    ],
                    'clauses': [
                        {'type': 'liability', 'content': 'Broad liability exclusions', 'risk': 6.5},
                        {'type': 'intellectual_property', 'content': 'Unclear IP ownership', 'risk': 5.8},
                        {'type': 'termination', 'content': 'Asymmetric termination rights', 'risk': 4.2},
                    ],
                    'flags': [
                        {'type': 'liability_concern', 'severity': 'medium', 'description': 'Liability clause may be too restrictive'},
                        {'type': 'ip_unclear', 'severity': 'medium', 'description': 'Intellectual property ownership needs clarification'},
                    ]
                },
                {
                    'risk_score': 8.3,
                    'risk_level': 'high',
                    'compliance': 'non_compliant',
                    'summary': 'This MOU contains high-risk clauses that pose significant concerns.',
                    'recommendations': [
                        'Immediate review required for liability terms',
                        'Renegotiate indemnification clauses',
                        'Add legal compliance requirements',
                        'Include proper termination procedures'
                    ],
                    'clauses': [
                        {'type': 'indemnification', 'content': 'One-sided indemnification', 'risk': 9.1},
                        {'type': 'liability', 'content': 'Unlimited liability exposure', 'risk': 8.8},
                        {'type': 'governing_law', 'content': 'Unfavorable jurisdiction', 'risk': 7.5},
                        {'type': 'force_majeure', 'content': 'Missing force majeure clause', 'risk': 6.0},
                    ],
                    'flags': [
                        {'type': 'indemnification_risk', 'severity': 'high', 'description': 'One-sided indemnification creates high risk exposure'},
                        {'type': 'unlimited_liability', 'severity': 'high', 'description': 'Unlimited liability clause poses significant financial risk'},
                        {'type': 'jurisdiction_concern', 'severity': 'medium', 'description': 'Governing law may be unfavorable'},
                    ]
                },
                {
                    'risk_score': 3.8,
                    'risk_level': 'medium',
                    'compliance': 'compliant',
                    'summary': 'Generally compliant MOU with minor areas for improvement.',
                    'recommendations': [
                        'Consider adding data protection clauses',
                        'Include change management procedures'
                    ],
                    'clauses': [
                        {'type': 'data_protection', 'content': 'Basic data handling terms', 'risk': 4.2},
                        {'type': 'modification', 'content': 'Standard amendment process', 'risk': 2.8},
                        {'type': 'term', 'content': 'Fixed term with renewal option', 'risk': 3.1},
                    ],
                    'flags': [
                        {'type': 'data_privacy', 'severity': 'low', 'description': 'Consider strengthening data protection terms'},
                    ]
                },
                {
                    'risk_score': 1.8,
                    'risk_level': 'low',
                    'compliance': 'compliant',
                    'summary': 'Excellent MOU structure with comprehensive terms and minimal risk.',
                    'recommendations': [
                        'No immediate action required',
                        'Schedule periodic review in 6 months'
                    ],
                    'clauses': [
                        {'type': 'scope', 'content': 'Well-defined scope and objectives', 'risk': 1.2},
                        {'type': 'responsibilities', 'content': 'Clear role definitions', 'risk': 1.5},
                        {'type': 'reporting', 'content': 'Regular reporting requirements', 'risk': 2.1},
                    ],
                    'flags': []
                },
            ]
            
            created_count = 0
            for i, mou in enumerate(mous_without_analysis):
                if i >= len(sample_analyses):
                    break
                    
                data = sample_analyses[i]
                
                # Create AI Analysis
                analysis = AIAnalysis.objects.create(
                    mou=mou,
                    overall_risk_score=Decimal(str(data['risk_score'])),
                    compliance_status=data['compliance'],
                    status='completed',
                    analysis_data={'summary': data['summary']},
                    recommendations=data['recommendations'],
                    model_version='1.0.0-demo',
                    processing_time_seconds=Decimal('5.2')
                )
                
                # Create clause analyses
                for clause_data in data['clauses']:
                    ClauseAnalysis.objects.create(
                        ai_analysis=analysis,
                        clause_type=clause_data['type'],
                        clause_text=clause_data['content'],
                        risk_score=Decimal(str(clause_data['risk'])),
                        confidence_score=Decimal('0.855'),
                        risk_factors=[]
                    )
                
                # Create risk flags
                for flag_data in data['flags']:
                    RiskFlag.objects.create(
                        mou=mou,
                        flag_type=flag_data['type'],
                        severity=flag_data['severity'],
                        title=flag_data['description'],
                        description=flag_data['description'],
                        confidence_score=Decimal('0.789')
                    )
                
                created_count += 1
                self.stdout.write(f'Created sample AI analysis for: {mou.title}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} sample AI analyses!')
            )
            
        except ImportError:
            self.stdout.write(
                self.style.ERROR('AI models not available. Run migrations first.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample data: {str(e)}')
            )
