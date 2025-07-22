"""
Management command to run AI analysis on existing MOUs
Usage: python manage.py analyze_existing_mous [--all] [--mou-id <id>] [--limit <count>]
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from mous.models import MOU
from mous.tasks import analyze_mou_with_ai
import time


class Command(BaseCommand):
    help = 'Run AI analysis on existing MOUs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Analyze all MOUs without AI analysis',
        )
        parser.add_argument(
            '--mou-id',
            type=int,
            help='Analyze specific MOU by ID',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of MOUs to analyze (default: 10)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-analyze MOUs that already have AI analysis',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting AI analysis for existing MOUs...')
        )

        try:
            # Import AI analysis models here to check if available
            from mous.ai_models import AIAnalysis
            
            if options['mou_id']:
                # Analyze specific MOU
                try:
                    mou = MOU.objects.get(id=options['mou_id'])
                    self.analyze_mou(mou, force=options['force'])
                except MOU.DoesNotExist:
                    raise CommandError(f'MOU with ID {options["mou_id"]} does not exist')
                    
            else:
                # Get MOUs to analyze
                queryset = MOU.objects.filter(pdf_file__isnull=False)
                
                if not options['force']:
                    # Exclude MOUs that already have analysis
                    queryset = queryset.filter(ai_analysis__isnull=True)
                
                if not options['all']:
                    # Limit the number of MOUs
                    queryset = queryset[:options['limit']]
                
                total_count = queryset.count()
                
                if total_count == 0:
                    self.stdout.write(
                        self.style.WARNING('No MOUs found to analyze.')
                    )
                    return
                
                self.stdout.write(
                    f'Found {total_count} MOUs to analyze...'
                )
                
                success_count = 0
                for i, mou in enumerate(queryset, 1):
                    self.stdout.write(f'Processing MOU {i}/{total_count}: {mou.title}')
                    
                    if self.analyze_mou(mou, force=options['force']):
                        success_count += 1
                    
                    # Add small delay to avoid overwhelming the system
                    time.sleep(1)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Completed! Successfully started analysis for {success_count}/{total_count} MOUs.'
                    )
                )
                
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    'AI models not available. Make sure migrations have been applied.'
                )
            )
        except Exception as e:
            raise CommandError(f'Error during analysis: {str(e)}')

    def analyze_mou(self, mou, force=False):
        """Analyze a single MOU"""
        try:
            # Check if already has analysis and force is not enabled
            if not force and hasattr(mou, 'ai_analysis'):
                self.stdout.write(
                    self.style.WARNING(f'  MOU "{mou.title}" already has AI analysis (use --force to re-analyze)')
                )
                return False
            
            # Check if PDF file exists
            if not mou.pdf_file:
                self.stdout.write(
                    self.style.WARNING(f'  MOU "{mou.title}" has no PDF file')
                )
                return False
            
            # Start the analysis task
            result = analyze_mou_with_ai.delay(mou.id)
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Started analysis for "{mou.title}" (Task ID: {result.id})')
            )
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Failed to analyze "{mou.title}": {str(e)}')
            )
            return False
