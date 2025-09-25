from django.contrib import admin
from .models import Announcement, AnnouncementNotification

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'created_by', 'created_at', 'is_published', 'is_pinned']
    list_filter = ['category', 'priority', 'is_published', 'is_pinned', 'created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'category', 'priority')
        }),
        ('Publishing', {
            'fields': ('publish_date', 'expiry_date', 'is_published', 'is_pinned')
        }),
        ('Metadata', {
            'fields': ('created_by', 'views'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(AnnouncementNotification)
class AnnouncementNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'announcement', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'read_at']
