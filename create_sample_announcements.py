import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from announcements.models import Announcement
from accounts.models import User
from django.utils import timezone

# Get or create a chairman user
try:
    chairman = User.objects.filter(role='chairman', is_approved=True).first()
    if not chairman:
        print("No chairman found. Creating one...")
        chairman = User.objects.create_user(
            username='chairman',
            email='chairman@burgosbasey.ph',
            password='chairman123',
            first_name='Juan',
            last_name='Dela Cruz',
            role='chairman',
            is_approved=True,
            is_staff=True
        )
        print(f"Created chairman: {chairman.username}")
    else:
        print(f"Using existing chairman: {chairman.username}")
except Exception as e:
    print(f"Error getting chairman: {e}")
    exit(1)

# Sample announcements data
announcements_data = [
    {
        'title': 'Barangay Assembly - October 2025',
        'content': 'Mahal naming mga kababayan, makikipag-ugnayan tayo sa susunod na Barangay Assembly sa Oktubre 15, 2025 sa Barangay Hall. Mahalagang dumalo ang lahat upang pag-usapan ang mga plano at proyekto para sa ating komunidad.',
        'category': 'meeting',
        'priority': 'high'
    },
    {
        'title': 'Improved Street Lighting Project',
        'content': 'Natapos na ang installation ng mga bagong solar-powered LED street lights sa mga pangunahing kalye ng barangay. Ito ay bahagi ng ating programa para sa mas ligtas na komunidad.',
        'category': 'service',
        'priority': 'medium'
    },
    {
        'title': 'Free Medical Mission',
        'content': 'Libre pong medical checkup, dental services, at konsultasyon para sa lahat ng residente tuwing Sabado ng umaga, 8:00 AM - 12:00 NN sa Barangay Health Center. Magdala ng valid ID.',
        'category': 'health',
        'priority': 'medium'
    },
    {
        'title': 'Basketball League Registration',
        'content': 'Bukas na ang registration para sa Barangay Basketball League 2025! Mga edad 15-35 years old ay maaaring magsumite ng kanilang mga application sa Barangay Sports Office hanggang Oktubre 20, 2025.',
        'category': 'event',
        'priority': 'low'
    },
    {
        'title': 'Typhoon Preparedness Advisory',
        'content': 'Sa paparating na typhoon season, hinihikayat namin ang lahat ng residente na maghanda ng emergency kit at disaster preparedness plan. Para sa tulong at impormasyon, makipag-ugnayan sa BDRRMC hotline.',
        'category': 'safety',
        'priority': 'urgent'
    },
    {
        'title': 'Water Service Interruption Notice',
        'content': 'Mangyaring magkaroon ng alerto na magkakaroon ng scheduled water service interruption sa Purok 1-3 sa Oktubre 10, 2025, 9:00 AM - 3:00 PM para sa pipeline maintenance. Mag-imbak ng tubig nang maaga.',
        'category': 'maintenance',
        'priority': 'high'
    }
]

# Create announcements
created_count = 0
for data in announcements_data:
    try:
        # Check if announcement with same title exists
        if not Announcement.objects.filter(title=data['title']).exists():
            announcement = Announcement.objects.create(
                title=data['title'],
                content=data['content'],
                category=data['category'],
                priority=data['priority'],
                created_by=chairman,
                approval_status='approved',
                approved_by=chairman,
                approved_at=timezone.now(),
                is_published=True
            )
            created_count += 1
            print(f"✓ Created: {announcement.title}")
        else:
            print(f"- Skipped (exists): {data['title']}")
    except Exception as e:
        print(f"✗ Error creating '{data['title']}': {e}")

print(f"\n{'='*50}")
print(f"Summary:")
print(f"  Created: {created_count} announcements")
print(f"  Total in DB: {Announcement.objects.count()} announcements")
print(f"  Approved & Published: {Announcement.objects.filter(approval_status='approved', is_published=True).count()}")
print(f"{'='*50}")
