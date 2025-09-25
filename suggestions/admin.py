from django.contrib import admin
from django.utils.html import format_html
from .models import SuggestionCategory, Suggestion, SuggestionLike, SuggestionComment

@admin.register(SuggestionCategory)
class SuggestionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'suggestion_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    
    def suggestion_count(self, obj):
        return obj.suggestions.count()
    suggestion_count.short_description = 'Total Suggestions'

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'submitter_name_admin', 'category', 'status', 
        'priority', 'is_featured', 'likes', 'views', 'submitted_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'is_featured', 
        'is_anonymous', 'submitted_at', 'reviewed_at'
    ]
    search_fields = ['title', 'description', 'submitted_by__username', 'submitted_by__email']
    list_editable = ['status', 'priority', 'is_featured']
    readonly_fields = ['submitted_at', 'updated_at', 'likes', 'views']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Submitter Information', {
            'fields': ('submitted_by', 'submitted_at', 'contact_phone', 'is_anonymous')
        }),
        ('Location', {
            'fields': ('location', 'coordinates'),
            'classes': ('collapse',)
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'is_featured')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'reviewed_at', 'admin_notes', 'public_response'),
            'classes': ('collapse',)
        }),
        ('Implementation', {
            'fields': ('estimated_budget', 'implementation_date'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('likes', 'views', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def submitter_name_admin(self, obj):
        if obj.is_anonymous:
            return format_html('<span style="color: #666;">Anonymous</span>')
        return obj.submitted_by.get_full_name() or obj.submitted_by.username
    submitter_name_admin.short_description = 'Submitted By'
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status in ['under_review', 'approved', 'rejected']:
            # Auto-set reviewer when status changes
            if not obj.reviewed_by:
                obj.mark_reviewed(request.user)
        super().save_model(request, obj, form, change)

@admin.register(SuggestionComment)
class SuggestionCommentAdmin(admin.ModelAdmin):
    list_display = ['suggestion_title', 'user', 'is_official', 'created_at']
    list_filter = ['is_official', 'created_at']
    search_fields = ['suggestion__title', 'user__username', 'comment']
    list_editable = ['is_official']
    
    def suggestion_title(self, obj):
        return obj.suggestion.title
    suggestion_title.short_description = 'Suggestion'

@admin.register(SuggestionLike)
class SuggestionLikeAdmin(admin.ModelAdmin):
    list_display = ['suggestion_title', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['suggestion__title', 'user__username']
    
    def suggestion_title(self, obj):
        return obj.suggestion.title
    suggestion_title.short_description = 'Suggestion'
