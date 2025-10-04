from django.contrib import admin
from .models import Suggestion, SuggestionVote


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'submitted_by', 'status', 'upvotes', 'submitted_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['submitted_at', 'reviewed_at', 'upvotes']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'location')
        }),
        ('Submission Info', {
            'fields': ('submitted_by', 'submitted_at')
        }),
        ('Status & Review', {
            'fields': ('status', 'admin_response', 'reviewed_by', 'reviewed_at')
        }),
        ('Engagement', {
            'fields': ('upvotes',)
        }),
    )


@admin.register(SuggestionVote)
class SuggestionVoteAdmin(admin.ModelAdmin):
    list_display = ['suggestion', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['suggestion__title', 'user__username']
