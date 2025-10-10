"""
Simple Feature Check for Barangay Portal
Run with: python check_features.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from django.urls import reverse, resolve
from django.test import Client
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def check_database_connection():
    """Check if database is accessible"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True, "Database connection successful"
    except Exception as e:
        return False, f"Database error: {str(e)}"

def check_urls():
    """Check if all main URLs are configured"""
    urls_to_check = [
        ('home', '/'),
        ('accounts:login', '/accounts/login/'),
        ('accounts:register', '/accounts/register/'),
        ('dashboard:home', '/dashboard/'),
        ('complaints:complaint_list', '/complaints/'),
        ('feedback:feedback_list', '/feedback/'),
        ('announcements:announcement_list', '/announcements/'),
        ('gallery:gallery', '/gallery/'),
        ('services:services_list', '/services/'),
        ('notifications:notification_list', '/notifications/'),
        ('suggestions:suggestion_list', '/suggestions/'),
        ('chatbot:chat', '/chatbot/'),
    ]
    
    results = []
    for name, path in urls_to_check:
        try:
            if ':' in name:
                url = reverse(name)
            else:
                url = reverse(name)
            results.append((name, True, "URL configured"))
        except Exception as e:
            results.append((name, False, f"URL not found: {str(e)}"))
    
    return results

def check_models():
    """Check if all models can be accessed"""
    models_to_check = [
        ('accounts.User', 'User model'),
        ('complaints.Complaint', 'Complaint model'),
        ('feedback.Feedback', 'Feedback model'),
        ('announcements.Announcement', 'Announcement model'),
        ('gallery.Photo', 'Gallery Photo model'),
        ('services.Service', 'Service model'),
        ('notifications.Notification', 'Notification model'),
        ('suggestions.Suggestion', 'Suggestion model'),
        ('chatbot.ChatMessage', 'Chatbot Message model'),
    ]
    
    results = []
    for model_path, description in models_to_check:
        try:
            app_name, model_name = model_path.split('.')
            from django.apps import apps
            model = apps.get_model(app_name, model_name)
            count = model.objects.count()
            results.append((description, True, f"Model accessible ({count} records)"))
        except Exception as e:
            results.append((description, False, f"Model error: {str(e)}"))
    
    return results

def check_templates():
    """Check if key templates exist"""
    import os
    from pathlib import Path
    
    BASE_DIR = Path(__file__).resolve().parent
    templates_to_check = [
        'templates/base.html',
        'templates/home.html',
        'accounts/templates/accounts/login.html',
        'accounts/templates/accounts/register.html',
        'dashboard/templates/dashboard/home.html',
        'complaints/templates/complaints/complaint_list.html',
        'feedback/templates/feedback/feedback_list.html',
        'announcements/templates/announcements/announcement_list.html',
    ]
    
    results = []
    for template_path in templates_to_check:
        full_path = BASE_DIR / template_path
        if os.path.exists(full_path):
            results.append((template_path, True, "Template exists"))
        else:
            # Check alternative path
            alt_path = BASE_DIR / template_path.replace('/', '\\')
            if os.path.exists(alt_path):
                results.append((template_path, True, "Template exists"))
            else:
                results.append((template_path, False, "Template not found"))
    
    return results

def check_static_files():
    """Check if static files are configured"""
    from django.conf import settings
    import os
    
    results = []
    
    # Check static directories
    if hasattr(settings, 'STATICFILES_DIRS'):
        for static_dir in settings.STATICFILES_DIRS:
            if os.path.exists(static_dir):
                results.append((f"Static dir: {static_dir}", True, "Directory exists"))
            else:
                results.append((f"Static dir: {static_dir}", False, "Directory not found"))
    
    # Check key static files
    static_files = [
        'css/style.css',
        'css/responsive-system.css',
        'js/responsive-enhancements.js',
    ]
    
    for file_path in static_files:
        full_path = os.path.join(settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else '', file_path)
        if os.path.exists(full_path):
            results.append((f"Static file: {file_path}", True, "File exists"))
        else:
            results.append((f"Static file: {file_path}", False, "File not found"))
    
    return results

def run_all_checks():
    """Run all system checks"""
    print("\n" + "="*70)
    print("BARANGAY PORTAL SYSTEM CHECK")
    print("="*70 + "\n")
    
    all_results = []
    
    # 1. Database Connection
    print("📊 Checking Database Connection...")
    db_ok, db_msg = check_database_connection()
    print(f"   {'✅' if db_ok else '❌'} {db_msg}")
    all_results.append(("Database", db_ok))
    
    # 2. URL Configuration
    print("\n🔗 Checking URL Configuration...")
    url_results = check_urls()
    for name, ok, msg in url_results:
        if ok:
            print(f"   ✅ {name}: {msg}")
        else:
            print(f"   ❌ {name}: {msg}")
    all_results.append(("URLs", all([r[1] for r in url_results])))
    
    # 3. Models
    print("\n📦 Checking Models...")
    model_results = check_models()
    for name, ok, msg in model_results:
        if ok:
            print(f"   ✅ {name}: {msg}")
        else:
            print(f"   ❌ {name}: {msg}")
    all_results.append(("Models", all([r[1] for r in model_results])))
    
    # 4. Templates
    print("\n📄 Checking Templates...")
    template_results = check_templates()
    for name, ok, msg in template_results:
        if ok:
            print(f"   ✅ {name}: {msg}")
        else:
            print(f"   ❌ {name}: {msg}")
    all_results.append(("Templates", all([r[1] for r in template_results])))
    
    # 5. Static Files
    print("\n🎨 Checking Static Files...")
    static_results = check_static_files()
    for name, ok, msg in static_results:
        if ok:
            print(f"   ✅ {name}: {msg}")
        else:
            print(f"   ❌ {name}: {msg}")
    all_results.append(("Static Files", all([r[1] for r in static_results])))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    total_categories = len(all_results)
    passed_categories = sum(1 for _, ok in all_results if ok)
    
    for category, ok in all_results:
        status = "✅ PASSED" if ok else "❌ NEEDS ATTENTION"
        print(f"{category:15} {status}")
    
    print("\n" + "-"*70)
    
    if passed_categories == total_categories:
        print("🎉 All systems operational! The portal is ready to use!")
        print("\nYou can access the portal at: http://127.0.0.1:8000")
        print("\nDefault accounts:")
        print("  Admin: username='admin', password='admin123'")
        print("  User: username='testuser', password='test123'")
    else:
        print(f"⚠️ {total_categories - passed_categories} system(s) need attention.")
        print("Please check the errors above for details.")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_checks()
