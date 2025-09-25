from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryCategory, GalleryPhoto, GalleryLike, GalleryComment


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'photo_count', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'category', 'uploaded_by', 'status', 'views', 'likes', 'uploaded_at']
    list_filter = ['status', 'category', 'is_featured', 'is_public', 'uploaded_at']
    search_fields = ['title', 'description', 'location', 'event_name']
    readonly_fields = ['views', 'likes', 'uploaded_at', 'approved_at', 'thumbnail']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'image', 'thumbnail', 'category')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'is_public', 'uploaded_by', 'approved_by', 'approved_at')
        }),
        ('Location & Event', {
            'fields': ('location', 'coordinates', 'date_taken', 'photographer', 'event_name'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('views', 'likes'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_photos', 'reject_photos', 'feature_photos']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'
    
    def approve_photos(self, request, queryset):
        queryset.update(status='approved', approved_by=request.user)
        self.message_user(request, f"{queryset.count()} photos approved successfully.")
    approve_photos.short_description = "Approve selected photos"
    
    def reject_photos(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} photos rejected.")
    reject_photos.short_description = "Reject selected photos"
    
    def feature_photos(self, request, queryset):
        queryset.update(status='featured', is_featured=True)
        self.message_user(request, f"{queryset.count()} photos featured.")
    feature_photos.short_description = "Feature selected photos"


@admin.register(GalleryComment)
class GalleryCommentAdmin(admin.ModelAdmin):
    list_display = ['photo', 'user', 'comment_preview', 'is_official', 'created_at']
    list_filter = ['is_official', 'created_at']
    search_fields = ['comment', 'photo__title', 'user__username']
    
    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.register(GalleryLike)
class GalleryLikeAdmin(admin.ModelAdmin):
    list_display = ['photo', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['photo__title', 'user__username']
