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
            
            # Create default admin if not exists
            if not User.objects.filter(username='chairman').exists():
                User.objects.create_user(
                    username='chairman',
                    email='chairman@brgyburgosbasey.gov.ph',
                    password='burgos2025',
                    first_name='Barangay',
                    last_name='Chairman',
                    role='chairman',
                    is_approved=True,
                    is_staff=True,
                    is_superuser=True
                )
                print("✅ Default admin user 'chairman' created successfully!")
            else:
                print("ℹ️ Admin user 'chairman' already exists.")
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")