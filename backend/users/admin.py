from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model"""
    
    list_display = ['username', 'real_name', 'student_id', 'identity_type', 'is_verified', 'is_staff']
    list_filter = BaseUserAdmin.list_filter + ('identity_type', 'is_verified')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('real_name', 'student_id', 'identity_type', 'is_verified', 'avatar')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('real_name', 'student_id', 'identity_type', 'is_verified', 'avatar')
        }),
    )
