from django.db import models
from django.conf import settings


class Notification(models.Model):
    """学校公告"""
    
    PRIORITY_CHOICES = [
        ('high', '高'),
        ('normal', '普通'),
        ('low', '低'),
    ]
    
    title = models.CharField(max_length=255, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name="优先级"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="发布者"
    )
    
    class Meta:
        verbose_name = "公告"
        verbose_name_plural = "公告"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
