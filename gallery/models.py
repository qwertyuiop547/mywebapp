from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from PIL import Image
import os

User = get_user_model()


class GalleryCategory(models.Model):
    """Categories for organizing gallery photos"""
    CATEGORY_CHOICES = [
        ('events', 'Community Events'),
        ('infrastructure', 'Infrastructure & Development'),
        ('services', 'Barangay Services'),
        ('activities', 'Community Activities'),
        ('officials', 'Barangay Officials'),
        ('cultural', 'Cultural Heritage'),
        ('sports', 'Sports & Recreation'),
        ('health', 'Health Programs'),
        ('education', 'Education Programs'),
        ('environment', 'Environmental Initiatives'),
        ('safety', 'Public Safety'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    icon = models.CharField(max_length=50, default='fas fa-images', help_text='FontAwesome icon class')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Gallery Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('gallery:category_photos', kwargs={'category_slug': self.slug})


class GalleryPhoto(models.Model):
    """Individual photos in the gallery"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('featured', 'Featured'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/photos/%Y/%m/')
    thumbnail = models.ImageField(upload_to='gallery/thumbnails/%Y/%m/', blank=True)
    
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='photos')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gallery_photos')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Location information
    location = models.CharField(max_length=255, blank=True)
    coordinates = models.CharField(max_length=50, blank=True, help_text='lat,lng format')
    
    # Metadata
    date_taken = models.DateField(blank=True, null=True)
    photographer = models.CharField(max_length=100, blank=True)
    event_name = models.CharField(max_length=200, blank=True)
    
    # Engagement
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    
    # Timestamps
    uploaded_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_photos'
    )
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('gallery:photo_detail', kwargs={'photo_id': self.id})
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Create thumbnail if doesn't exist
        if self.image and not self.thumbnail:
            self.create_thumbnail()
    
    def create_thumbnail(self):
        """Create a thumbnail version of the image"""
        if not self.image:
            return
            
        image = Image.open(self.image.path)
        image.thumbnail((300, 300), Image.LANCZOS)
        
        # Save thumbnail
        thumb_name = f"thumb_{os.path.basename(self.image.name)}"
        thumb_path = os.path.join(
            os.path.dirname(self.image.path).replace('photos', 'thumbnails'),
            thumb_name
        )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        
        image.save(thumb_path)
        self.thumbnail = thumb_path.replace(str(settings.MEDIA_ROOT), '').lstrip('/')
        super().save(update_fields=['thumbnail'])
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_status_display_class(self):
        """Get CSS class for status badge"""
        status_classes = {
            'pending': 'bg-warning',
            'approved': 'bg-success',
            'rejected': 'bg-danger',
            'featured': 'bg-primary',
        }
        return status_classes.get(self.status, 'bg-secondary')


class GalleryLike(models.Model):
    """Track user likes on photos"""
    photo = models.ForeignKey(GalleryPhoto, on_delete=models.CASCADE, related_name='photo_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('photo', 'user')
    
    def __str__(self):
        return f"{self.user.username} likes {self.photo.title}"


class GalleryComment(models.Model):
    """Comments on gallery photos"""
    photo = models.ForeignKey(GalleryPhoto, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    is_official = models.BooleanField(default=False)  # For official barangay responses
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.photo.title}"
