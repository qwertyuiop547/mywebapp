#!/usr/bin/env python3
"""
Script to populate the database with sample complaint data for testing
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from complaints.models import Complaint, ComplaintCategory

User = get_user_model()

def create_sample_data():
    """Create sample complaint categories and complaints"""
    
    print("🚀 Creating sample complaint data...")
    
    # Create complaint categories if they don't exist
    categories_data = [
        {'name': 'Infrastructure', 'description': 'Road repairs, street lighting, drainage'},
        {'name': 'Public Safety', 'description': 'Security concerns, crime reports'},
        {'name': 'Noise Complaint', 'description': 'Loud music, construction noise'},
        {'name': 'Waste Management', 'description': 'Garbage collection, littering'},
        {'name': 'Health & Sanitation', 'description': 'Water quality, health hazards'},
        {'name': 'Traffic', 'description': 'Traffic violations, road safety'},
        {'name': 'Other', 'description': 'General concerns and issues'},
    ]
    
    categories_created = 0
    for cat_data in categories_data:
        category, created = ComplaintCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            categories_created += 1
            print(f"  ✅ Created category: {category.name}")
    
    print(f"📁 Categories: {categories_created} created, {ComplaintCategory.objects.count()} total")
    
    # Get or create a resident user
    try:
        resident = User.objects.filter(role='resident', is_active=True).first()
        if not resident:
            # Create a test resident
            resident = User.objects.create_user(
                username='test_resident',
                email='resident@test.com',
                password='testpass123',
                first_name='Juan',
                last_name='Dela Cruz',
                role='resident',
                is_approved=True
            )
            print(f"  ✅ Created test resident: {resident.username}")
        
        print(f"👤 Using resident: {resident.get_full_name()} ({resident.username})")
    except Exception as e:
        print(f"❌ Error with resident user: {e}")
        return
    
    # Sample complaints data
    complaints_data = [
        {
            'title': 'Broken Street Light on Main Road',
            'description': 'The street light near the corner of Main Road and Rizal Street has been broken for 2 weeks. This creates safety concerns for pedestrians at night.',
            'category_name': 'Infrastructure',
            'priority': 'high',
            'status': 'pending',
            'location': 'Main Road, Corner Rizal Street'
        },
        {
            'title': 'Loud Music During Late Hours',
            'description': 'Neighbors playing loud music until 2 AM on weekends. This disturbs sleep and violates noise ordinances.',
            'category_name': 'Noise Complaint',
            'priority': 'medium',
            'status': 'in_progress',
            'location': 'Block 5, Lot 12, Subdivision'
        },
        {
            'title': 'Uncollected Garbage for 5 Days',
            'description': 'Garbage has not been collected in our area for 5 days. This is causing sanitation issues and attracting pests.',
            'category_name': 'Waste Management',
            'priority': 'high',
            'status': 'pending',
            'location': 'Barangay Street, Blocks 1-3'
        },
        {
            'title': 'Pothole on Community Road',
            'description': 'Large pothole has formed on the main community road. This is dangerous for vehicles and motorcycles.',
            'category_name': 'Infrastructure',
            'priority': 'medium',
            'status': 'resolved',
            'location': 'Community Road, in front of Barangay Hall'
        },
        {
            'title': 'Stray Dogs in the Area',
            'description': 'Increasing number of stray dogs in the neighborhood. Some appear aggressive and pose safety risks.',
            'category_name': 'Public Safety',
            'priority': 'medium',
            'status': 'in_progress',
            'location': 'Residential Area, Blocks 7-10'
        },
        {
            'title': 'Water Leak from Public Pipe',
            'description': 'Water pipe leak causing flooding in the street. Water is being wasted and creating muddy conditions.',
            'category_name': 'Infrastructure',
            'priority': 'urgent',
            'status': 'pending',
            'location': 'Corner of Peace Avenue and Unity Street'
        }
    ]
    
    complaints_created = 0
    for complaint_data in complaints_data:
        try:
            # Get category
            category = ComplaintCategory.objects.get(name=complaint_data['category_name'])
            
            # Create complaint
            complaint, created = Complaint.objects.get_or_create(
                title=complaint_data['title'],
                complainant=resident,
                defaults={
                    'description': complaint_data['description'],
                    'category': category,
                    'priority': complaint_data['priority'],
                    'status': complaint_data['status'],
                    'location': complaint_data['location'],
                    'created_at': timezone.now() - timedelta(days=complaints_created * 2)  # Spread out dates
                }
            )
            
            if created:
                complaints_created += 1
                print(f"  ✅ Created complaint: {complaint.title[:50]}...")
        
        except Exception as e:
            print(f"  ❌ Error creating complaint '{complaint_data['title']}': {e}")
    
    print(f"📋 Complaints: {complaints_created} created, {Complaint.objects.count()} total")
    
    # Show statistics
    print("\n📊 Current Statistics:")
    total = Complaint.objects.count()
    pending = Complaint.objects.filter(status='pending').count()
    in_progress = Complaint.objects.filter(status='in_progress').count()
    resolved = Complaint.objects.filter(status='resolved').count()
    
    print(f"  Total: {total}")
    print(f"  Pending: {pending}")
    print(f"  In Progress: {in_progress}")
    print(f"  Resolved: {resolved}")
    
    print("\n🎉 Sample data creation completed!")
    print("💡 Refresh your browser to see the updated complaint statistics.")

if __name__ == '__main__':
    create_sample_data()