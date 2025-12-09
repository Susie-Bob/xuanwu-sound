from django.contrib import admin
from .models import Memo


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'content_preview', 'is_completed', 'created_at', 'updated_at']
    list_filter = ['is_completed', 'created_at', 'updated_at']
    search_fields = ['content', 'owner__username']
    list_editable = ['is_completed']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('owner', 'content', 'is_completed')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """显示内容预览"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
