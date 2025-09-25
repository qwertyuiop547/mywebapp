#!/usr/bin/env python3
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from announcements.models import Announcement
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def main():
    # Get chairman
    chairman = User.objects.filter(role='chairman').first()
    if not chairman:
        print("No chairman found!")
        return
    
    # Check current announcements
    all_announcements = Announcement.objects.all()
    print(f"Total announcements: {all_announcements.count()}")
    
    for ann in all_announcements:
        print(f"ID: {ann.id}, Title: {ann.title}, Status: {ann.approval_status}, Published: {ann.is_published}")
    
    # Approve the first "Missing" announcement for testing
    missing_announcement = Announcement.objects.filter(title='Missing').first()
    if missing_announcement:
        print(f"\nApproving announcement: {missing_announcement.title}")
        missing_announcement.approve(chairman)
        print(f"✅ Approved by: {missing_announcement.approved_by.username}")
        print(f"✅ Approved at: {missing_announcement.approved_at}")
        print(f"✅ New status: {missing_announcement.approval_status}")
    else:
        print("No 'Missing' announcement found")
    
    # Check approved announcements that will show publicly
    approved_count = Announcement.objects.filter(
        is_published=True,
        approval_status='approved',
        publish_date__lte=timezone.now()
    ).exclude(expiry_date__lt=timezone.now()).count()
    
    print(f"\nAnnouncements visible to residents: {approved_count}")

if __name__ == '__main__':
    main()
