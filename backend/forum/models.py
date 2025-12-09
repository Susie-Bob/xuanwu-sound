from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Category(models.Model):
    """论坛分类"""
    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="分类描述")
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标")
    order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    """帖子"""
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="作者"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name="分类"
    )
    images = models.JSONField(default=list, blank=True, verbose_name="图片列表")
    is_pinned = models.BooleanField(default=False, verbose_name="是否置顶")
    is_locked = models.BooleanField(default=False, verbose_name="是否锁定")
    view_count = models.IntegerField(default=0, verbose_name="浏览次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "帖子"
        verbose_name_plural = "帖子"
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def comment_count(self):
        return self.comments.count()
    
    @property
    def like_count(self):
        return self.likes.count()


class Comment(models.Model):
    """评论"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="帖子"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="作者"
    )
    content = models.TextField(verbose_name="内容")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="父评论"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"{self.author.username} 的评论"
    
    @property
    def like_count(self):
        return self.likes.count()


class Like(models.Model):
    """点赞（支持帖子和评论）"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="用户"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "点赞"
        verbose_name_plural = "点赞"
        unique_together = [['user', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 点赞了 {self.content_object}"


# Add reverse relation to Post and Comment for likes
from django.contrib.contenttypes.fields import GenericRelation

Post.add_to_class('likes', GenericRelation(Like, related_query_name='post'))
Comment.add_to_class('likes', GenericRelation(Like, related_query_name='comment'))
