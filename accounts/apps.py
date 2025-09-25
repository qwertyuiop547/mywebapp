from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    verbose_name = 'User Accounts'
    
    def ready(self):
        import accounts.signals
        
        # Auto-create admin user on Railway deployment
        import os
        if 'RAILWAY_ENVIRONMENT_NAME' in os.environ:
            self.create_default_admin()
    
    def create_default_admin(self):
        try:
            from django.contrib.auth import get_user_model
            from django.db import IntegrityError
            
            User = get_user_model()
            
            # Default users to create
            default_users = [
                {
                    'username': 'chairman',
                    'email': 'chairman@brgyburgosbasey.gov.ph',
                    'password': 'burgos2025',
                    'first_name': 'Barangay',
                    'last_name': 'Chairman',
                    'role': 'chairman',
                    'is_approved': True,
                    'is_staff': True,
                    'is_superuser': True
                },
                {
                    'username': 'secretary',
                    'email': 'secretary@brgyburgosbasey.gov.ph',
                    'password': 'secretary2025',
                    'first_name': 'Barangay',
                    'last_name': 'Secretary',
                    'role': 'secretary',
                    'is_approved': True,
                    'is_staff': True,
                    'is_superuser': False
                },
                {
                    'username': 'resident',
                    'email': 'resident@brgyburgosbasey.gov.ph',
                    'password': 'resident2025',
                    'first_name': 'Test',
                    'last_name': 'Resident',
                    'role': 'resident',
                    'is_approved': True,
                    'is_staff': False,
                    'is_superuser': False
                }
            ]
            
            # Create default users
            for user_data in default_users:
                if not User.objects.filter(username=user_data['username']).exists():
                    User.objects.create_user(**user_data)
                    print(f"✅ Default {user_data['role']} user '{user_data['username']}' created successfully!")
                else:
                    print(f"ℹ️ User '{user_data['username']}' already exists.")
                    
        except Exception as e:
            print(f"❌ Error creating default users: {e}")