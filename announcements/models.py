from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Announcement(models.Model):
    """Model for barangay announcements"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General Announcement'),
        ('meeting', 'Barangay Meeting'),
        ('event', 'Community Event'),
        ('alert', 'Important Alert'),
        ('service', 'Service Update'),
        ('health', 'Health Advisory'),
        ('safety', 'Safety Notice'),
        ('maintenance', 'Maintenance Notice'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Announcement title")
    content = models.TextField(help_text="Detailed announcement content", blank=True)
    image = models.ImageField(upload_to='announcements/', help_text="Announcement image", blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Publishing Information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval Workflow
    approval_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Approval'),
        ('approved', 'Approved by Chairman'),
        ('rejected', 'Rejected by Chairman'),
    ], default='pending', help_text="Chairman approval status")
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_announcements',
        help_text="Chairman who approved this announcement"
    )
    approved_at = models.DateTimeField(null=True, blank=True, help_text="When this was approved")
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection")

    # Scheduling and Display
    publish_date = models.DateTimeField(default=timezone.now, help_text="When to publish this announcement")
    expiry_date = models.DateTimeField(null=True, blank=True, help_text="Optional expiry date")
    is_published = models.BooleanField(default=True, help_text="Make announcement visible to public")
    is_pinned = models.BooleanField(default=False, help_text="Pin announcement to top")
    
    # Engagement
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
    
    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"
    
    @property
    def is_active(self):
        """Check if announcement is currently active and approved"""
        now = timezone.now()
        if not self.is_published:
            return False
        if self.approval_status != 'approved':
            return False
        if self.publish_date > now:
            return False
        if self.expiry_date and self.expiry_date < now:
            return False
        return True
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def approve(self, chairman):
        """Approve announcement by chairman"""
        self.approval_status = 'approved'
        self.approved_by = chairman
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, chairman, reason=""):
        """Reject announcement by chairman"""
        self.approval_status = 'rejected'
        self.approved_by = chairman
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    @property
    def is_pending_approval(self):
        """Check if announcement is pending approval"""
        return self.approval_status == 'pending'
    
    @property
    def is_approved(self):
        """Check if announcement is approved"""
        return self.approval_status == 'approved'
    
    @property
    def is_rejected(self):
        """Check if announcement is rejected"""
        return self.approval_status == 'rejected'

class AnnouncementNotification(models.Model):
    """Notifications for announcements"""
    
    NOTIFICATION_TYPES = [
        ('created', 'Announcement Created'),
        ('updated', 'Announcement Updated'),
        ('published', 'Announcement Published'),
        ('expired', 'Announcement Expired'),
    ]
    
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='announcement_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcement_notifications')
    
    # Notification Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Announcement Notification"
        verbose_name_plural = "Announcement Notifications"
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
