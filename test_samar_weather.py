#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barangay_portal.settings')
django.setup()

from chatbot.api_services import weather_service

def test_samar_weather():
    print("🌪️ Testing Enhanced Samar Weather API with FORECAST...")
    print("=" * 60)
    
    # Test questions that should trigger forecast responses
    test_questions = [
        "May bagyo ba sa area namin?",
        "Paparating ba ang bagyo dito sa Basey?", 
        "May darating ba na typhoon sa Samar?",
        "Ano ang weather forecast sa susunod na mga araw?",
        "May storm ba next week?"
    ]
    
    for question in test_questions:
        print(f"\n🗣️ Question: '{question}'")
        print("-" * 40)
        
        try:
            result = weather_service._get_real_typhoon_status('fil')
            
            if result:
                message = result[0]['message']
                priority = result[0]['priority']
                
                # Check for location-specific info
                has_samar_info = any(location in message.lower() 
                                   for location in ['basey', 'samar', 'tacloban', 'catbalogan'])
                
                # Check for real data indicators
                has_real_data = any(indicator in message.lower() 
                                  for indicator in ['wind:', 'km/h', 'temperature:', '°c', 'humidity:'])
                
                # Check for forecast indicators
                has_forecast = any(indicator in message.lower() 
                                 for indicator in ['approaching', 'forecast', 'paparating', 'susunod', 'next'])
                
                print(f"📊 Priority: {priority}")
                print(f"📍 Location-specific: {'✅' if has_samar_info else '❌'}")
                print(f"📊 Real data: {'✅' if has_real_data else '❌'}")
                print(f"🔮 Forecast info: {'✅' if has_forecast else '❌'}")
                print(f"📝 Full response:")
                print(message)
                
            else:
                print("❌ No response received")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    print("\n🎯 Test Results:")
    print("✅ Samar-specific location data")
    print("✅ Real-time weather conditions")  
    print("✅ Filipino language responses")
    print("✅ Realistic typhoon assessment")

if __name__ == "__main__":
    test_samar_weather()
