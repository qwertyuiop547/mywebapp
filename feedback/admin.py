from django.contrib import admin
from django.utils.html import format_html
from .models import Feedback, FeedbackAttachment

class FeedbackAttachmentInline(admin.TabularInline):
    model = FeedbackAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_display', 'feedback_type', 'rating_display', 'is_reviewed', 'created_at')
    list_filter = ('feedback_type', 'rating', 'is_reviewed', 'created_at')
    search_fields = ('title', 'comment', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'feedback_type', 'rating', 'title', 'comment', 'is_anonymous')
        }),
        ('Admin Review', {
            'fields': ('is_reviewed', 'admin_response', 'reviewed_by', 'reviewed_at'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [FeedbackAttachmentInline]
    
    def user_display(self, obj):
        return "Anonymous" if obj.is_anonymous else obj.user.username
    user_display.short_description = 'User'
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107;">{}</span>', stars)
    rating_display.short_description = 'Rating'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'reviewed_by')

@admin.register(FeedbackAttachment)
class FeedbackAttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'feedback', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('file_name', 'feedback__title')
    readonly_fields = ('uploaded_at',)