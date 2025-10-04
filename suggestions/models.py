from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Suggestion(models.Model):
    """
    Simple model for barangay improvement suggestions
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200, help_text="Pamagat ng iyong mungkahi")
    description = models.TextField(help_text="Detalyadong paglalarawan")
    location = models.CharField(max_length=200, blank=True, help_text="Lugar kung saan ito applicable")
    
    # User info
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_suggestions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True, help_text="Tugon ng barangay")
    
    # Review info
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_suggestions'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    upvotes = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Suggestion"
        verbose_name_plural = "Suggestions"
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def mark_as_reviewed(self, reviewer):
        """Mark this suggestion as reviewed"""
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()


class SuggestionVote(models.Model):
    """
    Track which users voted for which suggestions
    """
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['suggestion', 'user']
        verbose_name = "Suggestion Vote"
        verbose_name_plural = "Suggestion Votes"
    
    def __str__(self):
        return f"{self.user.username} voted for {self.suggestion.title}"
