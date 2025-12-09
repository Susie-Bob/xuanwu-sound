from django.contrib import admin
from .models import Tag, Teacher, Canteen, Rating, HelpfulMark


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'color', 'order']
    list_filter = ['category']
    list_editable = ['color', 'order']
    search_fields = ['name']
    ordering = ['category', 'order', 'name']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'title', 'created_at']
    list_filter = ['department', 'title']
    search_fields = ['name', 'department', 'courses']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['department', 'name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'department', 'title')
        }),
        ('详细信息', {
            'fields': ('courses', 'bio', 'email', 'office', 'image')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Canteen)
class CanteenAdmin(admin.ModelAdmin):
    list_display = ['name', 'canteen_building', 'location', 'price_range', 'created_at']
    list_filter = ['canteen_building']
    search_fields = ['name', 'specialties']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['canteen_building', 'name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'canteen_building', 'location')
        }),
        ('详细信息', {
            'fields': ('description', 'specialties', 'price_range', 'opening_hours', 'image')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_object', 'score', 'is_anonymous', 'helpful_count', 'created_at']
    list_filter = ['score', 'is_anonymous', 'created_at']
    search_fields = ['user__username', 'comment']
    readonly_fields = ['helpful_count', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    ordering = ['-created_at']


@admin.register(HelpfulMark)
class HelpfulMarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
