from django.contrib import admin
from .models import TreeholePost, TreeholeComment, TreeholeLike


@admin.register(TreeholePost)
class TreeholePostAdmin(admin.ModelAdmin):
    list_display = ['id', 'anonymous_name', 'author', 'post_type', 'likes_count', 
                    'comments_count', 'is_hidden', 'created_at']
    list_filter = ['post_type', 'is_hidden', 'created_at']
    search_fields = ['content', 'author__username', 'author__real_name', 'anonymous_name']
    list_editable = ['is_hidden']
    readonly_fields = ['anonymous_name', 'anonymous_name_expires', 'likes_count', 
                       'comments_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('content', 'images', 'post_type')
        }),
        ('匿名信息', {
            'fields': ('anonymous_name', 'anonymous_name_expires')
        }),
        ('作者信息（仅管理员可见）', {
            'fields': ('author',),
            'classes': ('collapse',)
        }),
        ('设置', {
            'fields': ('is_hidden',)
        }),
        ('统计信息', {
            'fields': ('likes_count', 'comments_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TreeholeComment)
class TreeholeCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'anonymous_name', 'author', 'post', 'parent', 
                    'likes_count', 'is_hidden', 'created_at']
    list_filter = ['is_hidden', 'created_at']
    search_fields = ['content', 'author__username', 'author__real_name', 
                     'anonymous_name', 'post__content']
    list_editable = ['is_hidden']
    readonly_fields = ['anonymous_name', 'anonymous_name_expires', 'likes_count', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('post', 'content', 'parent')
        }),
        ('匿名信息', {
            'fields': ('anonymous_name', 'anonymous_name_expires')
        }),
        ('作者信息（仅管理员可见）', {
            'fields': ('author',),
            'classes': ('collapse',)
        }),
        ('设置', {
            'fields': ('is_hidden',)
        }),
        ('统计信息', {
            'fields': ('likes_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TreeholeLike)
class TreeholeLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__real_name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('点赞信息', {
            'fields': ('user', 'post', 'comment')
        }),
        ('统计信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
