from django.core.management.base import BaseCommand
from django.utils.text import slugify
from gallery.models import GalleryCategory


class Command(BaseCommand):
    help = 'Populate default gallery categories for the Barangay Portal'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Community Events',
                'description': 'Photos from barangay celebrations, festivals, and community gatherings',
                'category_type': 'events',
                'icon': 'fas fa-calendar-alt'
            },
            {
                'name': 'Infrastructure & Development',
                'description': 'Road construction, building projects, and infrastructure improvements',
                'category_type': 'infrastructure',
                'icon': 'fas fa-hammer'
            },
            {
                'name': 'Barangay Services',
                'description': 'Healthcare, education, and public services in action',
                'category_type': 'services',
                'icon': 'fas fa-hands-helping'
            },
            {
                'name': 'Community Activities',
                'description': 'Daily life, volunteer work, and community initiatives',
                'category_type': 'activities',
                'icon': 'fas fa-users'
            },
            {
                'name': 'Barangay Officials',
                'description': 'Photos of barangay officials, meetings, and ceremonies',
                'category_type': 'officials',
                'icon': 'fas fa-user-tie'
            },
            {
                'name': 'Cultural Heritage',
                'description': 'Traditional arts, cultural practices, and heritage sites',
                'category_type': 'cultural',
                'icon': 'fas fa-landmark'
            },
            {
                'name': 'Sports & Recreation',
                'description': 'Sports events, recreational activities, and fitness programs',
                'category_type': 'sports',
                'icon': 'fas fa-futbol'
            },
            {
                'name': 'Health Programs',
                'description': 'Medical missions, health campaigns, and wellness activities',
                'category_type': 'health',
                'icon': 'fas fa-heartbeat'
            },
            {
                'name': 'Education Programs',
                'description': 'School activities, educational workshops, and learning initiatives',
                'category_type': 'education',
                'icon': 'fas fa-graduation-cap'
            },
            {
                'name': 'Environmental Initiatives',
                'description': 'Tree planting, clean-up drives, and environmental protection',
                'category_type': 'environment',
                'icon': 'fas fa-leaf'
            },
            {
                'name': 'Public Safety',
                'description': 'Emergency response, safety training, and security measures',
                'category_type': 'safety',
                'icon': 'fas fa-shield-alt'
            },
            {
                'name': 'Historical Moments',
                'description': 'Important historical events and milestone achievements',
                'category_type': 'other',
                'icon': 'fas fa-history'
            }
        ]

        created_count = 0
        updated_count = 0

        for category_data in categories:
            slug = slugify(category_data['name'])
            
            category, created = GalleryCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': category_data['name'],
                    'description': category_data['description'],
                    'category_type': category_data['category_type'],
                    'icon': category_data['icon'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                # Update existing category
                category.description = category_data['description']
                category.category_type = category_data['category_type']
                category.icon = category_data['icon']
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated category: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} categories created, {updated_count} categories updated'
            )
        )
        
        total_categories = GalleryCategory.objects.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(f'Total active gallery categories: {total_categories}')
        )
