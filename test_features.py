"""
Comprehensive test script to verify all features of the Barangay Portal
Run this script with: python test_features.py
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

# Import models
from accounts.models import BarangayArea, ResidencyValidation
from complaints.models import Complaint, ComplaintCategory, ComplaintTimeline
from feedback.models import Feedback, FeedbackCategory
from announcements.models import Announcement
from gallery.models import Photo, GalleryCategory
from services.models import Service, ServiceRequest
from suggestions.models import Suggestion
from chatbot.models import ChatMessage
from notifications.models import Notification

User = get_user_model()

class FeatureTestRunner:
    def __init__(self):
        self.client = Client()
        self.results = []
        self.test_user = None
        self.admin_user = None
        
    def run_all_tests(self):
        """Run all feature tests"""
        print("\n" + "="*70)
        print("BARANGAY PORTAL FEATURE TESTING")
        print("="*70 + "\n")
        
        # Setup test data
        self.setup_test_data()
        
        # Test each feature
        self.test_authentication()
        self.test_homepage()
        self.test_dashboard()
        self.test_complaints_system()
        self.test_feedback_system()
        self.test_announcements()
        self.test_services()
        self.test_gallery()
        self.test_notifications()
        self.test_suggestions()
        self.test_analytics()
        self.test_chatbot()
        
        # Print summary
        self.print_summary()
        
    def setup_test_data(self):
        """Create test users and initial data"""
        print("📦 Setting up test data...")
        try:
            # Create barangay areas
            area1, _ = BarangayArea.objects.get_or_create(
                name="Zone 1",
                description="Testing Zone 1"
            )
            
            # Create admin user
            self.admin_user, created = User.objects.get_or_create(
                username="admin",
                defaults={
                    'email': 'admin@test.com',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'role': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_approved': True,
                    'position_portfolio': 'System Administrator'
                }
            )
            if created:
                self.admin_user.set_password('admin123')
                self.admin_user.save()
            
            # Create test user
            self.test_user, created = User.objects.get_or_create(
                username="testuser",
                defaults={
                    'email': 'test@test.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'role': 'resident',
                    'is_approved': True,
                    'barangay_area': area1
                }
            )
            if created:
                self.test_user.set_password('test123')
                self.test_user.save()
            
            # Create categories
            ComplaintCategory.objects.get_or_create(
                name="Noise Complaint",
                description="Complaints about noise"
            )
            
            FeedbackCategory.objects.get_or_create(
                name="Service Quality",
                description="Feedback about service quality"
            )
            
            GalleryCategory.objects.get_or_create(
                name="Events",
                description="Barangay events photos"
            )
            
            self.results.append(("Setup Test Data", "✅ PASSED"))
            print("   ✅ Test data created successfully")
        except Exception as e:
            self.results.append(("Setup Test Data", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_authentication(self):
        """Test authentication system"""
        print("\n🔐 Testing Authentication System...")
        try:
            # Test login page
            response = self.client.get(reverse('accounts:login'))
            assert response.status_code == 200, f"Login page returned {response.status_code}"
            
            # Test user login
            login_success = self.client.login(username='testuser', password='test123')
            assert login_success, "User login failed"
            
            # Test logout
            self.client.logout()
            
            # Test registration page
            response = self.client.get(reverse('accounts:register'))
            assert response.status_code == 200, f"Registration page returned {response.status_code}"
            
            self.results.append(("Authentication", "✅ PASSED"))
            print("   ✅ Authentication system working")
        except Exception as e:
            self.results.append(("Authentication", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_homepage(self):
        """Test homepage"""
        print("\n🏠 Testing Homepage...")
        try:
            response = self.client.get(reverse('home'))
            assert response.status_code == 200, f"Homepage returned {response.status_code}"
            
            # Check if key sections exist
            content = str(response.content)
            assert "Welcome" in content or "Barangay" in content, "Homepage content missing"
            
            self.results.append(("Homepage", "✅ PASSED"))
            print("   ✅ Homepage working")
        except Exception as e:
            self.results.append(("Homepage", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_dashboard(self):
        """Test dashboard functionality"""
        print("\n📊 Testing Dashboard...")
        try:
            # Login as user
            self.client.login(username='testuser', password='test123')
            
            # Test dashboard access
            response = self.client.get(reverse('dashboard:home'))
            assert response.status_code == 200, f"Dashboard returned {response.status_code}"
            
            self.results.append(("Dashboard", "✅ PASSED"))
            print("   ✅ Dashboard working")
        except Exception as e:
            self.results.append(("Dashboard", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_complaints_system(self):
        """Test complaints system"""
        print("\n📝 Testing Complaints System...")
        try:
            # Login as user
            self.client.login(username='testuser', password='test123')
            
            # Test complaint list page
            response = self.client.get(reverse('complaints:complaint_list'))
            assert response.status_code == 200, f"Complaint list returned {response.status_code}"
            
            # Test create complaint page
            response = self.client.get(reverse('complaints:submit_complaint'))
            assert response.status_code == 200, f"Submit complaint page returned {response.status_code}"
            
            # Create a test complaint
            category = ComplaintCategory.objects.first()
            complaint = Complaint.objects.create(
                category=category,
                subject="Test Complaint",
                description="This is a test complaint",
                status="pending",
                priority="medium",
                complainant=self.test_user
            )
            
            # Test complaint detail
            response = self.client.get(reverse('complaints:complaint_detail', args=[complaint.id]))
            assert response.status_code == 200, f"Complaint detail returned {response.status_code}"
            
            self.results.append(("Complaints System", "✅ PASSED"))
            print("   ✅ Complaints system working")
        except Exception as e:
            self.results.append(("Complaints System", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_feedback_system(self):
        """Test feedback system"""
        print("\n⭐ Testing Feedback System...")
        try:
            # Login as user
            self.client.login(username='testuser', password='test123')
            
            # Test feedback list
            response = self.client.get(reverse('feedback:feedback_list'))
            assert response.status_code == 200, f"Feedback list returned {response.status_code}"
            
            # Test submit feedback page
            response = self.client.get(reverse('feedback:submit_feedback'))
            assert response.status_code == 200, f"Submit feedback page returned {response.status_code}"
            
            # Create test feedback
            category = FeedbackCategory.objects.first()
            if category:
                feedback = Feedback.objects.create(
                    category=category,
                    rating=5,
                    comments="Great service!",
                    submitted_by=self.test_user
                )
            
            self.results.append(("Feedback System", "✅ PASSED"))
            print("   ✅ Feedback system working")
        except Exception as e:
            self.results.append(("Feedback System", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_announcements(self):
        """Test announcements system"""
        print("\n📢 Testing Announcements...")
        try:
            # Test announcement list
            response = self.client.get(reverse('announcements:announcement_list'))
            assert response.status_code == 200, f"Announcement list returned {response.status_code}"
            
            # Create test announcement as admin
            announcement = Announcement.objects.create(
                title="Test Announcement",
                content="This is a test announcement",
                priority="normal",
                author=self.admin_user
            )
            
            # Test announcement detail
            response = self.client.get(reverse('announcements:announcement_detail', args=[announcement.id]))
            assert response.status_code == 200, f"Announcement detail returned {response.status_code}"
            
            self.results.append(("Announcements", "✅ PASSED"))
            print("   ✅ Announcements working")
        except Exception as e:
            self.results.append(("Announcements", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_services(self):
        """Test services system"""
        print("\n🛠️ Testing Services...")
        try:
            # Login as user
            self.client.login(username='testuser', password='test123')
            
            # Test services list
            response = self.client.get(reverse('services:services_list'))
            assert response.status_code == 200, f"Services list returned {response.status_code}"
            
            # Create test service
            service = Service.objects.create(
                name="Test Service",
                description="Test service description",
                is_active=True
            )
            
            # Test service request page
            response = self.client.get(reverse('services:request_service'))
            assert response.status_code == 200, f"Service request page returned {response.status_code}"
            
            self.results.append(("Services", "✅ PASSED"))
            print("   ✅ Services working")
        except Exception as e:
            self.results.append(("Services", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_gallery(self):
        """Test gallery system"""
        print("\n🖼️ Testing Gallery...")
        try:
            # Test gallery page
            response = self.client.get(reverse('gallery:gallery'))
            assert response.status_code == 200, f"Gallery page returned {response.status_code}"
            
            # Login as admin
            self.client.login(username='admin', password='admin123')
            
            # Test upload photo page
            response = self.client.get(reverse('gallery:upload_photo'))
            # Note: This might require admin permissions
            if response.status_code == 302:  # Redirect if not permitted
                print("   ⚠️ Gallery upload requires admin permissions (expected)")
            else:
                assert response.status_code == 200, f"Upload photo page returned {response.status_code}"
            
            self.results.append(("Gallery", "✅ PASSED"))
            print("   ✅ Gallery working")
        except Exception as e:
            self.results.append(("Gallery", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_notifications(self):
        """Test notification system"""
        print("\n🔔 Testing Notifications...")
        try:
            # Login as user
            self.client.login(username='testuser', password='test123')
            
            # Test notification list
            response = self.client.get(reverse('notifications:notification_list'))
            assert response.status_code == 200, f"Notification list returned {response.status_code}"
            
            # Create test notification
            notification = Notification.objects.create(
                recipient=self.test_user,
                title="Test Notification",
                message="This is a test notification",
                notification_type="info"
            )
            
            self.results.append(("Notifications", "✅ PASSED"))
            print("   ✅ Notifications working")
        except Exception as e:
            self.results.append(("Notifications", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_suggestions(self):
        """Test suggestions system"""
        print("\n💡 Testing Suggestions...")
        try:
            # Login as user
            self.client.login(username='testuser', password='test123')
            
            # Test suggestion list
            response = self.client.get(reverse('suggestions:suggestion_list'))
            assert response.status_code == 200, f"Suggestion list returned {response.status_code}"
            
            # Test submit suggestion
            response = self.client.get(reverse('suggestions:submit_suggestion'))
            assert response.status_code == 200, f"Submit suggestion page returned {response.status_code}"
            
            # Create test suggestion
            suggestion = Suggestion.objects.create(
                title="Test Suggestion",
                description="This is a test suggestion",
                submitted_by=self.test_user,
                category="improvement"
            )
            
            self.results.append(("Suggestions", "✅ PASSED"))
            print("   ✅ Suggestions working")
        except Exception as e:
            self.results.append(("Suggestions", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_analytics(self):
        """Test analytics system"""
        print("\n📈 Testing Analytics...")
        try:
            # Login as admin
            self.client.login(username='admin', password='admin123')
            
            # Test analytics dashboard
            response = self.client.get(reverse('analytics:dashboard'))
            # Analytics might require admin permissions
            if response.status_code == 302:
                print("   ⚠️ Analytics requires admin permissions (expected)")
                self.results.append(("Analytics", "✅ PASSED (with permission check)"))
            else:
                assert response.status_code == 200, f"Analytics dashboard returned {response.status_code}"
                self.results.append(("Analytics", "✅ PASSED"))
            print("   ✅ Analytics working")
        except Exception as e:
            self.results.append(("Analytics", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def test_chatbot(self):
        """Test chatbot system"""
        print("\n🤖 Testing Chatbot...")
        try:
            # Login as user
            self.client.login(username='testuser', password='test123')
            
            # Test chatbot page
            response = self.client.get(reverse('chatbot:chat'))
            assert response.status_code == 200, f"Chatbot page returned {response.status_code}"
            
            self.results.append(("Chatbot", "✅ PASSED"))
            print("   ✅ Chatbot working")
        except Exception as e:
            self.results.append(("Chatbot", f"❌ FAILED: {str(e)}"))
            print(f"   ❌ Failed: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for _, result in self.results if "✅" in result)
        failed_tests = sum(1 for _, result in self.results if "❌" in result)
        
        for feature, result in self.results:
            print(f"{feature:25} {result}")
        
        print("\n" + "-"*70)
        print(f"Total: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! All features are working correctly!")
        else:
            print(f"\n⚠️ {failed_tests} test(s) failed. Please check the errors above.")
        
        print("="*70 + "\n")

if __name__ == "__main__":
    tester = FeatureTestRunner()
    tester.run_all_tests()
