from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class TreeholePost(models.Model):
    """树洞帖子"""
    
    POST_TYPE_CHOICES = [
        ('CONFESSION', '表白'),
        ('COMPLAINT', '吐槽'),
        ('MOOD', '心情'),
        ('OTHER', '其他'),
    ]
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='treehole_posts',
        verbose_name="作者"
    )
    anonymous_name = models.CharField(max_length=50, verbose_name="匿名昵称")
    anonymous_name_expires = models.DateTimeField(verbose_name="昵称过期时间")
    content = models.TextField(verbose_name="内容")
    images = models.JSONField(default=list, blank=True, verbose_name="图片列表")
    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPE_CHOICES,
        default='OTHER',
        verbose_name="帖子类型"
    )
    likes_count = models.IntegerField(default=0, verbose_name="点赞数")
    comments_count = models.IntegerField(default=0, verbose_name="评论数")
    is_hidden = models.BooleanField(default=False, verbose_name="是否被折叠")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "树洞帖子"
        verbose_name_plural = "树洞帖子"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['post_type']),
        ]
    
    def __str__(self):
        return f"{self.anonymous_name} 的树洞帖子"
    
    def save(self, *args, **kwargs):
        # Set anonymous name expiration on creation
        if not self.pk and not self.anonymous_name_expires:
            self.anonymous_name_expires = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)


class TreeholeComment(models.Model):
    """树洞评论"""
    
    post = models.ForeignKey(
        TreeholePost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="帖子"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='treehole_comments',
        verbose_name="作者"
    )
    anonymous_name = models.CharField(max_length=50, verbose_name="匿名昵称")
    anonymous_name_expires = models.DateTimeField(verbose_name="昵称过期时间")
    content = models.TextField(verbose_name="内容")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="父评论"
    )
    likes_count = models.IntegerField(default=0, verbose_name="点赞数")
    is_hidden = models.BooleanField(default=False, verbose_name="是否被折叠")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "树洞评论"
        verbose_name_plural = "树洞评论"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"{self.anonymous_name} 的评论"
    
    def save(self, *args, **kwargs):
        # Set anonymous name expiration on creation
        if not self.pk and not self.anonymous_name_expires:
            self.anonymous_name_expires = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)


class TreeholeLike(models.Model):
    """树洞点赞记录"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='treehole_likes',
        verbose_name="用户"
    )
    post = models.ForeignKey(
        TreeholePost,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes',
        verbose_name="帖子"
    )
    comment = models.ForeignKey(
        TreeholeComment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes',
        verbose_name="评论"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "树洞点赞"
        verbose_name_plural = "树洞点赞"
        unique_together = [['user', 'post'], ['user', 'comment']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['post']),
            models.Index(fields=['comment']),
        ]
    
    def __str__(self):
        if self.post:
            return f"{self.user.username} 点赞了帖子"
        return f"{self.user.username} 点赞了评论"
    
    def save(self, *args, **kwargs):
        # Validate that either post or comment is set (but not both)
        if not self.post and not self.comment:
            raise ValueError("必须点赞帖子或评论")
        if self.post and self.comment:
            raise ValueError("不能同时点赞帖子和评论")
        super().save(*args, **kwargs)
