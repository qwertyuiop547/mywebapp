from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatbotKnowledgeBase, ChatbotAnalytics, ProactiveAlert, ChatImageUpload, APIConfiguration


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'language', 'started_at', 'is_active']
    list_filter = ['is_active', 'language', 'started_at']
    search_fields = ['session_id', 'user__username', 'user__email']
    readonly_fields = ['session_id', 'started_at', 'ended_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp', 'is_helpful']
    list_filter = ['message_type', 'timestamp', 'is_helpful']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Content Preview"


@admin.register(ChatbotKnowledgeBase)
class ChatbotKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'category', 'priority', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'priority']
    search_fields = ['question', 'answer_en', 'answer_fil', 'keywords']
    list_editable = ['priority', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'question', 'keywords', 'priority', 'is_active')
        }),
        ('Answers', {
            'fields': ('answer_en', 'answer_fil')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def question_preview(self, obj):
        return obj.question[:75] + "..." if len(obj.question) > 75 else obj.question
    question_preview.short_description = "Question"


@admin.register(ChatbotAnalytics)
class ChatbotAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_sessions', 'total_messages', 'avg_session_length', 'satisfaction_rating']
    list_filter = ['date', 'most_common_category']
    readonly_fields = ['date']
    
    def has_add_permission(self, request):
        return False  # Analytics are generated automatically


@admin.register(ProactiveAlert)
class ProactiveAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'priority', 'is_active', 'target_language', 'expires_at', 'created_at']
    list_filter = ['alert_type', 'priority', 'is_active', 'target_language', 'created_at']
    search_fields = ['title', 'message']
    list_editable = ['is_active', 'priority']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('title', 'message', 'alert_type', 'priority')
        }),
        ('Targeting', {
            'fields': ('target_language', 'expires_at', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ChatImageUpload)
class ChatImageUploadAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'session', 'uploaded_at', 'has_analysis']
    list_filter = ['uploaded_at']
    search_fields = ['original_filename', 'ai_analysis']
    readonly_fields = ['uploaded_at', 'original_filename']
    
    def has_analysis(self, obj):
        return bool(obj.ai_analysis)
    has_analysis.boolean = True
    has_analysis.short_description = "Has AI Analysis"


@admin.register(APIConfiguration)
class APIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['provider', 'is_active', 'rate_limit', 'requests_made_today', 'usage_percentage', 'updated_at']
    list_filter = ['provider', 'is_active', 'last_request_date']
    search_fields = ['provider']
    list_editable = ['is_active', 'rate_limit']
    
    fieldsets = (
        ('API Provider', {
            'fields': ('provider', 'is_active')
        }),
        ('Authentication', {
            'fields': ('api_key', 'api_secret', 'base_url'),
            'classes': ('collapse',)
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit', 'requests_made_today', 'last_request_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['requests_made_today', 'last_request_date', 'created_at', 'updated_at']
    
    def usage_percentage(self, obj):
        if obj.rate_limit > 0:
            percentage = (obj.requests_made_today / obj.rate_limit) * 100
            if percentage > 80:
                return f"🔴 {percentage:.1f}%"
            elif percentage > 50:
                return f"🟡 {percentage:.1f}%"
            else:
                return f"🟢 {percentage:.1f}%"
        return "N/A"
    usage_percentage.short_description = "Usage Today"
