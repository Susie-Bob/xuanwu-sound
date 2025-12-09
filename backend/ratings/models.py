from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator


class Tag(models.Model):
    """评价标签"""
    CATEGORY_CHOICES = [
        ('TEACHER', '教师'),
        ('CANTEEN', '食堂'),
    ]
    
    name = models.CharField(max_length=20, verbose_name="标签名称")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, verbose_name="分类")
    color = models.CharField(max_length=20, default='blue', verbose_name="颜色")
    order = models.IntegerField(default=0, verbose_name="排序")
    
    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"
        unique_together = [['name', 'category']]
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"


class Teacher(models.Model):
    """教师"""
    name = models.CharField(max_length=50, verbose_name="姓名")
    department = models.CharField(max_length=100, verbose_name="所属学院/部门")
    title = models.CharField(max_length=50, blank=True, verbose_name="职称")
    courses = models.TextField(blank=True, verbose_name="主讲课程")
    bio = models.TextField(blank=True, verbose_name="个人简介")
    image = models.ImageField(upload_to='teachers/', null=True, blank=True, verbose_name="照片")
    email = models.EmailField(blank=True, verbose_name="邮箱")
    office = models.CharField(max_length=100, blank=True, verbose_name="办公室")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    ratings = GenericRelation('Rating', related_query_name='teacher')
    
    class Meta:
        verbose_name = "教师"
        verbose_name_plural = "教师"
        ordering = ['department', 'name']
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.department}"
    
    @property
    def average_rating(self):
        """平均评分"""
        result = self.ratings.aggregate(avg=Avg('score'))
        if result['avg']:
            return round(result['avg'], 1)
        return 0
    
    @property
    def rating_count(self):
        """评价数量"""
        return self.ratings.count()


class Canteen(models.Model):
    """食堂窗口"""
    name = models.CharField(max_length=100, verbose_name="名称")
    canteen_building = models.CharField(max_length=50, verbose_name="所属食堂")
    location = models.CharField(max_length=100, verbose_name="位置/楼层")
    description = models.TextField(blank=True, verbose_name="描述")
    specialties = models.TextField(blank=True, verbose_name="特色菜品")
    image = models.ImageField(upload_to='canteen/', null=True, blank=True, verbose_name="照片")
    price_range = models.CharField(max_length=50, blank=True, verbose_name="价格区间")
    opening_hours = models.CharField(max_length=100, blank=True, verbose_name="营业时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    ratings = GenericRelation('Rating', related_query_name='canteen')
    
    class Meta:
        verbose_name = "食堂窗口"
        verbose_name_plural = "食堂窗口"
        ordering = ['canteen_building', 'name']
        indexes = [
            models.Index(fields=['canteen_building']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.canteen_building} - {self.name}"
    
    @property
    def average_rating(self):
        """平均评分"""
        result = self.ratings.aggregate(avg=Avg('score'))
        if result['avg']:
            return round(result['avg'], 1)
        return 0
    
    @property
    def rating_count(self):
        """评价数量"""
        return self.ratings.count()


class Rating(models.Model):
    """评价（支持教师和食堂）"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings_given',
        verbose_name="评价人"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="评分"
    )
    comment = models.TextField(blank=True, verbose_name="评论")
    tags = models.ManyToManyField(Tag, blank=True, related_name='ratings', verbose_name="标签")
    is_anonymous = models.BooleanField(default=False, verbose_name="是否匿名")
    helpful_count = models.IntegerField(default=0, verbose_name="有用数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "评价"
        verbose_name_plural = "评价"
        ordering = ['-created_at']
        unique_together = [['user', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 评价了 {self.content_object} - {self.score}星"


class HelpfulMark(models.Model):
    """有用标记"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='helpful_marks',
        verbose_name="用户"
    )
    rating = models.ForeignKey(
        Rating,
        on_delete=models.CASCADE,
        related_name='helpful_marks',
        verbose_name="评价"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "有用标记"
        verbose_name_plural = "有用标记"
        unique_together = [['user', 'rating']]
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username} 觉得有用"
