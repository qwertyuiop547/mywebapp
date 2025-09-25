from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create admin user with chairman role'

    def handle(self, *args, **options):
        # Admin credentials for Barangay Burgos
        username = 'chairman'
        email = 'chairman@brgyburgosbasey.gov.ph'
        password = 'burgos2025'
        first_name = 'Barangay'
        last_name = 'Chairman'
        
        try:
            # Check if admin user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'Admin user "{username}" already exists.')
                )
                # Update the existing user
                admin_user = User.objects.get(username=username)
                admin_user.role = 'chairman'
                admin_user.is_approved = True
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.email = email
                admin_user.first_name = first_name
                admin_user.last_name = last_name
                admin_user.set_password(password)
                admin_user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Updated existing admin user "{username}" with chairman role.')
                )
            else:
                # Create new admin user
                admin_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role='chairman',
                    is_approved=True,
                    is_staff=True,
                    is_superuser=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created admin user "{username}" with chairman role.')
                )
            
            # Display credentials
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('ADMIN CREDENTIALS'))
            self.stdout.write('='*50)
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Role: Chairman')
            self.stdout.write(f'Full Name: {first_name} {last_name}')
            self.stdout.write('='*50)
            self.stdout.write(self.style.WARNING('Please keep these credentials secure!'))
            
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )