"""
Management command to set up and test AI features
Usage: python manage.py setup_ai_analysis
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from mous.models import MOU
from mous.utils import create_ai_analysis_from_data
import sys


class Command(BaseCommand):
    help = 'Set up and test AI analysis features'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--install-deps',
            action='store_true',
            help='Install AI dependencies (requires pip)'
        )
        
        parser.add_argument(
            '--test-analysis',
            action='store_true',
            help='Test AI analysis on existing MOUs'
        )
        
        parser.add_argument(
            '--mou-id',
            type=int,
            help='Specific MOU ID to analyze (for testing)'
        )
        
        parser.add_argument(
            '--download-models',
            action='store_true',
            help='Download required AI models'
        )
    
    def handle(self, *args, **options):
        if options['install_deps']:
            self.install_dependencies()
        
        if options['download_models']:
            self.download_models()
        
        if options['test_analysis']:
            if options['mou_id']:
                self.test_single_mou(options['mou_id'])
            else:
                self.test_ai_analysis()
        
        if not any(options.values()):
            self.show_help()
    
    def show_help(self):
        """Show help information"""
        self.stdout.write(self.style.SUCCESS("AI Analysis Setup Command"))
        self.stdout.write("\nAvailable options:")
        self.stdout.write("  --install-deps     Install AI dependencies")
        self.stdout.write("  --download-models  Download required AI models")
        self.stdout.write("  --test-analysis    Test AI analysis on existing MOUs")
        self.stdout.write("  --mou-id <id>      Test specific MOU by ID")
        self.stdout.write("\nExamples:")
        self.stdout.write("  python manage.py setup_ai_analysis --install-deps")
        self.stdout.write("  python manage.py setup_ai_analysis --test-analysis")
        self.stdout.write("  python manage.py setup_ai_analysis --mou-id 1")
    
    def install_dependencies(self):
        """Install AI dependencies"""
        self.stdout.write("Installing AI dependencies...")
        
        try:
            import subprocess
            
            # Install main AI packages
            packages = [
                'transformers>=4.21.0',
                'torch>=1.12.0', 
                'sentence-transformers>=2.2.2',
                'spacy>=3.4.0',
                'nltk>=3.7',
                'scikit-learn>=1.1.0',
                'numpy>=1.21.0'
            ]
            
            for package in packages:
                self.stdout.write(f"Installing {package}...")
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to install {package}: {result.stderr}")
                    )
                else:
                    self.stdout.write(self.style.SUCCESS(f"✓ Installed {package}"))
            
            self.stdout.write(self.style.SUCCESS("✓ AI dependencies installed successfully"))
            self.stdout.write("\nRun --download-models next to download language models")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error installing dependencies: {str(e)}"))
    
    def download_models(self):
        """Download required AI models"""
        self.stdout.write("Downloading AI models...")
        
        try:
            import subprocess
            
            # Download spaCy English model
            self.stdout.write("Downloading spaCy English model...")
            result = subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS("✓ spaCy English model downloaded"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to download spaCy model: {result.stderr}"))
            
            # Test model loading
            self.stdout.write("Testing AI model loading...")
            try:
                from mous.ai_services import ClauseAnalyzer
                analyzer = ClauseAnalyzer()
                if analyzer.is_ready:
                    self.stdout.write(self.style.SUCCESS("✓ AI models loaded successfully"))
                else:
                    self.stdout.write(self.style.WARNING("⚠ AI models loaded with fallback mode"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error loading AI models: {str(e)}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error downloading models: {str(e)}"))
    
    def test_ai_analysis(self):
        """Test AI analysis on existing MOUs"""
        self.stdout.write("Testing AI analysis...")
        
        try:
            # Check if we have AI services available
            try:
                from mous.ai_services import analyze_mou_document
                from mous.utils import extract_pdf_data
            except ImportError as e:
                self.stdout.write(self.style.ERROR(f"AI services not available: {str(e)}"))
                return
            
            # Find MOUs with PDF files
            mous_with_pdfs = MOU.objects.filter(pdf_file__isnull=False)[:5]  # Test on first 5
            
            if not mous_with_pdfs.exists():
                self.stdout.write(self.style.WARNING("No MOUs with PDF files found"))
                return
            
            self.stdout.write(f"Found {mous_with_pdfs.count()} MOUs with PDFs. Testing analysis...")
            
            success_count = 0
            for mou in mous_with_pdfs:
                try:
                    self.stdout.write(f"\nAnalyzing MOU: {mou.title}")
                    
                    # Extract PDF data
                    pdf_data = extract_pdf_data(mou.pdf_file.path)
                    
                    if not pdf_data.get('full_text'):
                        self.stdout.write(self.style.WARNING(f"  ⚠ No text extracted from PDF"))
                        continue
                    
                    # Perform AI analysis
                    ai_result = analyze_mou_document(pdf_data['full_text'], mou.title)
                    
                    # Create AI analysis record
                    ai_analysis = create_ai_analysis_from_data(mou, ai_result)
                    
                    if ai_analysis:
                        self.stdout.write(self.style.SUCCESS(
                            f"  ✓ Analysis completed - Risk Score: {ai_result.get('overall_risk_score', 'N/A')}/10"
                        ))
                        success_count += 1
                    else:
                        self.stdout.write(self.style.ERROR(f"  ✗ Failed to save analysis"))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Error analyzing MOU: {str(e)}"))
            
            self.stdout.write(f"\n✓ Successfully analyzed {success_count}/{mous_with_pdfs.count()} MOUs")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error in test analysis: {str(e)}"))
    
    def test_single_mou(self, mou_id):
        """Test AI analysis on a specific MOU"""
        try:
            from mous.ai_services import analyze_mou_document
            from mous.utils import extract_pdf_data
            
            mou = MOU.objects.get(id=mou_id)
            self.stdout.write(f"Testing AI analysis on MOU: {mou.title}")
            
            if not mou.pdf_file:
                self.stdout.write(self.style.ERROR("MOU has no PDF file"))
                return
            
            # Extract PDF data
            pdf_data = extract_pdf_data(mou.pdf_file.path)
            
            if not pdf_data.get('full_text'):
                self.stdout.write(self.style.ERROR("Could not extract text from PDF"))
                return
            
            self.stdout.write(f"Extracted {len(pdf_data['full_text'])} characters from PDF")
            
            # Perform AI analysis
            ai_result = analyze_mou_document(pdf_data['full_text'], mou.title)
            
            # Display results
            self.stdout.write("\n=== AI Analysis Results ===")
            self.stdout.write(f"Overall Risk Score: {ai_result.get('overall_risk_score', 'N/A')}/10")
            self.stdout.write(f"Clauses Analyzed: {len(ai_result.get('clauses', []))}")
            self.stdout.write(f"Compliance Status: {ai_result.get('compliance_status', 'Unknown')}")
            
            if ai_result.get('recommendations'):
                self.stdout.write("\nRecommendations:")
                for i, rec in enumerate(ai_result['recommendations'], 1):
                    self.stdout.write(f"  {i}. {rec}")
            
            # Create AI analysis record
            ai_analysis = create_ai_analysis_from_data(mou, ai_result)
            if ai_analysis:
                self.stdout.write(self.style.SUCCESS("\n✓ AI analysis saved successfully"))
            else:
                self.stdout.write(self.style.ERROR("\n✗ Failed to save AI analysis"))
                
        except MOU.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"MOU with ID {mou_id} not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
