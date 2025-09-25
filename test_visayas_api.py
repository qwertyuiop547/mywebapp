#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from chatbot.api_services import weather_service

def test_visayas_api():
    print("🌪️ Testing Enhanced Visayas Typhoon API...")
    print("=" * 50)
    
    # Test typhoon detection
    result = weather_service._get_real_typhoon_status('fil')
    
    if result:
        message = result[0]['message']
        priority = result[0]['priority']
        
        print(f"✅ API Response received!")
        print(f"📊 Priority Level: {priority}")
        print(f"📝 Message Preview:")
        print("-" * 30)
        print(message[:300] + "..." if len(message) > 300 else message)
        print("-" * 30)
        
        # Check if it contains Visayas-specific information
        visayas_keywords = ['visayas', 'basey', 'tacloban', 'samar', 'leyte']
        has_visayas_info = any(keyword.lower() in message.lower() for keyword in visayas_keywords)
        
        if has_visayas_info:
            print("🎯 ✅ Contains Visayas-specific information!")
        else:
            print("⚠️ General response (APIs may be down)")
            
        # Check for real-time data indicators
        realtime_keywords = ['real-time', 'wind', 'km/h', 'temperature', 'humidity']
        has_realtime = any(keyword.lower() in message.lower() for keyword in realtime_keywords)
        
        if has_realtime:
            print("📡 ✅ Contains real-time weather data!")
        else:
            print("📡 ⚠️ Using fallback seasonal data")
            
    else:
        print("❌ No response received")
    
    print("\n🌐 Configured Visayas API Endpoints:")
    print("• https://wttr.in/Basey,Samar,Philippines")
    print("• https://wttr.in/Tacloban,Leyte,Philippines") 
    print("• https://wttr.in/Catbalogan,Samar,Philippines")
    print("• https://wttr.in/Ormoc,Leyte,Philippines")
    print("• https://wttr.in/Cebu,Philippines")

if __name__ == "__main__":
    test_visayas_api()
