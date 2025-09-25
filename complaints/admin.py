from django.contrib import admin
from django.utils.html import format_html
from .models import ComplaintCategory, Complaint, ComplaintAttachment, ComplaintComment, CategoryAssignmentRule

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'complaint_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def complaint_count(self, obj):
        return obj.complaint_set.count()
    complaint_count.short_description = 'Complaints'

@admin.register(CategoryAssignmentRule)
class CategoryAssignmentRuleAdmin(admin.ModelAdmin):
    list_display = ('category', 'default_assignee_role', 'backup_assignee_role', 'is_sensitive', 'requires_referral')
    list_filter = ('default_assignee_role', 'is_sensitive', 'requires_referral')
    search_fields = ('category__name', 'escalation_notes')
    ordering = ('category__name',)

class ComplaintAttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0
    readonly_fields = ('file_type', 'uploaded_at')

class ComplaintCommentInline(admin.TabularInline):
    model = ComplaintComment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('author', 'comment', 'is_internal', 'created_at')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_complainant_info', 'category', 'status', 'priority', 'is_approved', 'is_anonymous', 'created_at')
    list_filter = ('status', 'priority', 'category', 'is_approved', 'is_anonymous', 'created_at')
    search_fields = ('title', 'description', 'complainant__username', 'complainant__first_name', 'complainant__last_name', 'anonymous_contact')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_complainant_info(self, obj):
        if obj.is_anonymous:
            contact = obj.anonymous_contact or 'No contact'
            return f"Anonymous ({contact})"
        elif obj.complainant:
            return obj.complainant.get_full_name() or obj.complainant.username
        else:
            return "Unknown"
    get_complainant_info.short_description = 'Complainant'
    fieldsets = (
        ('Basic Information', {
            'fields': ('complainant', 'is_anonymous', 'anonymous_contact', 'category', 'title', 'description')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Status & Assignment', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ComplaintAttachmentInline, ComplaintCommentInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('complainant', 'category', 'assigned_to')

@admin.register(ComplaintAttachment)
class ComplaintAttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'complaint', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('file_name', 'complaint__title')
    readonly_fields = ('file_type', 'uploaded_at')

@admin.register(ComplaintComment)
class ComplaintCommentAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'author', 'comment_preview', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at', 'author')
    search_fields = ('comment', 'complaint__title', 'author__username')
    readonly_fields = ('created_at',)
    
    def comment_preview(self, obj):
        return obj.comment[:50] + ('...' if len(obj.comment) > 50 else '')
    comment_preview.short_description = 'Comment'