from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
import os


def resource_file_path(instance, filename):
    """Generate upload path for resource files"""
    category = instance.category.name if instance.category else 'other'
    return f'resources/{category}/{instance.id or "temp"}_{filename}'


class ResourceCategory(models.Model):
    """资源分类"""
    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="描述")
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标")
    order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "资源分类"
        verbose_name_plural = "资源分类"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Resource(models.Model):
    """学习资源"""
    title = models.CharField(max_length=200, verbose_name="标题")
    description = models.TextField(blank=True, verbose_name="描述")
    file = models.FileField(
        upload_to=resource_file_path,
        verbose_name="文件",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip', 'rar', 
                                    'txt', 'jpg', 'jpeg', 'png', 'xls', 'xlsx']
            )
        ]
    )
    category = models.ForeignKey(
        ResourceCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='resources',
        verbose_name="分类"
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_resources',
        verbose_name="上传者"
    )
    course = models.CharField(max_length=100, blank=True, verbose_name="相关课程")
    year = models.IntegerField(null=True, blank=True, verbose_name="年份")
    semester = models.CharField(max_length=20, blank=True, verbose_name="学期")
    tags = models.CharField(max_length=200, blank=True, verbose_name="标签", 
                           help_text="多个标签用逗号分隔")
    file_size = models.BigIntegerField(default=0, verbose_name="文件大小(字节)")
    download_count = models.IntegerField(default=0, verbose_name="下载次数")
    is_approved = models.BooleanField(default=True, verbose_name="是否审核通过")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "资源"
        verbose_name_plural = "资源"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['uploader']),
            models.Index(fields=['course']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    @property
    def file_extension(self):
        """获取文件扩展名"""
        if self.file:
            return os.path.splitext(self.file.name)[1][1:].lower()
        return ''
    
    @property
    def file_size_mb(self):
        """文件大小（MB）"""
        return round(self.file_size / (1024 * 1024), 2) if self.file_size else 0
    
    @property
    def average_rating(self):
        """平均评分"""
        comments = self.comments.filter(rating__isnull=False)
        if comments.exists():
            from django.db.models import Avg
            result = comments.aggregate(avg=Avg('rating'))
            return round(result['avg'], 1) if result['avg'] else 0
        return 0
    
    @property
    def comment_count(self):
        """评论数量"""
        return self.comments.count()


class ResourceDownload(models.Model):
    """资源下载记录"""
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='downloads',
        verbose_name="资源"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resource_downloads',
        verbose_name="下载者"
    )
    downloaded_at = models.DateTimeField(auto_now_add=True, verbose_name="下载时间")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    
    class Meta:
        verbose_name = "下载记录"
        verbose_name_plural = "下载记录"
        ordering = ['-downloaded_at']
        indexes = [
            models.Index(fields=['resource', '-downloaded_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 下载了 {self.resource.title}"


class ResourceComment(models.Model):
    """资源评论"""
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="资源"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resource_comments',
        verbose_name="评论者"
    )
    content = models.TextField(verbose_name="评论内容")
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="评分"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "资源评论"
        verbose_name_plural = "资源评论"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resource', '-created_at']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 评论了 {self.resource.title}"
