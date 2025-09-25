from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChatSession(models.Model):
    """Chat session model to track conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en', choices=[('en', 'English'), ('fil', 'Filipino')])
    
    class Meta:
        ordering = ['-started_at']
        
    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"Chat Session {self.session_id} - {user_display}"


class ChatMessage(models.Model):
    """Individual chat messages"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_helpful = models.BooleanField(null=True, blank=True)  # User feedback
    
    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}..."


class ChatbotKnowledgeBase(models.Model):
    """Knowledge base for chatbot responses"""
    CATEGORY_CHOICES = [
        ('general', 'General Information'),
        ('complaints', 'Complaints Process'),
        ('services', 'Barangay Services'),
        ('registration', 'User Registration'),
        ('documents', 'Document Requirements'),
        ('contact', 'Contact Information'),
        ('hours', 'Office Hours'),
        ('emergency', 'Emergency Procedures'),
        ('navigation', 'Portal Navigation'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question = models.TextField(help_text="Common question or keywords")
    answer_en = models.TextField(help_text="Answer in English")
    answer_fil = models.TextField(help_text="Answer in Filipino")
    keywords = models.TextField(help_text="Comma-separated keywords for matching")
    priority = models.IntegerField(default=1, help_text="Higher numbers = higher priority")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'category']
        
    def __str__(self):
        return f"{self.get_category_display()}: {self.question[:50]}..."


class ChatbotAnalytics(models.Model):
    """Analytics for chatbot usage"""
    date = models.DateField(default=timezone.now)
    total_sessions = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    avg_session_length = models.FloatField(default=0.0)  # in minutes
    most_common_category = models.CharField(max_length=20, blank=True)
    satisfaction_rating = models.FloatField(default=0.0)  # 0-5 scale
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
        
    def __str__(self):
        return f"Chatbot Analytics - {self.date}"


class ProactiveAlert(models.Model):
    """Proactive alerts/notifications for residents"""
    ALERT_TYPES = [
        ('weather', 'Weather Alert'),
        ('emergency', 'Emergency Alert'),
        ('announcement', 'Barangay Announcement'),
        ('reminder', 'Service Reminder'),
        ('maintenance', 'System Maintenance'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='announcement')
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1, help_text="1=Low, 2=Medium, 3=High, 4=Critical")
    target_language = models.CharField(max_length=10, choices=[('en', 'English'), ('fil', 'Filipino'), ('both', 'Both')], default='both')
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Leave empty for no expiration")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        
    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.title}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class ChatImageUpload(models.Model):
    """Store uploaded images from chat"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='uploaded_images')
    image = models.ImageField(upload_to='chatbot/images/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    ai_analysis = models.TextField(blank=True, help_text="AI analysis of the image")
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"Image upload - {self.original_filename}"


class APIConfiguration(models.Model):
    """Store API keys and configurations"""
    API_PROVIDERS = [
        ('openweather', 'OpenWeatherMap'),
        ('google_translate', 'Google Translate'),
        ('openai', 'OpenAI GPT'),
        ('google_vision', 'Google Vision'),
        ('twilio_sms', 'Twilio SMS'),
        ('azure_speech', 'Azure Speech'),
        ('pagasa', 'PAGASA Weather'),
    ]
    
    provider = models.CharField(max_length=50, choices=API_PROVIDERS, unique=True)
    api_key = models.CharField(max_length=500, help_text="API Key (will be encrypted)")
    api_secret = models.CharField(max_length=500, blank=True, help_text="API Secret (optional)")
    base_url = models.URLField(blank=True, help_text="Custom base URL if needed")
    is_active = models.BooleanField(default=True)
    rate_limit = models.IntegerField(default=1000, help_text="Requests per hour limit")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Usage tracking
    requests_made_today = models.IntegerField(default=0)
    last_request_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['provider']
        
    def __str__(self):
        return f"{self.get_provider_display()} - {'Active' if self.is_active else 'Inactive'}"
    
    def can_make_request(self):
        """Check if we can make another API request"""
        today = timezone.now().date()
        if self.last_request_date != today:
            self.requests_made_today = 0
            self.last_request_date = today
            self.save()
        
        return self.requests_made_today < self.rate_limit
    
    def increment_usage(self):
        """Increment the usage counter"""
        today = timezone.now().date()
        if self.last_request_date != today:
            self.requests_made_today = 1
            self.last_request_date = today
        else:
            self.requests_made_today += 1
        self.save()
