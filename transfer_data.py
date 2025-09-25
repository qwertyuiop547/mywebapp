#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from accounts.models import User
from complaints.models import Complaint
from feedback.models import Feedback

def transfer_data():
    print("📋 Transferring sample data to current user...")
    print("=" * 50)
    
    try:
        # Get both users
        source_user = User.objects.get(username='juan_dela_cruz')
        target_user = User.objects.get(username='resident1')
        
        print(f"Source: {source_user.username} ({source_user.get_full_name()})")
        print(f"Target: {target_user.username} ({target_user.get_full_name()})")
        print()
        
        # Transfer complaints
        complaints = Complaint.objects.filter(complainant=source_user)
        print(f"Transferring {complaints.count()} complaints...")
        
        for complaint in complaints:
            complaint.complainant = target_user
            complaint.save()
            print(f"  ✅ Transferred: {complaint.title[:50]}...")
        
        # Transfer feedback
        feedback = Feedback.objects.filter(user=source_user)
        print(f"\nTransferring {feedback.count()} feedback entries...")
        
        for fb in feedback:
            fb.user = target_user
            fb.save()
            print(f"  ✅ Transferred feedback: {fb.category.name if fb.category else 'No category'}")
        
        print(f"\n🎉 Transfer complete!")
        print(f"Target user now has:")
        print(f"  Complaints: {target_user.complaints.count()}")
        print(f"  Feedback: {target_user.feedbacks.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    transfer_data()