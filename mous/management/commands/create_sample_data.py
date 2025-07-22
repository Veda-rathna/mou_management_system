from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mous.models import MOU, ActivityLog
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Create sample data for MOU Management System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            MOU.objects.all().delete()
            ActivityLog.objects.all().delete()

        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))

        # Create sample users
        users = []
        for username in ['manager1', 'manager2']:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': username.title(),
                    'last_name': 'Manager'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                users.append(user)
                self.stdout.write(f'Created user: {username}/password123')

        # Sample MOU data
        sample_mous = [
            {
                'title': 'Technology Partnership Agreement',
                'partner_name': 'Tech Solutions Inc.',
                'partner_organization': 'Tech Solutions Inc.',
                'partner_contact': 'contact@techsolutions.com',
                'expiry_date': date.today() + timedelta(days=30),
                'status': 'approved',
                'description': 'Partnership for technology development and innovation.',
            },
            {
                'title': 'Research Collaboration MOU',
                'partner_name': 'Dr. Jane Smith',
                'partner_organization': 'University Research Center',
                'partner_contact': 'j.smith@university.edu',
                'expiry_date': date.today() + timedelta(days=45),
                'status': 'pending',
                'description': 'Collaborative research in artificial intelligence.',
            },
            {
                'title': 'Service Provider Agreement',
                'partner_name': 'Global Services Ltd.',
                'partner_organization': 'Global Services Ltd.',
                'partner_contact': 'info@globalservices.com',
                'expiry_date': date.today() + timedelta(days=120),
                'status': 'approved',
                'description': 'Service provision and maintenance agreement.',
            },
            {
                'title': 'Academic Exchange Program',
                'partner_name': 'Prof. John Doe',
                'partner_organization': 'International University',
                'partner_contact': 'j.doe@intluni.edu',
                'expiry_date': date.today() + timedelta(days=200),
                'status': 'draft',
                'description': 'Student and faculty exchange program.',
            },
            {
                'title': 'Data Sharing Agreement',
                'partner_name': 'Data Analytics Corp',
                'partner_organization': 'Data Analytics Corp',
                'partner_contact': 'legal@dataanalytics.com',
                'expiry_date': date.today() + timedelta(days=60),
                'status': 'approved',
                'description': 'Secure data sharing for analytics purposes.',
            },
        ]

        admin_user = User.objects.get(username='admin')
        
        for mou_data in sample_mous:
            mou = MOU.objects.create(
                created_by=admin_user,
                **mou_data
            )
            
            # Create activity log
            ActivityLog.objects.create(
                mou=mou,
                action='created',
                user=admin_user,
                description='Sample MOU created during setup'
            )
            
            self.stdout.write(f'Created MOU: {mou.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(sample_mous)} sample MOUs'
            )
        )
