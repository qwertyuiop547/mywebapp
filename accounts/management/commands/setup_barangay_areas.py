"""
Management command to setup default barangay areas for residency validation
"""
from django.core.management.base import BaseCommand
from accounts.utils import setup_default_barangay_areas


class Command(BaseCommand):
    help = 'Setup default streets and areas for Barangay Burgos'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up default barangay areas...')
        
        try:
            created_count = setup_default_barangay_areas()
            
            if created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created {created_count} new barangay areas!'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'All barangay areas already exist. No new areas created.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up barangay areas: {str(e)}')
            )
