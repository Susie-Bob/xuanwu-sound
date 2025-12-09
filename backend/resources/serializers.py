from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ResourceCategory, Resource, ResourceDownload, ResourceComment
from users.serializers import UserSerializer

User = get_user_model()


class ResourceCategorySerializer(serializers.ModelSerializer):
    """资源分类序列化器"""
    resource_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ResourceCategory
        fields = ('id', 'name', 'description', 'icon', 'order', 'resource_count', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_resource_count(self, obj):
        return obj.resources.filter(is_approved=True).count()


class ResourceListSerializer(serializers.ModelSerializer):
    """资源列表序列化器（简化版）"""
    uploader = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    file_extension = serializers.ReadOnlyField()
    file_size_mb = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Resource
        fields = ('id', 'title', 'description', 'category', 'category_name', 'uploader',
                  'course', 'year', 'semester', 'tags', 'file_extension', 'file_size_mb',
                  'download_count', 'average_rating', 'comment_count', 'created_at')
        read_only_fields = ('id', 'uploader', 'download_count', 'created_at')


class ResourceDetailSerializer(serializers.ModelSerializer):
    """资源详情序列化器"""
    uploader = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    file_extension = serializers.ReadOnlyField()
    file_size_mb = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = ('id', 'title', 'description', 'file_url', 'category', 'category_name',
                  'uploader', 'course', 'year', 'semester', 'tags', 'file_extension',
                  'file_size', 'file_size_mb', 'download_count', 'average_rating',
                  'comment_count', 'is_approved', 'created_at', 'updated_at')
        read_only_fields = ('id', 'uploader', 'file_size', 'download_count', 'created_at', 'updated_at')
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ResourceUploadSerializer(serializers.ModelSerializer):
    """资源上传序列化器"""
    
    class Meta:
        model = Resource
        fields = ('title', 'description', 'file', 'category', 'course', 'year', 'semester', 'tags')
    
    def validate_file(self, value):
        """验证文件"""
        # Check file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100 MB
        if value.size > max_size:
            raise serializers.ValidationError("文件大小不能超过100MB")
        return value
    
    def validate_tags(self, value):
        """验证标签格式"""
        if value:
            tags = [tag.strip() for tag in value.split(',')]
            if len(tags) > 10:
                raise serializers.ValidationError("最多只能添加10个标签")
        return value


class ResourceUpdateSerializer(serializers.ModelSerializer):
    """资源更新序列化器"""
    
    class Meta:
        model = Resource
        fields = ('title', 'description', 'category', 'course', 'year', 'semester', 'tags')


class ResourceCommentSerializer(serializers.ModelSerializer):
    """资源评论序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ResourceComment
        fields = ('id', 'resource', 'user', 'content', 'rating', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def validate_rating(self, value):
        """验证评分"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("评分必须在1到5之间")
        return value


class ResourceDownloadSerializer(serializers.ModelSerializer):
    """资源下载记录序列化器"""
    user = UserSerializer(read_only=True)
    resource_title = serializers.CharField(source='resource.title', read_only=True)
    
    class Meta:
        model = ResourceDownload
        fields = ('id', 'resource', 'resource_title', 'user', 'downloaded_at', 'ip_address')
        read_only_fields = ('id', 'user', 'downloaded_at', 'ip_address')
