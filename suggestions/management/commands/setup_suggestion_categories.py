from django.core.management.base import BaseCommand
from suggestions.models import SuggestionCategory

class Command(BaseCommand):
    help = 'Create default suggestion categories for the barangay'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Infrastructure & Roads',
                'description': 'Suggestions for road improvements, drainage, bridges, and general infrastructure'
            },
            {
                'name': 'Public Safety & Security',
                'description': 'Suggestions for improving safety, security measures, and emergency response'
            },
            {
                'name': 'Health & Sanitation',
                'description': 'Suggestions for health services, waste management, and sanitation improvements'
            },
            {
                'name': 'Community Services',
                'description': 'Suggestions for community programs, events, and public services'
            },
            {
                'name': 'Environmental Issues',
                'description': 'Suggestions for environmental protection, tree planting, and green initiatives'
            },
            {
                'name': 'Youth & Education',
                'description': 'Suggestions for youth programs, educational activities, and skills development'
            },
            {
                'name': 'Senior Citizens',
                'description': 'Suggestions for senior citizen programs and services'
            },
            {
                'name': 'Sports & Recreation',
                'description': 'Suggestions for sports facilities, recreational activities, and fitness programs'
            },
            {
                'name': 'Economic Development',
                'description': 'Suggestions for livelihood programs, business development, and economic growth'
            },
            {
                'name': 'Digital Services',
                'description': 'Suggestions for improving online services, digital processes, and technology'
            },
            {
                'name': 'Transportation',
                'description': 'Suggestions for public transportation, traffic management, and mobility'
            },
            {
                'name': 'Cultural & Heritage',
                'description': 'Suggestions for preserving culture, heritage sites, and traditional practices'
            },
            {
                'name': 'Emergency Preparedness',
                'description': 'Suggestions for disaster preparedness, evacuation plans, and emergency response'
            },
            {
                'name': 'Administrative Services',
                'description': 'Suggestions for improving government services, processes, and citizen assistance'
            },
            {
                'name': 'Other',
                'description': 'General suggestions that don\'t fit in other categories'
            }
        ]

        created_count = 0
        for category_data in categories:
            category, created = SuggestionCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up {created_count} new suggestion categories'
            )
        )
