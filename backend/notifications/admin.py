from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'priority', 'created_at']
    list_filter = ['priority', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'priority')
        }),
        ('发布信息', {
            'fields': ('author', 'created_at')
        }),
    )
