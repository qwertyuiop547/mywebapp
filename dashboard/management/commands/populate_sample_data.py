from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from complaints.models import Complaint, ComplaintCategory
from feedback.models import Feedback
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data for realistic home page'

    def handle(self, *args, **options):
        # Create sample residents if they don't exist
        self.stdout.write("Creating sample residents...")
        
        residents_data = [
            {'username': 'juan_dela_cruz', 'first_name': 'Juan', 'last_name': 'Dela Cruz', 'email': 'juan@example.com'},
            {'username': 'maria_santos', 'first_name': 'Maria', 'last_name': 'Santos', 'email': 'maria@example.com'},
            {'username': 'pedro_garcia', 'first_name': 'Pedro', 'last_name': 'Garcia', 'email': 'pedro@example.com'},
            {'username': 'ana_reyes', 'first_name': 'Ana', 'last_name': 'Reyes', 'email': 'ana@example.com'},
            {'username': 'carlos_lopez', 'first_name': 'Carlos', 'last_name': 'Lopez', 'email': 'carlos@example.com'},
        ]
        
        for resident_data in residents_data:
            if not User.objects.filter(username=resident_data['username']).exists():
                user = User.objects.create_user(
                    username=resident_data['username'],
                    email=resident_data['email'],
                    first_name=resident_data['first_name'],
                    last_name=resident_data['last_name'],
                    role='resident',
                    is_approved=True
                )
                self.stdout.write(f"Created resident: {user.username}")
        
        # Get complaint categories
        categories = ComplaintCategory.objects.all()
        if not categories.exists():
            self.stdout.write("No complaint categories found. Please run the complaint categories setup first.")
            return
        
        # Create sample complaints
        self.stdout.write("Creating sample complaints...")
        residents = User.objects.filter(role='resident', is_approved=True)
        
        complaint_descriptions = [
            "Ang ilaw sa kalye namin ay hindi gumagana ng ilang araw na.",
            "May problema sa drainage system sa aming area.",
            "Masyadong malakas ang ingay ng mga kapitbahay tuwing gabi.",
            "May mga bata na nanggugulo sa playground.",
            "Hindi nakakakuha ng tubig sa gripo ng mahigit 2 araw na.",
            "May basura na hindi nakokolekta sa aming street.",
            "Sira ang bangketa sa harap ng bahay namin.",
            "May mga stray dogs na nakakagulo sa area.",
            "Hindi gumagana ang public restroom sa plaza.",
            "May problema sa electrical wiring sa community center.",
        ]
        
        statuses = ['pending', 'in_progress', 'resolved', 'closed']
        
        for i in range(20):  # Create 20 sample complaints
            if residents.exists() and categories.exists():
                days_ago = random.randint(1, 60)
                created_date = datetime.now() - timedelta(days=days_ago)
                
                complaint = Complaint.objects.create(
                    title=f"Complaint #{i+1}",
                    description=random.choice(complaint_descriptions),
                    category=random.choice(categories),
                    complainant=random.choice(residents),
                    status=random.choice(statuses),
                    priority=random.choice(['low', 'medium', 'high'])
                )
                complaint.created_at = created_date
                complaint.save()
        
        self.stdout.write("Created 20 sample complaints")
        
        # Create sample feedback
        self.stdout.write("Creating sample feedback...")
        
        feedback_comments = [
            "Maganda ang serbisyo ng barangay!",
            "Mabilis na naaksyon ang aming complaint.",
            "Salamat sa mga programs para sa mga bata.",
            "Sana mas mapabuti pa ang street lighting.",
            "Napakahusay ng barangay officials.",
            "Maganda ang mga health programs.",
            "Sana may mas maraming recreational activities.",
            "Napakabait ng mga staff sa barangay hall.",
        ]
        
        for i in range(15):  # Create 15 sample feedback
            if residents.exists():
                days_ago = random.randint(1, 30)
                created_date = datetime.now() - timedelta(days=days_ago)
                
                feedback = Feedback.objects.create(
                    title=f"Feedback #{i+1}",
                    comment=random.choice(feedback_comments),
                    rating=random.randint(3, 5),
                    user=random.choice(residents),
                    feedback_type=random.choice(['usability', 'feature', 'general'])
                )
                feedback.created_at = created_date
                feedback.save()
        
        self.stdout.write("Created 15 sample feedback")
        self.stdout.write(self.style.SUCCESS("Successfully populated database with sample data!"))