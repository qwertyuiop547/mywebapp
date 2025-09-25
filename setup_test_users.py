import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Test users with different roles for testing the assignment system
test_users = [
    {
        'username': 'tanod.head',
        'email': 'tanod@barangay.gov.ph',
        'first_name': 'Pedro',
        'last_name': 'Santos',
        'role': 'tanod_head',
        'position_portfolio': 'Head of Peace & Order Unit',
        'is_approved': True,
        'phone_number': '09123456789'
    },
    {
        'username': 'kagawad.peace',
        'email': 'peace@barangay.gov.ph',
        'first_name': 'Maria',
        'last_name': 'Cruz',
        'role': 'kagawad_peace',
        'position_portfolio': 'Peace & Order Committee Chair',
        'is_approved': True,
        'phone_number': '09234567890'
    },
    {
        'username': 'kagawad.health',
        'email': 'health@barangay.gov.ph',
        'first_name': 'Jose',
        'last_name': 'Reyes',
        'role': 'kagawad_health',
        'position_portfolio': 'Health Committee Chair',
        'is_approved': True,
        'phone_number': '09345678901'
    },
    {
        'username': 'lupon.chair',
        'email': 'lupon@barangay.gov.ph',
        'first_name': 'Ana',
        'last_name': 'Garcia',
        'role': 'lupon_chair',
        'position_portfolio': 'Lupon Tagapamayapa Chairperson',
        'is_approved': True,
        'phone_number': '09456789012'
    },
    {
        'username': 'bhw.main',
        'email': 'bhw@barangay.gov.ph',
        'first_name': 'Rosa',
        'last_name': 'Mendoza',
        'role': 'bhw',
        'position_portfolio': 'Senior Barangay Health Worker',
        'is_approved': True,
        'phone_number': '09567890123'
    },
    {
        'username': 'sk.chair',
        'email': 'sk@barangay.gov.ph',
        'first_name': 'Juan',
        'last_name': 'Dela Cruz Jr.',
        'role': 'sk_chair',
        'position_portfolio': 'SK Chairperson',
        'is_approved': True,
        'phone_number': '09678901234'
    },
    {
        'username': 'vaw.officer',
        'email': 'vaw@barangay.gov.ph',
        'first_name': 'Carmen',
        'last_name': 'Lopez',
        'role': 'vaw_officer',
        'position_portfolio': 'VAW Desk Officer',
        'is_approved': True,
        'phone_number': '09789012345'
    },
    {
        'username': 'animal.control',
        'email': 'animals@barangay.gov.ph',
        'first_name': 'Rico',
        'last_name': 'Magno',
        'role': 'animal_control',
        'position_portfolio': 'Animal Control Officer',
        'is_approved': True,
        'phone_number': '09890123456'
    },
    {
        'username': 'bdrrmc.focal',
        'email': 'disaster@barangay.gov.ph',
        'first_name': 'Elena',
        'last_name': 'Torres',
        'role': 'bdrrmc_focal',
        'position_portfolio': 'BDRRMC Focal Person',
        'is_approved': True,
        'phone_number': '09901234567'
    },
    {
        'username': 'badac.focal',
        'email': 'badac@barangay.gov.ph',
        'first_name': 'Roberto',
        'last_name': 'Villanueva',
        'role': 'badac_focal',
        'position_portfolio': 'BADAC Focal Person',
        'is_approved': True,
        'phone_number': '09012345678'
    }
]

print("Creating test users with barangay roles...")

created_count = 0
updated_count = 0

for user_data in test_users:
    username = user_data.pop('username')
    email = user_data.pop('email')
    
    user, created = User.objects.get_or_create(
        username=username,
        email=email,
        defaults={
            **user_data,
            'date_approved': timezone.now()
        }
    )
    
    if created:
        user.set_password('barangay123')  # Default password for testing
        user.save()
        print(f"✅ Created: {user.get_full_name()} ({user.get_role_display()})")
        created_count += 1
    else:
        # Update existing user with new role data
        for key, value in user_data.items():
            setattr(user, key, value)
        user.save()
        print(f"🔄 Updated: {user.get_full_name()} ({user.get_role_display()})")
        updated_count += 1

print(f"\n📊 Summary:")
print(f"   New users created: {created_count}")
print(f"   Existing users updated: {updated_count}")
print(f"   Total test users: {len(test_users)}")

print(f"\n🔐 All test users have password: 'barangay123'")
print(f"📧 Test user emails follow pattern: role@barangay.gov.ph")

# Show assignment coverage
print(f"\n📋 Role Assignment Coverage:")
print("═" * 40)
from complaints.models import CategoryAssignmentRule

rules = CategoryAssignmentRule.objects.all().select_related('category')
for rule in rules:
    primary_user = User.objects.filter(role=rule.default_assignee_role, is_approved=True).first()
    backup_user = User.objects.filter(role=rule.backup_assignee_role, is_approved=True).first() if rule.backup_assignee_role else None
    
    primary_status = "✅" if primary_user else "❌"
    backup_status = "✅" if backup_user or not rule.backup_assignee_role else "❌"
    
    print(f"{rule.category.name:<25} → {primary_status} {rule.get_default_assignee_role_display()}")
    if rule.backup_assignee_role:
        print(f"{'':25}   {backup_status} Backup: {rule.get_backup_assignee_role_display()}")

print(f"\n🎯 Ready to test auto-assignment! Create a complaint to see it in action.")