from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    name_filipino = models.CharField(max_length=100, help_text="Filipino translation")
    description = models.TextField(blank=True)
    description_filipino = models.TextField(blank=True, help_text="Filipino translation")
    icon = models.CharField(max_length=50, default='fas fa-file', help_text="FontAwesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Service(models.Model):
    PROCESSING_TIME_CHOICES = [
        ('same_day', 'Same Day / Araw din'),
        ('1_day', '1 Business Day / 1 Araw ng Trabaho'),
        ('3_days', '3 Business Days / 3 Araw ng Trabaho'),
        ('1_week', '1 Week / 1 Linggo'),
        ('2_weeks', '2 Weeks / 2 Linggo'),
    ]
    
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    name_filipino = models.CharField(max_length=100, help_text="Filipino translation")
    description = models.TextField()
    description_filipino = models.TextField(help_text="Filipino translation")
    requirements = models.TextField(help_text="Requirements in English")
    requirements_filipino = models.TextField(help_text="Requirements in Filipino")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Service fee in PHP")
    processing_time = models.CharField(max_length=20, choices=PROCESSING_TIME_CHOICES, default='3_days')
    is_active = models.BooleanField(default=True)
    is_online_available = models.BooleanField(default=False, help_text="Can be requested online")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={'pk': self.pk})

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review / Naghihintay ng Review'),
        ('processing', 'Processing / Pinoproseso'),
        ('ready', 'Ready for Pickup / Handa nang Kunin'),
        ('completed', 'Completed / Tapos na'),
        ('rejected', 'Rejected / Hindi Tinanggap'),
    ]
    
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent / Urgent'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Personal Information
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField()
    
    # Request Details
    purpose = models.TextField(help_text="Purpose of the service request")
    purpose_filipino = models.TextField(blank=True, help_text="Purpose in Filipino (optional)")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Processing Information
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_service_requests')
    admin_notes = models.TextField(blank=True, help_text="Internal notes for staff")
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection")
    
    # Dates
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.reference_number} - {self.service.name} - {self.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate reference number like BRG-2025-0001
            import datetime
            year = datetime.datetime.now().year
            last_request = ServiceRequest.objects.filter(
                reference_number__startswith=f'BRG-{year}-'
            ).order_by('-id').first()
            
            if last_request:
                last_number = int(last_request.reference_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.reference_number = f'BRG-{year}-{new_number:04d}'
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('services:request_detail', kwargs={'pk': self.pk})

class ServiceAttachment(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='service_attachments/%Y/%m/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.service_request.reference_number} - {self.filename}"
