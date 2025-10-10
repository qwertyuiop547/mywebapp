"""
Test all endpoints to verify they are responding correctly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    """Test all main endpoints"""
    
    endpoints = [
        ("Homepage", "/", "GET", 200),
        ("Admin", "/admin/", "GET", [200, 302]),
        ("Login", "/en/accounts/login/", "GET", 200),
        ("Register", "/en/accounts/register/", "GET", 200),
        ("Dashboard", "/en/dashboard/", "GET", [200, 302]),  # May redirect to login
        ("Complaints", "/en/complaints/", "GET", [200, 302]),
        ("Feedback", "/en/feedback/", "GET", [200, 302]),
        ("Announcements", "/en/announcements/", "GET", 200),
        ("Gallery", "/en/gallery/", "GET", 200),
        ("Services", "/en/services/", "GET", [200, 302]),
        ("Notifications", "/en/notifications/", "GET", [200, 302]),
        ("Suggestions", "/en/suggestions/", "GET", [200, 302]),
        ("Chatbot", "/en/chatbot/", "GET", [200, 302]),
        ("Quick Stats API", "/quick-stats/", "GET", 200),
    ]
    
    print("\n" + "="*70)
    print("TESTING BARANGAY PORTAL ENDPOINTS")
    print("="*70 + "\n")
    
    session = requests.Session()
    all_passed = True
    results = []
    
    for name, endpoint, method, expected_status in endpoints:
        try:
            url = BASE_URL + endpoint
            
            if method == "GET":
                response = session.get(url, timeout=5)
            else:
                response = session.post(url, timeout=5)
            
            # Handle multiple expected status codes
            if isinstance(expected_status, list):
                success = response.status_code in expected_status
                status_str = f"{response.status_code} (expected: {expected_status})"
            else:
                success = response.status_code == expected_status
                status_str = f"{response.status_code} (expected: {expected_status})"
            
            if success:
                print(f"✅ {name:20} {endpoint:30} Status: {status_str}")
                results.append((name, True))
            else:
                print(f"❌ {name:20} {endpoint:30} Status: {status_str}")
                results.append((name, False))
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name:20} {endpoint:30} Connection Error - Is the server running?")
            results.append((name, False))
            all_passed = False
        except Exception as e:
            print(f"❌ {name:20} {endpoint:30} Error: {str(e)}")
            results.append((name, False))
            all_passed = False
    
    # Test authentication flow
    print("\n" + "-"*70)
    print("TESTING AUTHENTICATION FLOW")
    print("-"*70 + "\n")
    
    # Try to login with test credentials
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': 'test'  # This might not work with CSRF enabled
    }
    
    try:
        login_url = BASE_URL + "/en/accounts/login/"
        
        # First GET to get CSRF token (if needed)
        response = session.get(login_url)
        
        # Try POST login (may fail due to CSRF)
        response = session.post(login_url, data=login_data)
        
        if response.status_code in [200, 302]:
            print(f"✅ Login endpoint accessible (Status: {response.status_code})")
        else:
            print(f"⚠️ Login endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Could not test login: {str(e)}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results)
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Endpoints Tested: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if all_passed:
        print("\n🎉 ALL ENDPOINTS ARE WORKING!")
        print("\n📝 NOTES:")
        print("- Some endpoints may redirect (302) to login page if authentication is required")
        print("- This is normal behavior for protected pages")
        print("- The portal is functioning correctly!")
    else:
        print("\n⚠️ Some endpoints need attention.")
        print("- Check if the development server is running: python manage.py runserver")
        print("- Redirects (302) to login are normal for protected pages")
    
    print("\n🌐 You can access the portal at: http://127.0.0.1:8000")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_endpoints()
