from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, UserVerificationDocument, BarangayArea, ResidencyValidation, UserLoginHistory

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'profile_photo_thumbnail', 'is_approved', 'date_joined')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active', 'date_joined')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address', 'profile_photo', 'profile_photo_preview', 'is_approved', 'date_approved')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'address', 'profile_photo', 'is_approved')
        }),
    )
    
    readonly_fields = ('profile_photo_preview',)
    
    def profile_photo_thumbnail(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />', obj.profile_photo.url)
        return "No Photo"
    profile_photo_thumbnail.short_description = 'Photo'
    
    def profile_photo_preview(self, obj):
        if obj.profile_photo:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 10px; object-fit: cover;" />', obj.profile_photo.url)
        return "No Photo Available"
    profile_photo_preview.short_description = 'Profile Photo Preview'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


@admin.register(UserVerificationDocument)
class UserVerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'user', 'document_type', 'uploaded_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('document_type', 'uploaded_at')


@admin.register(BarangayArea)
class BarangayAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'is_active', 'created_at')
    list_filter = ('zone', 'is_active', 'created_at')
    search_fields = ('name', 'zone')
    ordering = ('zone', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'zone', 'is_active')
        }),
    )


@admin.register(ResidencyValidation)
class ResidencyValidationAdmin(admin.ModelAdmin):
    list_display = ('user', 'location_status', 'address_status', 'auto_validation_score', 'get_overall_status', 'last_validated')
    list_filter = ('location_status', 'address_status', 'last_validated')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('-last_validated',)
    readonly_fields = ('auto_validation_score', 'last_validated')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Validation Status', {
            'fields': ('location_status', 'address_status', 'auto_validation_score')
        }),
        ('Notes & Details', {
            'fields': ('validation_notes', 'last_validated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_overall_status(self, obj):
        status = obj.get_overall_status()
        color_map = {
            'auto_approved': 'green',
            'requires_manual': 'orange', 
            'pending': 'gray'
        }
        color = color_map.get(status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status.replace('_', ' ').title()
        )
    get_overall_status.short_description = 'Overall Status'


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'device_type', 'browser', 'login_time', 'is_active', 'is_suspicious')
    list_filter = ('device_type', 'is_active', 'is_suspicious', 'login_time', 'browser')
    search_fields = ('user__username', 'user__email', 'ip_address', 'browser', 'os')
    ordering = ('-login_time',)
    readonly_fields = ('login_time', 'logout_time', 'session_key', 'user_agent')
    
    fieldsets = (
        ('User & Session', {
            'fields': ('user', 'session_key', 'login_time', 'logout_time', 'is_active')
        }),
        ('Device Information', {
            'fields': ('device_type', 'browser', 'browser_version', 'os', 'os_version'),
            'classes': ('collapse',)
        }),
        ('Network & Security', {
            'fields': ('ip_address', 'location_estimate', 'is_suspicious'),
        }),
        ('Raw Data', {
            'fields': ('user_agent',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
