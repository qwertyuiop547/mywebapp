from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class SuggestionCategory(models.Model):
    """Categories for organizing suggestions"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Suggestion Category"
        verbose_name_plural = "Suggestion Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Suggestion(models.Model):
    """Model for barangay improvement suggestions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('implemented', 'Implemented'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Brief title of your suggestion")
    description = models.TextField(help_text="Detailed description of your suggestion")
    category = models.ForeignKey(SuggestionCategory, on_delete=models.CASCADE, related_name='suggestions', null=True, blank=True)
    
    # Submitter Information
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suggestions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Optional contact number")
    
    # Location Information (optional)
    location = models.CharField(max_length=200, blank=True, help_text="Specific location if applicable")
    coordinates = models.CharField(max_length=50, blank=True, help_text="GPS coordinates if applicable")
    
    # Status and Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Review Information
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_suggestions'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes from barangay officials")
    public_response = models.TextField(blank=True, help_text="Public response to the suggestion")
    
    # Implementation Details
    estimated_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    implementation_date = models.DateField(null=True, blank=True)
    
    # Engagement
    likes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    
    # Metadata
    is_anonymous = models.BooleanField(default=False, help_text="Submit suggestion anonymously")
    is_featured = models.BooleanField(default=False, help_text="Feature this suggestion")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Suggestion"
        verbose_name_plural = "Suggestions"
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @property
    def submitter_name(self):
        """Return submitter name or Anonymous"""
        if self.is_anonymous:
            return "Anonymous"
        return self.submitted_by.get_full_name() or self.submitted_by.username
    
    def mark_reviewed(self, reviewer):
        """Mark suggestion as reviewed"""
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])

class SuggestionLike(models.Model):
    """Track user likes for suggestions"""
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='user_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['suggestion', 'user']
    
    def __str__(self):
        return f"{self.user} likes {self.suggestion.title}"

class SuggestionComment(models.Model):
    """Comments on suggestions"""
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    is_official = models.BooleanField(default=False, help_text="Official barangay response")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user} on {self.suggestion.title}"
