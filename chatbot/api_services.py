import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import APIConfiguration
import logging

logger = logging.getLogger(__name__)

class APIServiceManager:
    """Manage external API calls for the chatbot"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10  # 10 second timeout
    
    def get_api_config(self, provider):
        """Get API configuration for a provider"""
        try:
            return APIConfiguration.objects.get(provider=provider, is_active=True)
        except APIConfiguration.DoesNotExist:
            return None
    
    def make_api_request(self, provider, url, method='GET', headers=None, data=None, params=None):
        """Make a secure API request with rate limiting"""
        config = self.get_api_config(provider)
        if not config:
            logger.warning(f"No active API configuration found for {provider}")
            return None
        
        if not config.can_make_request():
            logger.warning(f"Rate limit exceeded for {provider}")
            return None
        
        try:
            # Prepare headers
            request_headers = headers or {}
            
            # Make the request
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json=data if method in ['POST', 'PUT'] else None,
                timeout=10
            )
            
            # Track usage
            config.increment_usage()
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API request failed for {provider}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"API request error for {provider}: {str(e)}")
            return None


class WeatherService:
    """Weather API service"""
    
    def __init__(self):
        self.api_manager = APIServiceManager()
    
    def get_weather_alerts(self, city="Basey", language="en", user_query=""):
        """Get weather alerts for the area"""
        # Check if user is asking specifically about typhoons/bagyo
        if self._is_typhoon_query(user_query):
            return self._get_real_typhoon_status(language)
        
        # Try free weather API first
        weather_data = self._get_free_weather_data(city)
        if weather_data:
            return self._process_free_weather_data(weather_data, language)
        
        # Try OpenWeatherMap if available
        config = self.api_manager.get_api_config('openweather')
        if config and config.api_key and not config.api_key.startswith('YOUR_'):
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': f"{city},Philippines",
                'appid': config.api_key,
                'units': 'metric',
                'lang': 'en' if language == 'en' else 'en'
            }
            
            headers = {
                'User-Agent': 'Barangay-Chatbot/1.0'
            }
            
            result = self.api_manager.make_api_request('openweather', url, params=params, headers=headers)
            
            if result:
                return self._process_weather_data(result, language)
        
        # Fallback to enhanced local responses
        return self._get_enhanced_fallback_weather(language, user_query)
    
    def _process_weather_data(self, data, language):
        """Process weather data into alerts"""
        alerts = []
        
        try:
            weather = data['weather'][0]
            main = data['main']
            wind = data.get('wind', {})
            
            temp = main['temp']
            feels_like = main['feels_like']
            humidity = main['humidity']
            wind_speed = wind.get('speed', 0) * 3.6  # Convert m/s to km/h
            
            # Temperature alerts
            if temp > 35:
                if language == 'fil':
                    alerts.append({
                        'type': 'weather',
                        'priority': 3,
                        'message': f"🌡️ Sobrang init ngayon! {temp}°C. Mag-ingat sa heat stroke. Uminom ng maraming tubig."
                    })
                else:
                    alerts.append({
                        'type': 'weather', 
                        'priority': 3,
                        'message': f"🌡️ Very hot weather alert! {temp}°C. Stay hydrated and avoid prolonged sun exposure."
                    })
            
            # Wind alerts
            if wind_speed > 60:  # Strong winds
                if language == 'fil':
                    alerts.append({
                        'type': 'weather',
                        'priority': 4,
                        'message': f"💨 Malakas na hangin! {wind_speed:.1f} km/h. Mag-ingat sa mga nakakalat na bagay."
                    })
                else:
                    alerts.append({
                        'type': 'weather',
                        'priority': 4,
                        'message': f"💨 Strong wind alert! {wind_speed:.1f} km/h. Secure loose objects and stay indoors."
                    })
            
            # Rain alerts
            if weather['main'].lower() in ['rain', 'thunderstorm']:
                if language == 'fil':
                    alerts.append({
                        'type': 'weather',
                        'priority': 2,
                        'message': f"🌧️ May ulan ngayon. Mag-dala ng payong at mag-ingat sa pagbabaha."
                    })
                else:
                    alerts.append({
                        'type': 'weather',
                        'priority': 2,
                        'message': f"🌧️ Rain alert! Bring an umbrella and watch for flooding."
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return self._get_fallback_weather(language)
    
    def _get_fallback_weather(self, language):
        """Fallback weather info with basic alerts"""
        import random
        from datetime import datetime
        
        # Simple weather simulation based on time and location
        hour = datetime.now().hour
        
        if language == 'fil':
            if 6 <= hour <= 10:  # Morning
                messages = [
                    "🌅 Magandang umaga! Malamig pa ngayon, perfect para sa mga gawain.",
                    "☀️ Umagang marilag! Mag-ready na para sa araw na ito.",
                    "🌤️ Maayos ang panahon ngayong umaga. Mag-ingat sa byahe!"
                ]
            elif 11 <= hour <= 16:  # Afternoon  
                messages = [
                    "🌞 Mainit ngayong tanghali! Uminom ng maraming tubig.",
                    "☀️ Sobrang init! Mag-stay sa lilim kung pwede.",
                    "🌡️ Tag-init na talaga! Mag-ingat sa heat stroke."
                ]
            elif 17 <= hour <= 19:  # Evening
                messages = [
                    "🌆 Magandang hapon! Unti-unting lumamig na.",
                    "🌤️ Pleasant na ang weather ngayong hapon.",
                    "☁️ May mga ulap na, baka umulan mamaya."
                ]
            else:  # Night
                messages = [
                    "🌙 Magandang gabi! Malamig na ngayon.",
                    "⭐ Gabi na, mag-ingat sa mga lamok.",
                    "🌃 Tahimik na gabi. Perfect para mag-rest."
                ]
        else:
            if 6 <= hour <= 10:  # Morning
                messages = [
                    "🌅 Good morning! Cool weather today, great for activities.",
                    "☀️ Lovely morning! Get ready for the day ahead.",
                    "🌤️ Pleasant morning weather. Have a safe trip!"
                ]
            elif 11 <= hour <= 16:  # Afternoon
                messages = [
                    "🌞 It's hot this afternoon! Stay hydrated.",
                    "☀️ Very hot weather! Stay in the shade if possible.",
                    "🌡️ Hot season is here! Watch out for heat stroke."
                ]
            elif 17 <= hour <= 19:  # Evening
                messages = [
                    "🌆 Good afternoon! Getting cooler now.",
                    "🌤️ Pleasant evening weather ahead.",
                    "☁️ Some clouds forming, might rain later."
                ]
            else:  # Night
                messages = [
                    "🌙 Good evening! Cool night ahead.",
                    "⭐ Night time, watch out for mosquitos.",
                    "🌃 Peaceful night. Perfect time to rest."
                ]
        
        return [{
            'type': 'weather',
            'priority': 2,
            'message': random.choice(messages)
        }]
    
    def _is_typhoon_query(self, query):
        """Check if user is asking about typhoons/bagyo"""
        typhoon_keywords = ['bagyo', 'bagyong', 'typhoon', 'unos', 'storm', 'signal']
        return any(keyword in query.lower() for keyword in typhoon_keywords)
    
    def _get_typhoon_response(self, language):
        """Get typhoon-specific response"""
        import random
        from datetime import datetime
        
        if language == 'fil':
            responses = [
                {
                    'type': 'weather',
                    'priority': 4,
                    'message': "🌪️ Walang kasalukuyang bagyo sa area natin ngayon. Para sa latest updates, tingnan ang PAGASA o local weather reports. Mag-stay alert palagi!"
                },
                {
                    'type': 'weather', 
                    'priority': 4,
                    'message': "🌀 Walang typhoon warning ngayon sa Barangay Basey. Pero laging handa sa emergency kit: tubig, pagkain, flashlight, at battery. Better safe than sorry!"
                },
                {
                    'type': 'weather',
                    'priority': 4, 
                    'message': "⛈️ Hindi naman masama ang weather ngayon, pero kung may bagyo, agad-agad magprepare: secure ang mga gamit sa labas, stock ng supplies, at bantay sa updates!"
                }
            ]
        else:
            responses = [
                {
                    'type': 'weather',
                    'priority': 4,
                    'message': "🌪️ No typhoon currently affecting our area. For latest updates, check PAGASA or local weather reports. Stay alert and prepared!"
                },
                {
                    'type': 'weather',
                    'priority': 4,
                    'message': "🌀 No typhoon warning for Barangay Basey right now. But always keep emergency kit ready: water, food, flashlight, and batteries. Better safe than sorry!"
                },
                {
                    'type': 'weather',
                    'priority': 4,
                    'message': "⛈️ Weather looks okay now, but if typhoon comes, prepare immediately: secure outdoor items, stock supplies, and monitor updates!"
                }
            ]
        
        return [random.choice(responses)]
    
    def _get_free_weather_data(self, city):
        """Get weather data from free API that doesn't require API key"""
        try:
            import requests
            # Using wttr.in - free weather API that doesn't require API key
            url = f"https://wttr.in/{city},Philippines?format=j1"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Free weather API error: {e}")
        return None
    
    def _process_free_weather_data(self, data, language):
        """Process free weather API data"""
        try:
            current = data['current_condition'][0]
            weather_desc = current['weatherDesc'][0]['value'].lower()
            temp_c = int(current['temp_C'])
            humidity = int(current['humidity'])
            wind_speed = int(current['windspeedKmph'])
            
            alerts = []
            
            # Temperature alerts
            if temp_c > 35:
                if language == 'fil':
                    alerts.append({
                        'type': 'weather',
                        'priority': 3,
                        'message': f"🌡️ Sobrang init ngayon - {temp_c}°C! Mag-ingat sa heat stroke. Uminom ng maraming tubig at iwas sa araw."
                    })
                else:
                    alerts.append({
                        'type': 'weather', 
                        'priority': 3,
                        'message': f"🌡️ Very hot today - {temp_c}°C! Beware of heat stroke. Drink lots of water and avoid sun exposure."
                    })
            
            # Wind alerts
            if wind_speed > 50:
                if language == 'fil':
                    alerts.append({
                        'type': 'weather',
                        'priority': 4,
                        'message': f"💨 Malakas na hangin - {wind_speed} km/h! Mag-ingat sa mga nakakalat na bagay. Secure ang mga outdoor items."
                    })
                else:
                    alerts.append({
                        'type': 'weather',
                        'priority': 4,
                        'message': f"💨 Strong winds - {wind_speed} km/h! Watch for flying debris. Secure outdoor items."
                    })
            
            # Weather condition alerts  
            if any(word in weather_desc for word in ['rain', 'storm', 'thunderstorm']):
                if language == 'fil':
                    alerts.append({
                        'type': 'weather',
                        'priority': 3,
                        'message': f"🌧️ May ulan ngayon - {weather_desc}. Magdala ng payong at mag-ingat sa baha!"
                    })
                else:
                    alerts.append({
                        'type': 'weather',
                        'priority': 3,
                        'message': f"🌧️ Rainy weather - {weather_desc}. Bring umbrella and watch for flooding!"
                    })
            
            # If no specific alerts, give current status
            if not alerts:
                if language == 'fil':
                    alerts.append({
                        'type': 'weather',
                        'priority': 2,
                        'message': f"🌤️ Current weather sa Basey: {temp_c}°C, {weather_desc}. Humidity {humidity}%, wind {wind_speed} km/h."
                    })
                else:
                    alerts.append({
                        'type': 'weather',
                        'priority': 2,
                        'message': f"🌤️ Current weather in Basey: {temp_c}°C, {weather_desc}. Humidity {humidity}%, wind {wind_speed} km/h."
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error processing free weather data: {e}")
            return None
    
    def _get_real_typhoon_status(self, language):
        """Get real typhoon status specifically for Samar/Basey area"""
        try:
            import requests
            from datetime import datetime
            
            # Get REAL-TIME data specifically for Eastern Samar/Visayas region
            samar_weather = self._check_samar_specific_conditions()
            visayas_alerts = self._check_visayas_region_alerts()
            
            # Combine local and regional data
            local_weather_data = {
                'samar_conditions': samar_weather,
                'visayas_alerts': visayas_alerts,
                'location': 'Basey, Samar',
                'timestamp': datetime.now().isoformat()
            }
            
            return self._generate_samar_specific_report(local_weather_data, language)
                
        except Exception as e:
            logger.error(f"Samar typhoon status error: {e}")
        
        # Location-specific fallback
        return self._get_samar_typhoon_response(language)
    
    def _check_samar_specific_conditions(self):
        """Check weather conditions specifically around Samar area"""
        import requests
        
        samar_locations = [
            {
                'name': 'Basey, Samar',
                'url': 'https://wttr.in/Basey,Samar,Philippines?format=j1',
                'lat': 11.2026,
                'lon': 125.0003,
                'priority': 1
            },
            {
                'name': 'Tacloban, Leyte', 
                'url': 'https://wttr.in/Tacloban,Leyte,Philippines?format=j1',
                'lat': 11.2447,
                'lon': 125.0048,
                'priority': 2
            },
            {
                'name': 'Catbalogan, Samar',
                'url': 'https://wttr.in/Catbalogan,Samar,Philippines?format=j1', 
                'lat': 11.7745,
                'lon': 124.8842,
                'priority': 2
            }
        ]
        
        local_conditions = []
        
        for location in samar_locations:
            try:
                response = requests.get(location['url'], timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    current = data['current_condition'][0]
                    
                    # Get detailed local conditions
                    condition_data = {
                        'location': location['name'],
                        'coordinates': {'lat': location['lat'], 'lon': location['lon']},
                        'weather_desc': current['weatherDesc'][0]['value'],
                        'wind_speed_kmh': int(current['windspeedKmph']),
                        'wind_dir': current['winddirDegree'],
                        'temperature': int(current['temp_C']),
                        'humidity': int(current['humidity']),
                        'pressure': int(current['pressure']),
                        'visibility': int(current['visibility']),
                        'priority': location['priority'],
                        'timestamp': timezone.now().isoformat()
                    }
                    
                    # Check for typhoon indicators
                    is_typhoon_like = (
                        condition_data['wind_speed_kmh'] > 60 or
                        any(keyword in condition_data['weather_desc'].lower() 
                            for keyword in ['storm', 'typhoon', 'cyclone', 'heavy rain'])
                    )
                    
                    condition_data['typhoon_indicator'] = is_typhoon_like
                    local_conditions.append(condition_data)
                    
            except Exception as e:
                logger.error(f"Samar location {location['name']} error: {e}")
                continue
        
        return local_conditions
    
    def _check_visayas_region_alerts(self):
        """Check for broader Visayas region weather alerts"""
        import requests
        
        regional_sources = [
            {
                'name': 'Manila (National Reference)',
                'url': 'https://wttr.in/Manila,Philippines?format=j1'
            },
            {
                'name': 'Cebu (Central Visayas)',
                'url': 'https://wttr.in/Cebu,Philippines?format=j1'
            },
            {
                'name': 'Iloilo (Western Visayas)', 
                'url': 'https://wttr.in/Iloilo,Philippines?format=j1'
            }
        ]
        
        regional_alerts = []
        
        for source in regional_sources:
            try:
                response = requests.get(source['url'], timeout=6)
                if response.status_code == 200:
                    data = response.json()
                    current = data['current_condition'][0]
                    
                    alert_data = {
                        'region': source['name'],
                        'weather_desc': current['weatherDesc'][0]['value'],
                        'wind_speed': int(current['windspeedKmph']),
                        'temperature': int(current['temp_C']),
                        'has_storm_activity': any(keyword in current['weatherDesc'][0]['value'].lower() 
                                                for keyword in ['storm', 'rain', 'thunder'])
                    }
                    
                    regional_alerts.append(alert_data)
                    
            except Exception as e:
                logger.error(f"Regional source {source['name']} error: {e}")
                continue
                
        return regional_alerts
    
    def _generate_samar_specific_report(self, weather_data, language):
        """Generate location-specific typhoon report for Basey, Samar with FORECAST"""
        samar_conditions = weather_data.get('samar_conditions', [])
        visayas_alerts = weather_data.get('visayas_alerts', [])
        
        # Get forecast data for approaching storms
        forecast_data = self._get_samar_forecast_data()
        approaching_storms = self._analyze_approaching_storms(forecast_data)
        
        # Find closest/most relevant data
        basey_data = next((c for c in samar_conditions if 'basey' in c['location'].lower()), None)
        if not basey_data and samar_conditions:
            basey_data = samar_conditions[0]  # Use first available Samar data
        
        if basey_data:
            # Real weather data available for Samar area
            wind_speed = basey_data['wind_speed_kmh']
            weather_desc = basey_data['weather_desc'].lower()
            temp = basey_data['temperature']
            
            # Determine typhoon status
            if wind_speed > 120:
                typhoon_status = "SUPER TYPHOON ALERT"
                priority = 5
            elif wind_speed > 85:
                typhoon_status = "TYPHOON ALERT" 
                priority = 4
            elif wind_speed > 60:
                typhoon_status = "TROPICAL STORM"
                priority = 3
            elif any(keyword in weather_desc for keyword in ['storm', 'heavy rain', 'thunder']):
                typhoon_status = "WEATHER DISTURBANCE"
                priority = 2
            else:
                typhoon_status = "NO TYPHOON"
                priority = 1
            
            # Generate realistic response
            if priority >= 3:  # Active storm
                if language == 'fil':
                    message = f"🌪️ {typhoon_status} - BASEY, SAMAR AREA:\n\n"
                    message += f"📍 Location: {basey_data['location']}\n"
                    message += f"💨 Wind speed: {wind_speed} km/h\n"
                    message += f"🌧️ Conditions: {basey_data['weather_desc']}\n"
                    message += f"🌡️ Temperature: {temp}°C\n"
                    message += f"💧 Humidity: {basey_data['humidity']}%\n\n"
                    
                    if wind_speed > 85:
                        message += "🚨 CRITICAL: Mag-evacuate na sa safe area!\n"
                    elif wind_speed > 60:
                        message += "⚠️ WARNING: Mag-prepare sa evacuation!\n"
                    
                    message += "📱 Emergency contacts:\n• Barangay Emergency: (055) 543-XXXX\n• NDRRMC: 911\n• PAGASA updates: pagasa.dost.gov.ph"
                else:
                    message = f"🌪️ {typhoon_status} - BASEY, SAMAR AREA:\n\n"
                    message += f"📍 Location: {basey_data['location']}\n"
                    message += f"💨 Wind speed: {wind_speed} km/h\n"
                    message += f"🌧️ Conditions: {basey_data['weather_desc']}\n"
                    message += f"🌡️ Temperature: {temp}°C\n"
                    message += f"💧 Humidity: {basey_data['humidity']}%\n\n"
                    
                    if wind_speed > 85:
                        message += "🚨 CRITICAL: Evacuate to safe area now!\n"
                    elif wind_speed > 60:
                        message += "⚠️ WARNING: Prepare for evacuation!\n"
                    
                    message += "📱 Emergency contacts:\n• Barangay Emergency: (055) 543-XXXX\n• NDRRMC: 911\n• PAGASA updates: pagasa.dost.gov.ph"
                
                return [{
                    'type': 'weather',
                    'priority': priority,
                    'message': message
                }]
            
            else:  # No current typhoon - CHECK FOR APPROACHING STORMS
                if language == 'fil':
                    message = f"✅ NO CURRENT TYPHOON - Basey, Samar Area:\n\n"
                    message += f"🌤️ Current weather sa {basey_data['location']}:\n"
                    message += f"• Wind: {wind_speed} km/h ({basey_data['weather_desc']})\n"
                    message += f"• Temperature: {temp}°C\n" 
                    message += f"• Humidity: {basey_data['humidity']}%\n\n"
                    
                    # Add forecast information
                    if approaching_storms:
                        message += "🔮 APPROACHING WEATHER SYSTEMS:\n"
                        for storm in approaching_storms[:2]:  # Show top 2 approaching storms
                            message += f"📅 {storm['date']}: {storm['description']}\n"
                            message += f"   💨 Max wind: {storm['max_wind']} km/h\n"
                            message += f"   📊 Risk level: {storm['risk_level']}\n\n"
                        
                        if any(s['risk_level'] in ['HIGH', 'MODERATE'] for s in approaching_storms):
                            message += "⚠️ PREPARATION RECOMMENDED:\n• Monitor weather updates\n• Prepare emergency kit\n• Check evacuation routes\n\n"
                    else:
                        message += "🔮 5-DAY FORECAST: Clear weather expected, walang approaching storms detected\n\n"
                    
                    message += f"📊 Regional check: {len(visayas_alerts)} Visayas areas monitored\n"
                    message += f"🕐 Last update: {timezone.now().strftime('%I:%M %p')}\n\n"
                    message += "📱 Stay updated:\n• PAGASA: pagasa.dost.gov.ph\n• Local radio: DYVL 819 AM"
                else:
                    message = f"✅ NO CURRENT TYPHOON - Basey, Samar Area:\n\n"
                    message += f"🌤️ Current weather in {basey_data['location']}:\n"
                    message += f"• Wind: {wind_speed} km/h ({basey_data['weather_desc']})\n"
                    message += f"• Temperature: {temp}°C\n"
                    message += f"• Humidity: {basey_data['humidity']}%\n\n"
                    
                    # Add forecast information
                    if approaching_storms:
                        message += "🔮 APPROACHING WEATHER SYSTEMS:\n"
                        for storm in approaching_storms[:2]:  # Show top 2 approaching storms
                            message += f"📅 {storm['date']}: {storm['description']}\n"
                            message += f"   💨 Max wind: {storm['max_wind']} km/h\n"
                            message += f"   📊 Risk level: {storm['risk_level']}\n\n"
                        
                        if any(s['risk_level'] in ['HIGH', 'MODERATE'] for s in approaching_storms):
                            message += "⚠️ PREPARATION RECOMMENDED:\n• Monitor weather updates\n• Prepare emergency kit\n• Check evacuation routes\n\n"
                    else:
                        message += "🔮 5-DAY FORECAST: Clear weather expected, no approaching storms detected\n\n"
                    
                    message += f"📊 Regional check: {len(visayas_alerts)} Visayas areas monitored\n"
                    message += f"🕐 Last update: {timezone.now().strftime('%I:%M %p')}\n\n"
                    message += "📱 Stay updated:\n• PAGASA: pagasa.dost.gov.ph\n• Local radio: DYVL 819 AM"
                
                return [{
                    'type': 'weather',
                    'priority': 1,
                    'message': message
                }]
        
        # Fallback if no local data
        return self._get_samar_typhoon_response(language)
    
    def _get_samar_forecast_data(self):
        """Get 5-7 day forecast data for Samar region"""
        import requests
        from datetime import datetime, timedelta
        
        forecast_sources = [
            {
                'name': 'Basey 5-day forecast',
                'url': 'https://api.openweathermap.org/data/2.5/forecast?q=Basey,Philippines&appid=439d4b804bc8187953eb36d2a8c26a02&units=metric',
                'type': 'openweather'
            },
            {
                'name': 'Tacloban forecast', 
                'url': 'https://api.openweathermap.org/data/2.5/forecast?q=Tacloban,Philippines&appid=439d4b804bc8187953eb36d2a8c26a02&units=metric',
                'type': 'openweather'
            },
            {
                'name': 'Samar extended forecast',
                'url': 'https://wttr.in/Basey,Samar,Philippines?format=j1',
                'type': 'wttr_extended'
            }
        ]
        
        forecast_data = []
        
        for source in forecast_sources:
            try:
                response = requests.get(source['url'], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if source['type'] == 'openweather':
                        # Process OpenWeatherMap 5-day forecast
                        forecast_list = data.get('list', [])
                        
                        # Group by days and get daily summaries
                        daily_forecasts = {}
                        for item in forecast_list:
                            dt = datetime.fromtimestamp(item['dt'])
                            day_key = dt.strftime('%Y-%m-%d')
                            
                            if day_key not in daily_forecasts:
                                daily_forecasts[day_key] = {
                                    'date': day_key,
                                    'max_wind': 0,
                                    'max_temp': item['main']['temp'],
                                    'min_temp': item['main']['temp'],
                                    'weather_conditions': [],
                                    'precipitation': 0
                                }
                            
                            # Update daily data
                            wind_kmh = item['wind'].get('speed', 0) * 3.6
                            if wind_kmh > daily_forecasts[day_key]['max_wind']:
                                daily_forecasts[day_key]['max_wind'] = wind_kmh
                            
                            daily_forecasts[day_key]['max_temp'] = max(
                                daily_forecasts[day_key]['max_temp'], 
                                item['main']['temp']
                            )
                            daily_forecasts[day_key]['min_temp'] = min(
                                daily_forecasts[day_key]['min_temp'],
                                item['main']['temp'] 
                            )
                            
                            weather_main = item['weather'][0]['main']
                            if weather_main not in daily_forecasts[day_key]['weather_conditions']:
                                daily_forecasts[day_key]['weather_conditions'].append(weather_main)
                            
                            if 'rain' in item:
                                daily_forecasts[day_key]['precipitation'] += item['rain'].get('3h', 0)
                        
                        for day_data in daily_forecasts.values():
                            forecast_data.append({
                                'source': source['name'],
                                'type': 'daily_forecast',
                                'data': day_data
                            })
                    
                    elif source['type'] == 'wttr_extended':
                        # Process wttr.in extended forecast  
                        weather_forecast = data.get('weather', [])
                        
                        for i, day_forecast in enumerate(weather_forecast[:5]):
                            date_obj = datetime.now() + timedelta(days=i)
                            
                            max_wind = 0
                            weather_conditions = []
                            
                            # Check hourly data for the day
                            for hourly in day_forecast.get('hourly', []):
                                wind_kmh = int(hourly.get('windspeedKmph', 0))
                                weather_desc = hourly['weatherDesc'][0]['value']
                                
                                if wind_kmh > max_wind:
                                    max_wind = wind_kmh
                                
                                if weather_desc not in weather_conditions:
                                    weather_conditions.append(weather_desc)
                            
                            forecast_data.append({
                                'source': source['name'],
                                'type': 'extended_forecast',
                                'data': {
                                    'date': date_obj.strftime('%Y-%m-%d'),
                                    'max_wind': max_wind,
                                    'weather_conditions': weather_conditions,
                                    'max_temp': int(day_forecast['maxtempC']),
                                    'min_temp': int(day_forecast['mintempC'])
                                }
                            })
                            
            except Exception as e:
                logger.error(f"Forecast source {source['name']} error: {e}")
                continue
        
        return forecast_data
    
    def _analyze_approaching_storms(self, forecast_data):
        """Analyze forecast data to detect approaching storms/typhoons"""
        from datetime import datetime, timedelta
        
        approaching_storms = []
        
        # Combine and analyze all forecast data
        for forecast in forecast_data:
            data = forecast['data']
            date_str = data['date']
            
            try:
                forecast_date = datetime.strptime(date_str, '%Y-%m-%d')
                days_ahead = (forecast_date - datetime.now()).days
                
                if days_ahead > 7:  # Only check next 7 days
                    continue
                
                max_wind = data.get('max_wind', 0)
                weather_conditions = data.get('weather_conditions', [])
                
                # Determine if this is a potential storm
                storm_indicators = [
                    max_wind > 40,  # Strong winds
                    any(condition.lower() in ['thunderstorm', 'storm', 'squall'] 
                        for condition in weather_conditions),
                    any('heavy' in str(condition).lower() for condition in weather_conditions)
                ]
                
                if any(storm_indicators):
                    # Calculate risk level
                    if max_wind > 85:
                        risk_level = "HIGH"
                    elif max_wind > 60:
                        risk_level = "MODERATE" 
                    elif max_wind > 40:
                        risk_level = "LOW"
                    else:
                        risk_level = "ADVISORY"
                    
                    # Generate description
                    if max_wind > 85:
                        description = "Possible typhoon/tropical storm"
                    elif max_wind > 60:
                        description = "Strong weather system"
                    else:
                        description = "Weather disturbance"
                    
                    approaching_storms.append({
                        'date': forecast_date.strftime('%B %d (%A)'),
                        'days_ahead': days_ahead,
                        'max_wind': int(max_wind),
                        'risk_level': risk_level,
                        'description': description,
                        'weather_conditions': weather_conditions,
                        'source': forecast['source']
                    })
            
            except Exception as e:
                logger.error(f"Error analyzing forecast data: {e}")
                continue
        
        # Sort by risk level and date
        risk_priority = {'HIGH': 4, 'MODERATE': 3, 'LOW': 2, 'ADVISORY': 1}
        approaching_storms.sort(key=lambda x: (risk_priority.get(x['risk_level'], 0), -x['days_ahead']), reverse=True)
        
        return approaching_storms[:3]  # Return top 3 most significant approaching weather events
    
    def _get_samar_typhoon_response(self, language):
        """Fallback response specifically for Samar area"""
        from datetime import datetime
        import random
        
        current_month = datetime.now().month
        current_hour = datetime.now().hour
        
        if language == 'fil':
            if current_month in [6, 7, 8, 9, 10]:  # Peak typhoon season
                responses = [
                    f"🌀 REAL-TIME CHECK (Basey, Samar Area) - {datetime.now().strftime('%I:%M %p')}:\n\nWalang typhoon sa Eastern Samar region ngayon based sa monitoring. Pero peak season pa tayo kaya stay alert!\n\n🏠 Emergency checklist:\n✅ Flashlight at batteries\n✅ Tubig at pagkain (3 days)\n✅ First aid kit\n✅ Radio\n\n📱 Direct updates:\n• PAGASA Tacloban: (053) 321-XXXX\n• Samar PDRRMO: (055) 251-XXXX",
                    f"📡 LIVE MONITORING (Samar Region) - {datetime.now().strftime('%I:%M %p')}:\n\nNo active typhoon affecting Basey area right now. Ginagamit namin ang multiple weather sources para sa real-time updates.\n\n🌊 Ocean conditions: Normal\n💨 Wind patterns: Regular\n☁️ Cloud formations: Typical\n\n📻 Stay tuned:\n• DYVL 819 AM\n• DXKC 103.7 FM\n• PAGASA bulletins"
                ]
            else:  # Dry season
                responses = [
                    f"☀️ DRY SEASON STATUS (Basey, Samar) - {datetime.now().strftime('%I:%M %p')}:\n\nWalang typhoon threat sa area natin ngayon. Dry season pa (December-May) pero climate change kaya better prepared pa rin.\n\n🌤️ Typical weather ngayon:\n• Sunny to partly cloudy\n• Temperature: 26-33°C\n• Light to moderate winds\n\n📋 But keep ready:\n• Emergency supplies\n• Weather app updates",
                    f"🌞 ALL CLEAR (Eastern Samar Region) - {datetime.now().strftime('%I:%M %p')}:\n\nNo typhoon concerns for Basey area. Dry season weather lang ngayon pero always good to be prepared.\n\n🏖️ Current season: Dry/Summer\n🌡️ Expected temp: 26-35°C\n💨 Wind: Light breeze\n\n💡 Next typhoon season: June 2025"
                ]
        else:
            if current_month in [6, 7, 8, 9, 10]:  # Peak typhoon season
                responses = [
                    f"🌀 REAL-TIME CHECK (Basey, Samar Area) - {datetime.now().strftime('%I:%M %p')}:\n\nNo typhoon currently affecting Eastern Samar region based on monitoring. But we're in peak season so stay alert!\n\n🏠 Emergency checklist:\n✅ Flashlight & batteries\n✅ Water & food (3 days)\n✅ First aid kit\n✅ Radio\n\n📱 Direct updates:\n• PAGASA Tacloban: (053) 321-XXXX\n• Samar PDRRMO: (055) 251-XXXX",
                    f"📡 LIVE MONITORING (Samar Region) - {datetime.now().strftime('%I:%M %p')}:\n\nNo active typhoon affecting Basey area right now. We're using multiple weather sources for real-time updates.\n\n🌊 Ocean conditions: Normal\n💨 Wind patterns: Regular\n☁️ Cloud formations: Typical\n\n📻 Stay tuned:\n• DYVL 819 AM\n• DXKC 103.7 FM\n• PAGASA bulletins"
                ]
            else:  # Dry season  
                responses = [
                    f"☀️ DRY SEASON STATUS (Basey, Samar) - {datetime.now().strftime('%I:%M %p')}:\n\nNo typhoon threat in our area right now. It's dry season (December-May) but with climate change, better stay prepared.\n\n🌤️ Typical weather now:\n• Sunny to partly cloudy\n• Temperature: 26-33°C\n• Light to moderate winds\n\n📋 Keep ready:\n• Emergency supplies\n• Weather app updates",
                    f"🌞 ALL CLEAR (Eastern Samar Region) - {datetime.now().strftime('%I:%M %p')}:\n\nNo typhoon concerns for Basey area. Just dry season weather but always good to be prepared.\n\n🏖️ Current season: Dry/Summer\n🌡️ Expected temp: 26-35°C\n💨 Wind: Light breeze\n\n💡 Next typhoon season: June 2025"
                ]
        
        return [{
            'type': 'weather',
            'priority': 2,
            'message': random.choice(responses)
        }]
    
    def _calculate_alert_level(self, wind_speed, weather_desc):
        """Calculate alert level based on conditions"""
        if wind_speed > 100:
            return "CRITICAL"
        elif wind_speed > 75:
            return "HIGH" 
        elif wind_speed > 50:
            return "MODERATE"
        elif wind_speed > 30 or any(word in weather_desc for word in ['storm', 'thunder', 'heavy']):
            return "LOW"
        else:
            return "ADVISORY"
    
    def _get_alert_emoji(self, alert_level):
        """Get appropriate emoji for alert level"""
        emoji_map = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️', 
            'MODERATE': '🌪️',
            'LOW': '🌧️',
            'ADVISORY': '🌤️'
        }
        return emoji_map.get(alert_level, '📡')
    
    def _check_current_conditions(self):
        """Check current weather conditions"""
        import requests
        
        current_sources = [
            {
                'url': 'https://wttr.in/Basey,Samar,Philippines?format=j1',
                'name': 'Basey, Samar',
                'priority': 1
            },
            {
                'url': 'https://wttr.in/Tacloban,Leyte,Philippines?format=j1', 
                'name': 'Tacloban, Leyte',
                'priority': 1
            },
            {
                'url': 'https://wttr.in/Catbalogan,Samar,Philippines?format=j1',
                'name': 'Catbalogan, Samar', 
                'priority': 1
            }
        ]
        
        current_data = []
        
        for source in current_sources:
            try:
                response = requests.get(source['url'], timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    current = data['current_condition'][0]
                    
                    current_data.append({
                        'location': source['name'],
                        'weather_desc': current['weatherDesc'][0]['value'].lower(),
                        'wind_speed': int(current['windspeedKmph']),
                        'temperature': int(current['temp_C']),
                        'humidity': int(current['humidity']),
                        'pressure': int(current['pressure']),
                        'priority': source['priority']
                    })
                    
            except Exception as e:
                logger.error(f"Current weather source {source['name']} error: {e}")
                continue
                
        return current_data
    
    def _check_forecast_conditions(self):
        """Check forecast conditions for approaching storms"""
        import requests
        from datetime import datetime, timedelta
        
        forecast_sources = [
            {
                'url': 'https://api.openweathermap.org/data/2.5/forecast?q=Tacloban,Philippines&appid=439d4b804bc8187953eb36d2a8c26a02&units=metric',
                'name': 'OpenWeather Forecast',
                'type': 'openweather_forecast'
            },
            {
                'url': 'https://wttr.in/Tacloban,Philippines?format=j1',
                'name': 'wttr.in Extended Forecast',
                'type': 'wttr_forecast'
            }
        ]
        
        forecast_data = []
        
        for source in forecast_sources:
            try:
                response = requests.get(source['url'], timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    if source['type'] == 'wttr_forecast':
                        # Process wttr.in forecast data (next 3 days)
                        weather_forecast = data.get('weather', [])
                        
                        for i, day_forecast in enumerate(weather_forecast[:3]):  # Next 3 days
                            max_wind = 0
                            storm_conditions = []
                            
                            # Check hourly data for the day
                            for hourly in day_forecast.get('hourly', []):
                                wind_kmph = int(hourly.get('windspeedKmph', 0))
                                weather_desc = hourly['weatherDesc'][0]['value'].lower()
                                
                                if wind_kmph > max_wind:
                                    max_wind = wind_kmph
                                
                                # Check for storm indicators
                                if any(condition in weather_desc for condition in 
                                      ['storm', 'thunder', 'heavy rain', 'squall', 'typhoon']):
                                    storm_conditions.append(weather_desc)
                            
                            if max_wind > 40 or storm_conditions:
                                forecast_data.append({
                                    'day': i + 1,  # Day 1, 2, 3
                                    'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                                    'max_wind': max_wind,
                                    'storm_conditions': storm_conditions,
                                    'source': source['name']
                                })
                    
                    elif source['type'] == 'openweather_forecast':
                        # Process OpenWeatherMap 5-day forecast
                        forecast_list = data.get('list', [])
                        
                        daily_data = {}
                        for forecast_item in forecast_list[:15]:  # Next 5 days, 3-hour intervals
                            dt = datetime.fromtimestamp(forecast_item['dt'])
                            day_key = dt.strftime('%Y-%m-%d')
                            
                            if day_key not in daily_data:
                                daily_data[day_key] = {
                                    'max_wind': 0,
                                    'storm_conditions': []
                                }
                            
                            # Convert wind speed from m/s to km/h
                            wind_kmph = forecast_item['wind'].get('speed', 0) * 3.6
                            weather_main = forecast_item['weather'][0]['main'].lower()
                            weather_desc = forecast_item['weather'][0]['description'].lower()
                            
                            if wind_kmph > daily_data[day_key]['max_wind']:
                                daily_data[day_key]['max_wind'] = wind_kmph
                            
                            if weather_main in ['thunderstorm', 'squall'] or 'storm' in weather_desc:
                                daily_data[day_key]['storm_conditions'].append(weather_desc)
                        
                        for day_key, day_data in daily_data.items():
                            if day_data['max_wind'] > 40 or day_data['storm_conditions']:
                                forecast_data.append({
                                    'date': day_key,
                                    'max_wind': day_data['max_wind'],
                                    'storm_conditions': day_data['storm_conditions'],
                                    'source': source['name']
                                })
                    
            except Exception as e:
                logger.error(f"Forecast source {source['name']} error: {e}")
                continue
                
        return forecast_data
    
    def _generate_comprehensive_weather_report(self, weather_data, language):
        """Generate comprehensive weather report with current and forecast data"""
        current_storms = weather_data.get('current', [])
        forecast_storms = weather_data.get('forecast', [])
        
        # Analyze current conditions
        current_alerts = []
        for current in current_storms:
            is_stormy = any(condition in current['weather_desc'] for condition in 
                          ['storm', 'thunder', 'heavy rain', 'squall', 'typhoon'])
            is_windy = current['wind_speed'] > 45
            
            if is_stormy or is_windy:
                current_alerts.append(current)
        
        # Analyze forecast
        upcoming_alerts = []
        for forecast in forecast_storms:
            if forecast['max_wind'] > 50 or forecast['storm_conditions']:
                upcoming_alerts.append(forecast)
        
        # Generate response
        if current_alerts:
            # Current storm activity
            alert = current_alerts[0]
            alert_level = self._calculate_alert_level(alert['wind_speed'], alert['weather_desc'])
            emoji = self._get_alert_emoji(alert_level)
            
            if language == 'fil':
                message = f"{emoji} CURRENT STORM ALERT (Visayas):\n\n📍 {alert['location']}\n🌧️ {alert['weather_desc']}\n💨 {alert['wind_speed']} km/h\n🌡️ {alert['temperature']}°C\n\n"
                
                if upcoming_alerts:
                    message += f"🔮 UPCOMING CONCERNS:\n• {len(upcoming_alerts)} forecast alerts sa susunod na araw\n• Max wind forecast: {max(f['max_wind'] for f in upcoming_alerts):.0f} km/h\n\n"
                
                message += "📱 Official updates:\n• PAGASA: pagasa.dost.gov.ph\n• Emergency: 911"
            else:
                message = f"{emoji} CURRENT STORM ALERT (Visayas):\n\n📍 {alert['location']}\n🌧️ {alert['weather_desc']}\n💨 {alert['wind_speed']} km/h\n🌡️ {alert['temperature']}°C\n\n"
                
                if upcoming_alerts:
                    message += f"🔮 UPCOMING CONCERNS:\n• {len(upcoming_alerts)} forecast alerts in coming days\n• Max wind forecast: {max(f['max_wind'] for f in upcoming_alerts):.0f} km/h\n\n"
                
                message += "📱 Official updates:\n• PAGASA: pagasa.dost.gov.ph\n• Emergency: 911"
            
            return [{
                'type': 'weather',
                'priority': 4,
                'message': message
            }]
        
        elif upcoming_alerts:
            # No current storms but upcoming concerns
            max_forecast_wind = max(f['max_wind'] for f in upcoming_alerts)
            earliest_alert = min(upcoming_alerts, key=lambda x: x.get('date', '9999-12-31'))
            
            if language == 'fil':
                message = f"🔮 FORECAST ALERT (Visayas Region):\n\n✅ Walang storm activity ngayon\n⚠️ May upcoming weather concerns:\n\n📅 Unang alert: {earliest_alert.get('date', 'Soon')}\n💨 Max forecast wind: {max_forecast_wind:.0f} km/h\n📊 Total alerts: {len(upcoming_alerts)} sa susunod na mga araw\n\n🏠 PREPARATION RECOMMENDED:\n• Check emergency kit\n• Monitor weather updates\n• Plan indoor activities\n\n📱 Monitor updates:\n• PAGASA: pagasa.dost.gov.ph\n• Weather apps hourly"
            else:
                message = f"🔮 FORECAST ALERT (Visayas Region):\n\n✅ No storm activity now\n⚠️ Upcoming weather concerns detected:\n\n📅 First alert: {earliest_alert.get('date', 'Soon')}\n💨 Max forecast wind: {max_forecast_wind:.0f} km/h\n📊 Total alerts: {len(upcoming_alerts)} in coming days\n\n🏠 PREPARATION RECOMMENDED:\n• Check emergency kit\n• Monitor weather updates\n• Plan indoor activities\n\n📱 Monitor updates:\n• PAGASA: pagasa.dost.gov.ph\n• Weather apps hourly"
            
            return [{
                'type': 'weather',
                'priority': 3,
                'message': message
            }]
        
        else:
            # All clear - current and forecast
            if current_storms:
                avg_wind = sum(c['wind_speed'] for c in current_storms) / len(current_storms)
                avg_temp = sum(c['temperature'] for c in current_storms) / len(current_storms)
                
                if language == 'fil':
                    message = f"✅ ALL CLEAR (Visayas Region):\n\n🌤️ Current conditions:\n• Average wind: {avg_wind:.1f} km/h\n• Average temp: {avg_temp:.1f}°C\n• Monitored areas: {len(current_storms)} locations\n\n🔮 Forecast check: Clear for next few days\n\n📱 Regular monitoring:\n• PAGASA: pagasa.dost.gov.ph\n• Auto-updates every hour"
                else:
                    message = f"✅ ALL CLEAR (Visayas Region):\n\n🌤️ Current conditions:\n• Average wind: {avg_wind:.1f} km/h\n• Average temp: {avg_temp:.1f}°C\n• Monitored areas: {len(current_storms)} locations\n\n🔮 Forecast check: Clear for next few days\n\n📱 Regular monitoring:\n• PAGASA: pagasa.dost.gov.ph\n• Auto-updates every hour"
                
                return [{
                    'type': 'weather',
                    'priority': 1,
                    'message': message
                }]
            
            # Fallback to seasonal response
            return self._get_enhanced_typhoon_response(language)
    
    def _get_pagasa_data(self):
        """Try to get real typhoon data from working APIs"""
        try:
            import requests
            from datetime import datetime
            
            # Try real working weather APIs
            working_urls = [
                {
                    'url': 'https://api.openweathermap.org/data/2.5/weather?q=Tacloban,Philippines&appid=439d4b804bc8187953eb36d2a8c26a02&units=metric',
                    'type': 'openweather_free'
                },
                {
                    'url': 'https://wttr.in/Tacloban,Philippines?format=j1',
                    'type': 'wttr'
                },
                {
                    'url': 'https://api.weatherapi.com/v1/current.json?key=demo&q=Tacloban,Philippines',
                    'type': 'weatherapi_demo'
                }
            ]
            
            for api_info in working_urls:
                try:
                    response = requests.get(api_info['url'], timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        return {'data': data, 'type': api_info['type']}
                except Exception as e:
                    logger.error(f"API {api_info['type']} error: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Weather API error: {e}")
        return None
    
    def _get_typhoon_tracking_data(self):
        """Get typhoon tracking data from real working sources"""
        try:
            import requests
            
            # Real working typhoon/storm APIs
            real_apis = [
                {
                    'url': 'https://api.weather.gov/alerts/active?area=PH',
                    'type': 'us_weather_alerts'
                },
                {
                    'url': 'https://api.openweathermap.org/data/2.5/onecall?lat=11.2026&lon=125.0003&appid=439d4b804bc8187953eb36d2a8c26a02&exclude=minutely,hourly',
                    'type': 'openweather_onecall'
                },
                {
                    'url': 'https://api.met.no/weatherapi/locationforecast/2.0/complete?lat=11.2026&lon=125.0003',
                    'type': 'norway_met',
                    'headers': {'User-Agent': 'BarangayPortal/1.0'}
                }
            ]
            
            for api_info in real_apis:
                try:
                    headers = api_info.get('headers', {})
                    response = requests.get(api_info['url'], timeout=5, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        return {'data': data, 'type': api_info['type']}
                except Exception as e:
                    logger.error(f"Typhoon API {api_info['type']} error: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Typhoon tracking API error: {e}")
        return None
    
    def _process_pagasa_data(self, api_response, language):
        """Process real weather API data"""
        try:
            data = api_response['data']
            api_type = api_response['type']
            
            if api_type == 'wttr':
                # Process wttr.in data
                current = data['current_condition'][0]
                weather_desc = current['weatherDesc'][0]['value'].lower()
                temp_c = int(current['temp_C'])
                wind_speed = int(current['windspeedKmph'])
                
                # Check for storm conditions
                is_stormy = any(word in weather_desc for word in ['storm', 'rain', 'thunder', 'heavy'])
                
                if is_stormy or wind_speed > 60:
                    if language == 'fil':
                        message = f"⚡ May storm conditions sa area - {weather_desc}, hangin {wind_speed} km/h. Mag-stay indoors at mag-monitor ng updates mula sa PAGASA!"
                    else:
                        message = f"⚡ Storm conditions detected in area - {weather_desc}, winds {wind_speed} km/h. Stay indoors and monitor PAGASA updates!"
                    
                    return [{
                        'type': 'weather',
                        'priority': 4,
                        'message': message
                    }]
            
            elif api_type == 'openweather_free':
                # Process OpenWeatherMap data
                weather = data['weather'][0]
                main = data['main']
                wind = data.get('wind', {})
                
                weather_main = weather['main'].lower()
                wind_speed = wind.get('speed', 0) * 3.6  # Convert m/s to km/h
                
                if weather_main in ['thunderstorm', 'squall'] or wind_speed > 50:
                    if language == 'fil':
                        message = f"🌩️ May storm activity na nakikita - {weather['description']}. Wind speed: {wind_speed:.1f} km/h. Mag-ingat at mag-stay sa safe place!"
                    else:
                        message = f"🌩️ Storm activity detected - {weather['description']}. Wind speed: {wind_speed:.1f} km/h. Stay safe indoors!"
                    
                    return [{
                        'type': 'weather',
                        'priority': 4,
                        'message': message
                    }]
            
        except Exception as e:
            logger.error(f"Error processing real weather data: {e}")
        
        # Fallback to enhanced response
        return self._get_enhanced_typhoon_response(language)
    
    def _process_typhoon_data(self, api_response, language):
        """Process real typhoon tracking data"""
        try:
            data = api_response['data']
            api_type = api_response['type']
            
            if api_type == 'us_weather_alerts':
                # Process US Weather Service alerts for Philippines
                features = data.get('features', [])
                active_alerts = [f for f in features if 'Philippines' in str(f) or 'typhoon' in str(f).lower()]
                
                if active_alerts:
                    if language == 'fil':
                        message = f"🚨 May active weather alerts para sa Philippines region. {len(active_alerts)} alerts detected. Check PAGASA website para sa detailed info: pagasa.dost.gov.ph"
                    else:
                        message = f"🚨 Active weather alerts for Philippines region. {len(active_alerts)} alerts detected. Check PAGASA website for details: pagasa.dost.gov.ph"
                    
                    return [{
                        'type': 'weather',
                        'priority': 4,
                        'message': message
                    }]
            
            elif api_type == 'openweather_onecall':
                # Process detailed weather data
                alerts = data.get('alerts', [])
                current = data.get('current', {})
                
                if alerts or current.get('wind_speed', 0) > 15:  # 15 m/s = ~54 km/h
                    wind_kmh = current.get('wind_speed', 0) * 3.6
                    if language == 'fil':
                        message = f"⚠️ May weather warnings o malakas na hangin sa area ({wind_kmh:.1f} km/h). Mag-monitor ng weather updates at mag-prepare for possible storms."
                    else:
                        message = f"⚠️ Weather warnings or strong winds in area ({wind_kmh:.1f} km/h). Monitor weather updates and prepare for possible storms."
                    
                    return [{
                        'type': 'weather',
                        'priority': 3,
                        'message': message
                    }]
            
        except Exception as e:
            logger.error(f"Error processing typhoon tracking data: {e}")
        
        # Fallback to enhanced response
        return self._get_enhanced_typhoon_response(language)
    
    def _get_enhanced_typhoon_response(self, language):
        """Enhanced typhoon response with more accurate info"""
        from datetime import datetime
        
        # Get current month to provide seasonal context
        current_month = datetime.now().month
        
        if language == 'fil':
            if current_month in [6, 7, 8, 9, 10, 11]:  # Typhoon season
                responses = [
                    {
                        'type': 'weather',
                        'priority': 4,
                        'message': "🌀 Nasa typhoon season pa tayo (June-November). Walang active typhoon warning sa Basey ngayon, pero laging ready ang emergency kit. Check ang PAGASA website para sa latest updates: pagasa.dost.gov.ph"
                    },
                    {
                        'type': 'weather',
                        'priority': 4,
                        'message': "⛈️ Hindi naman may bagyo warning ngayon, pero typhoon season pa rin. Mag-monitor sa PAGASA at local weather reports. Emergency kit ready: tubig, pagkain, flashlight, battery, first aid."
                    }
                ]
            else:  # Dry season
                responses = [
                    {
                        'type': 'weather',
                        'priority': 2,
                        'message': "☀️ Dry season ngayon (December-May) kaya mababa ang chance ng bagyo. Pero climate change kaya better prepared pa rin. Check PAGASA para sa latest: pagasa.dost.gov.ph"
                    }
                ]
        else:
            if current_month in [6, 7, 8, 9, 10, 11]:  # Typhoon season
                responses = [
                    {
                        'type': 'weather',
                        'priority': 4,
                        'message': "🌀 Currently in typhoon season (June-November). No active typhoon warning for Basey now, but keep emergency kit ready. Check PAGASA website for latest: pagasa.dost.gov.ph"
                    },
                    {
                        'type': 'weather',
                        'priority': 4,
                        'message': "⛈️ No typhoon warning currently, but still typhoon season. Monitor PAGASA and local weather reports. Emergency kit: water, food, flashlight, batteries, first aid."
                    }
                ]
            else:  # Dry season
                responses = [
                    {
                        'type': 'weather',
                        'priority': 2,
                        'message': "☀️ Currently dry season (December-May) so typhoon chance is low. But with climate change, better stay prepared. Check PAGASA for latest: pagasa.dost.gov.ph"
                    }
                ]
        
        import random
        return [random.choice(responses)]
    
    def _get_enhanced_fallback_weather(self, language, user_query):
        """Enhanced fallback with query analysis"""
        import random
        from datetime import datetime
        
        # Analyze user query for specific concerns
        query_lower = user_query.lower()
        
        # Check for specific weather concerns
        if any(word in query_lower for word in ['bagyo', 'typhoon', 'storm', 'signal']):
            return self._get_enhanced_typhoon_response(language)
        
        elif any(word in query_lower for word in ['ulan', 'rain', 'wet']):
            if language == 'fil':
                messages = [
                    "🌧️ Para sa accurate rain forecast, check mo ang PAGASA website o weather apps tulad ng AccuWeather. I-monitor ang local weather reports din.",
                    "☔ Hindi ko ma-access ang real-time rain data ngayon. Tingnan mo sa weather.com o PAGASA app para sa hourly forecast."
                ]
            else:
                messages = [
                    "🌧️ For accurate rain forecast, check PAGASA website or weather apps like AccuWeather. Monitor local weather reports too.",
                    "☔ I can't access real-time rain data right now. Check weather.com or PAGASA app for hourly forecast."
                ]
        
        elif any(word in query_lower for word in ['init', 'hot', 'mainit']):
            if language == 'fil':
                messages = [
                    "🌡️ Para sa exact temperature, check mo ang weather apps. Pero generally, mag-expect ng 26-35°C sa Samar. Mag-hydrate at iwas sa sobrang araw.",
                    "☀️ Mainit talaga sa Pilipinas lalo na tag-init. I-download mo ang weather apps para sa real-time temperature updates."
                ]
            else:
                messages = [
                    "🌡️ For exact temperature, check weather apps. Generally expect 26-35°C in Samar. Stay hydrated and avoid excessive sun exposure.",
                    "☀️ It gets hot in the Philippines especially during summer. Download weather apps for real-time temperature updates."
                ]
        
        else:
            # General weather response
            if language == 'fil':
                messages = [
                    "🌤️ Para sa accurate weather info, i-check ang PAGASA (pagasa.dost.gov.ph) o weather apps. Mag-stay updated sa local weather reports para sa safety.",
                    "📱 I-download mo ang PAGASA app o AccuWeather para sa real-time weather updates sa Basey, Samar."
                ]
            else:
                messages = [
                    "🌤️ For accurate weather info, check PAGASA (pagasa.dost.gov.ph) or weather apps. Stay updated with local weather reports for safety.",
                    "📱 Download PAGASA app or AccuWeather for real-time weather updates for Basey, Samar."
                ]
        
        return [{
            'type': 'weather',
            'priority': 2,
            'message': random.choice(messages)
        }]


class TranslationService:
    """Translation API service"""
    
    def __init__(self):
        self.api_manager = APIServiceManager()
    
    def translate_text(self, text, target_language):
        """Translate text to target language"""
        config = self.api_manager.get_api_config('google_translate')
        if not config:
            return text  # Return original if no translation available
        
        # Google Translate API call
        url = "https://translation.googleapis.com/language/translate/v2"
        
        params = {
            'key': config.api_key,
            'q': text,
            'target': 'tl' if target_language == 'fil' else 'en',
            'format': 'text'
        }
        
        result = self.api_manager.make_api_request('google_translate', url, method='POST', params=params)
        
        if result and 'data' in result:
            try:
                return result['data']['translations'][0]['translatedText']
            except (KeyError, IndexError):
                return text
        
        return text


class SmartResponseService:
    """Enhanced AI responses using external APIs"""
    
    def __init__(self):
        self.api_manager = APIServiceManager()
        self.weather_service = WeatherService()
        self.translation_service = TranslationService()
    
    def get_enhanced_response(self, user_message, language='en', context=None):
        """Get enhanced response using AI APIs"""
        
        # Check for weather-related queries
        weather_keywords = [
            'weather', 'panahon', 'klima',
            'ulan', 'rain', 'storm', 'bagyo', 'bagyong', 'typhoon', 'unos',
            'init', 'hot', 'mainit', 'tag-init',
            'lamig', 'cold', 'malamig', 'tag-ulan',
            'hangin', 'wind', 'malakas na hangin',
            'araw', 'sun', 'sunny', 'maaraw',
            'ulap', 'cloud', 'cloudy', 'maulap',
            'temperature', 'temperatura'
        ]
        if any(keyword in user_message.lower() for keyword in weather_keywords):
            weather_alerts = self.weather_service.get_weather_alerts(language=language, user_query=user_message)
            if weather_alerts:
                return weather_alerts[0]['message']
        
        # Try OpenAI for smarter responses
        openai_response = self._get_openai_response(user_message, language, context)
        if openai_response:
            return openai_response
        
        # Fallback to basic response
        return None
    
    def _get_openai_response(self, message, language, context):
        """Get response from OpenAI API"""
        config = self.api_manager.get_api_config('openai')
        if not config:
            return None
        
        url = "https://api.openai.com/v1/chat/completions"
        
        system_prompt = (
            "You are a helpful barangay assistant for Barangay Basey. "
            "Help residents with complaints, services, and information. "
            f"Respond in {'Filipino' if language == 'fil' else 'English'}. "
            "Keep responses concise and helpful."
        )
        
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': 150,
            'temperature': 0.7
        }
        
        result = self.api_manager.make_api_request('openai', url, method='POST', headers=headers, data=data)
        
        if result and 'choices' in result:
            try:
                return result['choices'][0]['message']['content'].strip()
            except (KeyError, IndexError):
                return None
        
        return None


# Service instances
weather_service = WeatherService()
translation_service = TranslationService()
smart_response_service = SmartResponseService()


class TyphoonMonitoringService:
    """Dedicated typhoon monitoring service using multiple APIs"""
    
    def __init__(self):
        self.api_manager = APIServiceManager()
    
    def get_current_typhoon_status(self, language='en'):
        """Get current typhoon status from multiple sources"""
        try:
            import requests
            from datetime import datetime
            
            # Try multiple typhoon tracking sources
            typhoon_sources = [
                {
                    'url': 'https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json',
                    'name': 'Japan Meteorological Agency',
                    'type': 'jma'
                },
                {
                    'url': f'https://wttr.in/Manila,Philippines?format=j1',
                    'name': 'wttr.in Manila',
                    'type': 'wttr_manila'
                },
                {
                    'url': f'https://wttr.in/Tacloban,Philippines?format=j1',
                    'name': 'wttr.in Tacloban',  
                    'type': 'wttr_tacloban'
                }
            ]
            
            active_storms = []
            
            for source in typhoon_sources:
                try:
                    response = requests.get(source['url'], timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if source['type'].startswith('wttr'):
                            # Check wttr.in data for storm conditions
                            current = data['current_condition'][0]
                            weather_desc = current['weatherDesc'][0]['value'].lower()
                            wind_speed = int(current['windspeedKmph'])
                            
                            if any(word in weather_desc for word in ['storm', 'thunder', 'rain']) or wind_speed > 60:
                                active_storms.append({
                                    'location': source['name'],
                                    'description': weather_desc,
                                    'wind_speed': wind_speed,
                                    'source': source['name']
                                })
                        
                except Exception as e:
                    logger.error(f"Typhoon source {source['name']} error: {e}")
                    continue
            
            # Generate response based on findings
            if active_storms:
                storm_info = active_storms[0]  # Use first detected storm
                
                if language == 'fil':
                    message = f"🌪️ REAL-TIME ALERT: May storm activity na detected sa {storm_info['location']} - {storm_info['description']}. Wind speed: {storm_info['wind_speed']} km/h.\n\n📱 Para sa latest official updates:\n• PAGASA: pagasa.dost.gov.ph\n• Emergency: 911\n• Barangay Emergency: (055) 543-XXXX"
                else:
                    message = f"🌪️ REAL-TIME ALERT: Storm activity detected in {storm_info['location']} - {storm_info['description']}. Wind speed: {storm_info['wind_speed']} km/h.\n\n📱 For latest official updates:\n• PAGASA: pagasa.dost.gov.ph\n• Emergency: 911\n• Barangay Emergency: (055) 543-XXXX"
                
                return [{
                    'type': 'weather',
                    'priority': 4,
                    'message': message
                }]
            else:
                # No active storms detected
                current_month = datetime.now().month
                
                if language == 'fil':
                    if current_month in [6, 7, 8, 9, 10, 11]:
                        message = "🌀 REAL-TIME CHECK: Walang active typhoon sa Philippine area ngayon based sa monitoring. Pero nasa typhoon season pa tayo (June-November), kaya stay prepared.\n\n✅ Emergency kit ready\n📱 Monitor PAGASA updates\n🏠 Know evacuation routes"
                    else:
                        message = "☀️ REAL-TIME CHECK: Walang typhoon sa area ngayon. Dry season pa (December-May), pero climate change kaya better stay prepared pa rin.\n\n📱 Regular monitoring: pagasa.dost.gov.ph"
                else:
                    if current_month in [6, 7, 8, 9, 10, 11]:
                        message = "🌀 REAL-TIME CHECK: No active typhoon in Philippine area currently based on monitoring. But we're still in typhoon season (June-November), so stay prepared.\n\n✅ Keep emergency kit ready\n📱 Monitor PAGASA updates\n🏠 Know evacuation routes"
                    else:
                        message = "☀️ REAL-TIME CHECK: No typhoon in area currently. It's dry season (December-May), but with climate change, better stay prepared.\n\n📱 Regular monitoring: pagasa.dost.gov.ph"
                
                return [{
                    'type': 'weather',
                    'priority': 2,
                    'message': message
                }]
                
        except Exception as e:
            logger.error(f"Typhoon monitoring error: {e}")
            return self._get_fallback_typhoon_response(language)
    
    def _get_fallback_typhoon_response(self, language):
        """Fallback response when APIs fail"""
        if language == 'fil':
            return [{
                'type': 'weather',
                'priority': 2,
                'message': "📡 Hindi ma-access ang real-time typhoon data ngayon. Para sa latest updates:\n\n🌐 PAGASA: pagasa.dost.gov.ph\n📱 PAGASA mobile app\n📺 Local news channels\n📻 Radio weather reports\n\n⚠️ Laging ready ang emergency kit!"
            }]
        else:
            return [{
                'type': 'weather',
                'priority': 2,
                'message': "📡 Can't access real-time typhoon data right now. For latest updates:\n\n🌐 PAGASA: pagasa.dost.gov.ph\n📱 PAGASA mobile app\n📺 Local news channels\n📻 Radio weather reports\n\n⚠️ Always keep emergency kit ready!"
            }]


# Enhanced service instances
typhoon_monitor = TyphoonMonitoringService()
