from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create a new user account'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the new user')
        parser.add_argument('email', type=str, help='Email for the new user')
        parser.add_argument('--first-name', type=str, help='First name of the user')
        parser.add_argument('--last-name', type=str, help='Last name of the user')
        parser.add_argument('--password', type=str, help='Password for the user (will prompt if not provided)')
        parser.add_argument('--staff', action='store_true', help='Make user a staff member')
        parser.add_argument('--superuser', action='store_true', help='Make user a superuser')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        
        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" already exists.')
                )
                return
            
            # Get password
            password = options.get('password')
            if not password:
                import getpass
                password = getpass.getpass('Password: ')
                confirm_password = getpass.getpass('Confirm password: ')
                if password != confirm_password:
                    self.stdout.write(
                        self.style.ERROR('Passwords do not match.')
                    )
                    return
            
            # Create user
            user_data = {
                'username': username,
                'email': email,
                'first_name': options.get('first_name', ''),
                'last_name': options.get('last_name', ''),
            }
            
            if options['superuser']:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Superuser "{username}" created successfully.')
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                
                if options['staff']:
                    user.is_staff = True
                    user.save()
                
                user_type = "staff user" if options['staff'] else "regular user"
                self.stdout.write(
                    self.style.SUCCESS(f'{user_type.title()} "{username}" created successfully.')
                )
                
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating user: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
