#!/usr/bin/env python
import os
import django
import sys
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from accounts.models import User
from complaints.models import Complaint, ComplaintCategory
from feedback.models import Feedback

def create_realistic_barangay_data():
    print("🏢 Creating Realistic Barangay Data...")
    print("=" * 60)
    
    try:
        # Get current user
        user = User.objects.get(username='resident1')
        print(f"👤 Adding data for: {user.get_full_name()}")
        
        # Create more realistic Filipino barangay complaint categories
        barangay_categories = [
            'Kalat at Basura', 'Drainage at Baha', 'Sira na Kalsada', 'Maingay na Kapitbahay',
            'Stray Animals', 'Streetlights na Sira', 'Tubig at Kanal', 'Illegal Parking',
            'Puno na Nakaharang', 'Mga Tambay', 'Illegal Construction', 'Smoke Belching',
            'Masamang Amoy', 'Security Issues', 'Barangay Services'
        ]
        
        categories = {}
        for cat_name in barangay_categories:
            category, created = ComplaintCategory.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'Mga reklamo tungkol sa {cat_name.lower()}'}
            )
            categories[cat_name] = category
            if created:
                print(f"  ✅ Created category: {cat_name}")
        
        # Delete existing complaints to start fresh
        Complaint.objects.filter(complainant=user).delete()
        print(f"🧹 Cleared existing complaints")
        
        # Create realistic complaints with Filipino context
        complaints_data = [
            {
                'title': 'Nakabara ang Drainage sa Looban Street',
                'description': 'Yung drainage sa Looban Street ay nakabara na dahil sa mga basura. Kapag umuulan, bumabaha na agad sa amin. Nakakasama sa kalusugan at delikado sa mga bata. Sana po maaayos na agad.',
                'category': 'Drainage at Baha',
                'priority': 'high',
                'location': 'Looban Street, Purok 3',
                'status': 'pending'
            },
            {
                'title': 'Hindi Kinokollect ang Basura sa amin',
                'description': 'Mahigit 1 linggo na pong hindi kinokollect ang basura dito sa Purok 2. Nagsisimula na pong maging masangsang at maraming langaw. May mga aso rin na nakakalat ng basura.',
                'category': 'Kalat at Basura',
                'priority': 'high',
                'location': 'Purok 2, Mabini Street',
                'status': 'in_progress'
            },
            {
                'title': 'Sira na Streetlight sa Main Road',
                'description': 'Yung streetlight sa tapat ng sari-sari store ni Aling Rosa ay sira na po. Madilim na sa gabi at nakatakot na maglakad doon. Maraming holdaper din daw sa lugar na yun.',
                'category': 'Streetlights na Sira',
                'priority': 'medium',
                'location': 'Main Road, tapat ng Rosa Store',
                'status': 'resolved'
            },
            {
                'title': 'Sobrang Ingay ng Videoke sa Kapitbahay',
                'description': 'Yung kapitbahay namin sa Purok 1 ay palaging may videoke hanggang madaling araw. Hindi na kami makatulog ng mga anak ko. Paulit-ulit na rin namin sinasabi pero hindi naman nakikinig.',
                'category': 'Maingay na Kapitbahay',
                'priority': 'medium',
                'location': 'Purok 1, House #15',
                'status': 'in_progress'
            },
            {
                'title': 'Maraming Asong Gala sa Barangay',
                'description': 'Dumami na ang mga asong gala dito sa amin. Minsan aggressive pa at nakatakot sa mga bata. May mga nabibites na rin daw. Sana po may dog catching program.',
                'category': 'Stray Animals',
                'priority': 'medium',
                'location': 'Buong Barangay',
                'status': 'pending'
            },
            {
                'title': 'Butas na Kalsada sa Rizal Avenue',
                'description': 'Yung kalsada sa Rizal Avenue ay puno na ng mga butas. Delikado sa mga motor at sasakyan. May mga aksidente na rin nangyayari. Lalo na kapag tag-ulan, hindi na makita ang mga butas.',
                'category': 'Sira na Kalsada',
                'priority': 'high',
                'location': 'Rizal Avenue, malapit sa Elementary School',
                'status': 'pending'
            },
            {
                'title': 'Walang Tubig sa Purok 4',
                'description': 'Mahigit 3 araw na kaming walang tubig dito sa Purok 4. Nahihirapan kaming mag-laba at maligo. Yung mga bata namin ay hindi rin makapasok sa school dahil walang panligo.',
                'category': 'Tubig at Kanal',
                'priority': 'high',
                'location': 'Purok 4, lahat ng bahay',
                'status': 'pending'
            },
            {
                'title': 'Illegally Parked na Jeepney',
                'description': 'May jeepney na palaging nakapark sa harap ng barangay hall. Humaharang siya sa daan at nahihirapan kaming dumaan. Minsan traffic pa dahil doon.',
                'category': 'Illegal Parking',
                'priority': 'low',
                'location': 'Harap ng Barangay Hall',
                'status': 'resolved'
            },
            {
                'title': 'Puno na Nakaharang sa Linya ng Kuryente',
                'description': 'May puno dito sa amin na nakaharang na sa mga linya ng kuryente. Delikado na at baka magka-short circuit. Lalo na kapag malakas ang hangin.',
                'category': 'Puno na Nakaharang',
                'priority': 'high',
                'location': 'Santos Street, Purok 3',
                'status': 'in_progress'
            },
            {
                'title': 'Mga Tambay sa Basketball Court',
                'description': 'Maraming tambay sa basketball court na hindi naman naglalaro. Nag-iinuman pa sila doon at nagiging maingay. Hindi na rin magamit ng mga kabataan ang court.',
                'category': 'Mga Tambay',
                'priority': 'medium',
                'location': 'Barangay Basketball Court',
                'status': 'pending'
            }
        ]
        
        print(f"\n📝 Creating {len(complaints_data)} realistic complaints...")
        
        for i, complaint_data in enumerate(complaints_data):
            # Create complaint with realistic dates (within last 2 months)
            days_ago = random.randint(1, 60)
            created_date = datetime.now() - timedelta(days=days_ago)
            
            complaint = Complaint.objects.create(
                title=complaint_data['title'],
                description=complaint_data['description'],
                category=categories[complaint_data['category']],
                priority=complaint_data['priority'],
                location=complaint_data['location'],
                status=complaint_data['status'],
                complainant=user,
                created_at=created_date
            )
            print(f"  ✅ {i+1}. {complaint_data['title'][:50]}... | {complaint_data['status']}")
        
        # Create feedback categories - using the actual feedback types from the model
        feedback_types = ['usability', 'feature', 'bug', 'general']
        
        # Delete existing feedback to start fresh
        Feedback.objects.filter(user=user).delete()
        
        # Create realistic feedback
        feedback_data = [
            {
                'title': 'Maganda ang Portal',
                'comment': 'Napakabait ng mga staff sa barangay hall. Mabilis din ang serbisyo. Salamat sa online portal na ito.',
                'rating': 5,
                'feedback_type': 'general'
            },
            {
                'title': 'Mas Mapabilis pa sana',
                'comment': 'Sana po mas mapabilis pa ang pag-aayos ng mga reklamo. Ang tagal po minsan bago ma-respond.',
                'rating': 3,
                'feedback_type': 'general'
            },
            {
                'title': 'User-friendly na Website',
                'comment': 'Madali gamitin ang website. Hindi mahirap mag-navigate. Salamat sa mga developers.',
                'rating': 4,
                'feedback_type': 'usability'
            },
            {
                'title': 'Sana may Mobile App',
                'comment': 'Sana po may mobile app para mas madali ma-access sa phone. Minsan kasi mahirap mag-browse sa mobile.',
                'rating': 4,
                'feedback_type': 'feature'
            },
            {
                'title': 'May Bug sa Upload',
                'comment': 'Minsan hindi nag-upload ang mga pictures na kasama sa complaint. Pero overall okay naman.',
                'rating': 3,
                'feedback_type': 'bug'
            }
        ]
        
        print(f"\n💬 Creating {len(feedback_data)} feedback entries...")
        
        for feedback_item in feedback_data:
            Feedback.objects.create(
                user=user,
                title=feedback_item['title'],
                comment=feedback_item['comment'],
                rating=feedback_item['rating'],
                feedback_type=feedback_item['feedback_type'],
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            print(f"  ✅ {feedback_item['title']}: {feedback_item['rating']} stars ({feedback_item['feedback_type']})")
        
        print(f"\n🎉 Successfully created realistic barangay data!")
        print(f"📊 Final counts:")
        print(f"   Complaints: {user.complaints.count()}")
        print(f"   Feedback: {user.feedbacks.count()}")
        print(f"   Complaint Categories: {ComplaintCategory.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_realistic_barangay_data()