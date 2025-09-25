from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username', 'recipient__email')
    readonly_fields = ('created_at', 'read_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'notification_type', 'priority', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('related_complaint', 'related_feedback'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at', 'read_at')
        }),
    )

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_complaint_updates', 'email_feedback_responses', 'updated_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('email_complaint_updates', 'email_feedback_responses', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': ('email_complaint_updates', 'email_feedback_responses', 'email_system_announcements')
        }),
        ('In-App Notifications', {
            'fields': ('inapp_complaint_updates', 'inapp_feedback_responses', 'inapp_system_announcements')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )