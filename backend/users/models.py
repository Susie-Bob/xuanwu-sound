from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model with real-name authentication fields"""
    
    IDENTITY_CHOICES = [
        ('UNDERGRAD', '本科生'),
        ('POSTGRAD', '研究生'),
        ('TEACHER', '教职工'),
        ('ALUMNI', '校友'),
    ]
    
    real_name = models.CharField(max_length=50, blank=True, verbose_name="真实姓名")
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="学号/工号")
    identity_type = models.CharField(max_length=20, choices=IDENTITY_CHOICES, blank=True, verbose_name="身份类型")
    is_verified = models.BooleanField(default=False, verbose_name="是否实名认证")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="头像")
    
    def __str__(self):
        return f"{self.username} ({self.real_name})"
