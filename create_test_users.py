#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from accounts.models import User

def create_test_users():
    print("Creating test users...")
    
    # Create Chairman user
    if not User.objects.filter(username='chairman').exists():
        chairman = User.objects.create_user(
            username='chairman',
            email='chairman@barangay.gov.ph',
            password='chairman123',
            first_name='Maria',
            last_name='Santos',
            role='chairman',
            is_approved=True
        )
        print("✅ Chairman user created:")
        print(f"   Username: chairman")
        print(f"   Password: chairman123")
        print(f"   Email: chairman@barangay.gov.ph")
        print(f"   Role: Chairman")
    else:
        print("⚠️ Chairman user already exists")
    
    # Create Secretary user
    if not User.objects.filter(username='secretary').exists():
        secretary = User.objects.create_user(
            username='secretary',
            email='secretary@barangay.gov.ph',
            password='secretary123',
            first_name='Juan',
            last_name='Cruz',
            role='secretary',
            is_approved=True
        )
        print("\n✅ Secretary user created:")
        print(f"   Username: secretary")
        print(f"   Password: secretary123")
        print(f"   Email: secretary@barangay.gov.ph")
        print(f"   Role: Secretary")
    else:
        print("⚠️ Secretary user already exists")
    
    # Create Resident users
    residents = [
        {
            'username': 'resident1',
            'email': 'juan.dela.cruz@gmail.com',
            'password': 'resident123',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz'
        },
        {
            'username': 'resident2', 
            'email': 'maria.garcia@gmail.com',
            'password': 'resident123',
            'first_name': 'Maria',
            'last_name': 'Garcia'
        },
        {
            'username': 'testuser',
            'email': 'test@gmail.com', 
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    ]
    
    print("\n✅ Resident users:")
    for resident_data in residents:
        if not User.objects.filter(username=resident_data['username']).exists():
            resident = User.objects.create_user(
                username=resident_data['username'],
                email=resident_data['email'],
                password=resident_data['password'],
                first_name=resident_data['first_name'],
                last_name=resident_data['last_name'],
                role='resident',
                is_approved=True
            )
            print(f"   Username: {resident_data['username']}")
            print(f"   Password: {resident_data['password']}")
            print(f"   Email: {resident_data['email']}")
            print(f"   Role: Resident")
            print()
        else:
            print(f"⚠️ User {resident_data['username']} already exists")
    
    print("\n" + "="*50)
    print("🎉 TEST CREDENTIALS SUMMARY")
    print("="*50)
    print("\n📋 ADMIN ACCESS:")
    print("   Chairman: chairman / chairman123")
    print("   Secretary: secretary / secretary123")
    
    print("\n👥 RESIDENT ACCESS:")
    print("   Resident 1: resident1 / resident123")
    print("   Resident 2: resident2 / resident123") 
    print("   Test User: testuser / testpass123")
    
    print("\n🔗 Login URL: http://127.0.0.1:8000/accounts/login/")
    print("="*50)

if __name__ == '__main__':
    create_test_users()