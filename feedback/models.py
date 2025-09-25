from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ('usability', 'Portal Usability'),
        ('feature', 'Feature Request'),
        ('bug', 'Bug Report'),
        ('general', 'General Feedback'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, default='general')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate from 1 (poor) to 5 (excellent)"
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_anonymous = models.BooleanField(default=False, help_text="Hide your identity in reports")
    
    # Admin fields
    is_reviewed = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_feedbacks'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feedback_type']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        user_display = "Anonymous" if self.is_anonymous else self.user.username
        return f"{self.title} - {user_display} ({self.rating}★)"
    
    @property
    def star_display(self):
        """Return stars for template display"""
        return '★' * self.rating + '☆' * (5 - self.rating)

class FeedbackAttachment(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='feedback_attachments/%Y/%m/')
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.feedback.title} - {self.file_name}"
    
    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.file.name
        super().save(*args, **kwargs)