#!/usr/bin/env python
"""
Create test resident accounts for testing the Resident Management system
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from accounts.models import User

def create_test_residents():
    """Create several test resident accounts"""
    
    residents_data = [
        {
            'username': 'juan_dela_cruz',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'email': 'juan@example.com',
            'role': 'resident',
            'is_approved': True,
            'is_active': True,
            'address': 'Block 1 Lot 15 Barangay Burgos',
            'phone_number': '09171234567',
        },
        {
            'username': 'maria_santos',
            'first_name': 'Maria',
            'last_name': 'Santos', 
            'email': 'maria@example.com',
            'role': 'resident',
            'is_approved': True,
            'is_active': True,
            'address': 'Block 2 Lot 8 Barangay Burgos',
            'phone_number': '09287654321',
        },
        {
            'username': 'pedro_garcia',
            'first_name': 'Pedro',
            'last_name': 'Garcia',
            'email': 'pedro@example.com', 
            'role': 'resident',
            'is_approved': False,  # Pending approval
            'is_active': True,
            'address': 'Block 3 Lot 22 Barangay Burgos',
            'phone_number': '09351234567',
        },
        {
            'username': 'ana_reyes',
            'first_name': 'Ana',
            'last_name': 'Reyes',
            'email': 'ana@example.com',
            'role': 'resident', 
            'is_approved': True,
            'is_active': False,  # Inactive account
            'address': 'Block 1 Lot 30 Barangay Burgos',
            'phone_number': '09456789012',
        },
        {
            'username': 'jose_lopez',
            'first_name': 'Jose',
            'last_name': 'Lopez',
            'email': 'jose@example.com',
            'role': 'resident',
            'is_approved': True,
            'is_active': True,
            'address': 'Block 4 Lot 5 Barangay Burgos',
            'phone_number': '09123456789',
        },
    ]
    
    print("Creating test resident accounts...")
    
    for resident_data in residents_data:
        username = resident_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"  ❌ Resident '{username}' already exists, skipping...")
            continue
        
        # Create the user
        user = User.objects.create_user(
            username=username,
            password='testpassword123',  # Simple password for testing
            **{k: v for k, v in resident_data.items() if k != 'username'}
        )
        
        status = "Active" if user.is_active and user.is_approved else (
            "Inactive" if not user.is_active else "Pending Approval"
        )
        
        print(f"  ✅ Created resident: {user.get_full_name()} ({username}) - {status}")
    
    print("\n📊 Resident Statistics:")
    total_residents = User.objects.filter(role='resident').count()
    active_residents = User.objects.filter(role='resident', is_active=True, is_approved=True).count()
    inactive_residents = User.objects.filter(role='resident', is_active=False).count()
    pending_residents = User.objects.filter(role='resident', is_approved=False).count()
    
    print(f"  Total Residents: {total_residents}")
    print(f"  Active: {active_residents}")
    print(f"  Inactive: {inactive_residents}")
    print(f"  Pending Approval: {pending_residents}")
    
    print("\n🎯 Test the Resident Management system:")
    print("  1. Login as Chairman")
    print("  2. Go to Dashboard → 'Manage Residents'")
    print("  3. Try deactivating/activating residents")
    print("  4. Try searching and filtering")
    print("  5. Test the delete functionality (with caution)")

if __name__ == '__main__':
    create_test_residents()
