from django.core.management.base import BaseCommand
from chatbot.models import APIConfiguration


class Command(BaseCommand):
    help = 'Setup sample API configurations for chatbot'

    def handle(self, *args, **options):
        # Sample API configurations
        api_configs = [
            {
                'provider': 'openweather',
                'api_key': 'YOUR_OPENWEATHER_API_KEY_HERE',
                'base_url': 'http://api.openweathermap.org/data/2.5/',
                'rate_limit': 1000,
                'is_active': False  # Disabled by default until API key is added
            },
            {
                'provider': 'google_translate',
                'api_key': 'YOUR_GOOGLE_TRANSLATE_API_KEY_HERE',
                'base_url': 'https://translation.googleapis.com/language/translate/v2',
                'rate_limit': 1000000,  # Google has high limits
                'is_active': False
            },
            {
                'provider': 'openai',
                'api_key': 'YOUR_OPENAI_API_KEY_HERE',
                'base_url': 'https://api.openai.com/v1/',
                'rate_limit': 3000,  # Conservative limit
                'is_active': False
            },
            {
                'provider': 'google_vision',
                'api_key': 'YOUR_GOOGLE_VISION_API_KEY_HERE',
                'base_url': 'https://vision.googleapis.com/v1/',
                'rate_limit': 1000,
                'is_active': False
            },
            {
                'provider': 'twilio_sms',
                'api_key': 'YOUR_TWILIO_ACCOUNT_SID_HERE',
                'api_secret': 'YOUR_TWILIO_AUTH_TOKEN_HERE',
                'base_url': 'https://api.twilio.com/2010-04-01/',
                'rate_limit': 1000,
                'is_active': False
            },
            {
                'provider': 'azure_speech',
                'api_key': 'YOUR_AZURE_SPEECH_KEY_HERE',
                'base_url': 'https://YOUR_REGION.api.cognitive.microsoft.com/',
                'rate_limit': 5000,
                'is_active': False
            },
            {
                'provider': 'pagasa',
                'api_key': '',  # PAGASA doesn't require API key for basic weather
                'base_url': 'https://www.pagasa.dost.gov.ph/',
                'rate_limit': 100,  # Conservative for government API
                'is_active': False
            }
        ]

        created_count = 0
        updated_count = 0

        for config_data in api_configs:
            provider = config_data.pop('provider')
            
            config, created = APIConfiguration.objects.get_or_create(
                provider=provider,
                defaults=config_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created API configuration for {provider}')
                )
            else:
                # Update existing configuration if needed
                if not config.api_key or config.api_key.startswith('YOUR_'):
                    for key, value in config_data.items():
                        setattr(config, key, value)
                    config.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated API configuration for {provider}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nAPI Configuration Setup Complete!\n'
                f'Created: {created_count} configurations\n'
                f'Updated: {updated_count} configurations\n\n'
                f'Next steps:\n'
                f'1. Go to Django Admin -> Chatbot -> API Configurations\n'
                f'2. Add your actual API keys\n'
                f'3. Set is_active=True for APIs you want to use\n'
                f'4. Adjust rate limits as needed\n\n'
                f'Popular free APIs to start with:\n'
                f'• OpenWeatherMap: https://openweathermap.org/api (Free tier: 1000 calls/day)\n'
                f'• Google Translate: https://cloud.google.com/translate (Free tier: 500K chars/month)\n'
                f'• OpenAI: https://platform.openai.com/api-keys (Pay per use)\n'
            )
        )
