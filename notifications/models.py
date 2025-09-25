from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('complaint_created', 'Complaint Created'),
        ('complaint_updated', 'Complaint Updated'),
        ('complaint_resolved', 'Complaint Resolved'),
        ('complaint_rejected', 'Complaint Rejected'),
        ('feedback_received', 'Feedback Received'),
        ('user_approved', 'User Approved'),
        ('system_announcement', 'System Announcement'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Optional links
    related_complaint = models.ForeignKey(
        'complaints.Complaint', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    related_feedback = models.ForeignKey(
        'feedback.Feedback', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    related_announcement = models.ForeignKey(
        'announcements.Announcement', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @property
    def get_link(self):
        """Get the appropriate link for the notification"""
        # For complaint rejections, direct to the in-app notification detail view
        if self.notification_type == 'complaint_rejected':
            return f"/notifications/view/{self.id}/"
        if self.related_complaint:
            return f"/complaints/{self.related_complaint.id}/"
        elif self.related_feedback:
            return f"/feedback/{self.related_feedback.id}/"
        elif self.related_announcement:
            return f"/announcements/{self.related_announcement.id}/"
        return "/dashboard/"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_complaint_updates = models.BooleanField(default=True, help_text="Receive emails for complaint status changes")
    email_feedback_responses = models.BooleanField(default=True, help_text="Receive emails for feedback responses")
    email_system_announcements = models.BooleanField(default=True, help_text="Receive system announcements")
    
    # In-app notifications
    inapp_complaint_updates = models.BooleanField(default=True)
    inapp_feedback_responses = models.BooleanField(default=True)
    inapp_system_announcements = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Preferences - {self.user.username}"