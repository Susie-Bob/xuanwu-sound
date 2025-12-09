from django.contrib import admin
from .models import ResourceCategory, Resource, ResourceDownload, ResourceComment


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    list_editable = ['order']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'uploader', 'course', 'year', 'file_size_mb', 
                    'download_count', 'is_approved', 'created_at']
    list_filter = ['category', 'is_approved', 'year', 'created_at']
    search_fields = ['title', 'description', 'course', 'tags']
    list_editable = ['is_approved']
    readonly_fields = ['file_size', 'download_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'file', 'category')
        }),
        ('课程信息', {
            'fields': ('course', 'year', 'semester', 'tags')
        }),
        ('上传信息', {
            'fields': ('uploader', 'file_size', 'download_count', 'is_approved')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResourceDownload)
class ResourceDownloadAdmin(admin.ModelAdmin):
    list_display = ['resource', 'user', 'downloaded_at', 'ip_address']
    list_filter = ['downloaded_at']
    search_fields = ['resource__title', 'user__username']
    readonly_fields = ['downloaded_at']
    ordering = ['-downloaded_at']


@admin.register(ResourceComment)
class ResourceCommentAdmin(admin.ModelAdmin):
    list_display = ['resource', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['resource__title', 'user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
