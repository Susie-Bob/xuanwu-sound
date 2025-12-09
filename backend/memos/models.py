from django.db import models
from django.conf import settings


class Memo(models.Model):
    """个人备忘录/笔记"""
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memos',
        verbose_name="所有者"
    )
    
    class Meta:
        verbose_name = "备忘录"
        verbose_name_plural = "备忘录"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['owner', 'is_completed']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] if len(self.content) > 50 else self.content
        return f"{self.owner.username} - {content_preview}"
