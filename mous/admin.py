from django.contrib import admin
from django.utils.html import format_html
from .models import MOU, ActivityLog, ShareLink, PartnerSubmission


@admin.register(MOU)
class MOUAdmin(admin.ModelAdmin):
    list_display = ['title', 'partner_name', 'status', 'expiry_date', 'created_at', 'expires_soon_indicator']
    list_filter = ['status', 'created_at', 'expiry_date']
    search_fields = ['title', 'partner_name', 'partner_organization']
    readonly_fields = ['created_at', 'updated_at', 'clauses']
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'pdf_file')
        }),
        ('Partner Information', {
            'fields': ('partner_name', 'partner_organization', 'partner_contact')
        }),
        ('MOU Details', {
            'fields': ('status', 'expiry_date', 'clauses')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def expires_soon_indicator(self, obj):
        if obj.expires_soon:
            return format_html('<span style="color: red;">⚠️ Expires Soon</span>')
        return format_html('<span style="color: green;">✓ Valid</span>')
    expires_soon_indicator.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['mou', 'action', 'user_display', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['mou__title', 'user__username', 'user_name']
    readonly_fields = ['timestamp']

    def user_display(self, obj):
        if obj.user:
            return obj.user.username
        return obj.user_name or 'Anonymous'
    user_display.short_description = 'User'


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ['mou', 'token', 'expires_at', 'is_active', 'access_count', 'created_at']
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['mou__title', 'token']
    readonly_fields = ['token', 'created_at', 'access_count']


@admin.register(PartnerSubmission)
class PartnerSubmissionAdmin(admin.ModelAdmin):
    list_display = ['partner_name', 'partner_organization', 'share_link', 'submitted_at']
    list_filter = ['submitted_at']
    search_fields = ['partner_name', 'partner_organization', 'partner_email']
    readonly_fields = ['submitted_at', 'ip_address']
