from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Category, Post, Comment, Like
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'icon', 'order', 'post_count', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_post_count(self, obj):
        return obj.posts.count()


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author = UserSerializer(read_only=True)
    like_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'content', 'parent', 'like_count', 
                  'is_liked', 'replies', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Comment)
            return Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False
    
    def get_replies(self, obj):
        if obj.parent is None:  # Only show replies for top-level comments
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class PostListSerializer(serializers.ModelSerializer):
    """帖子列表序列化器（简化版）"""
    author = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comment_count = serializers.ReadOnlyField()
    like_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'author', 'category', 'category_name', 
                  'is_pinned', 'view_count', 'comment_count', 'like_count',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'view_count', 'created_at', 'updated_at')


class PostDetailSerializer(serializers.ModelSerializer):
    """帖子详情序列化器"""
    author = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comment_count = serializers.ReadOnlyField()
    like_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'category', 'category_name',
                  'images', 'is_pinned', 'is_locked', 'view_count', 'comment_count',
                  'like_count', 'is_liked', 'comments', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'view_count', 'created_at', 'updated_at')
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(Post)
            return Like.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.id
            ).exists()
        return False
    
    def get_comments(self, obj):
        # Only return top-level comments, replies are nested within them
        comments = obj.comments.filter(parent=None)
        return CommentSerializer(comments, many=True, context=self.context).data


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """帖子创建和更新序列化器"""
    
    class Meta:
        model = Post
        fields = ('title', 'content', 'category', 'images')
    
    def validate_images(self, value):
        """验证图片列表"""
        if not isinstance(value, list):
            raise serializers.ValidationError("图片必须是列表格式")
        if len(value) > 9:
            raise serializers.ValidationError("最多只能上传9张图片")
        return value


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""
    
    class Meta:
        model = Comment
        fields = ('post', 'content', 'parent')
    
    def validate(self, attrs):
        # Validate parent comment belongs to the same post
        if attrs.get('parent'):
            if attrs['parent'].post != attrs['post']:
                raise serializers.ValidationError("父评论必须属于同一个帖子")
        return attrs


class LikeSerializer(serializers.Serializer):
    """点赞序列化器"""
    content_type = serializers.CharField()
    object_id = serializers.IntegerField()
    
    def validate_content_type(self, value):
        """验证内容类型"""
        if value not in ['post', 'comment']:
            raise serializers.ValidationError("内容类型必须是 'post' 或 'comment'")
        return value
    
    def validate(self, attrs):
        content_type_str = attrs['content_type']
        object_id = attrs['object_id']
        
        # Get the actual content type
        if content_type_str == 'post':
            content_type = ContentType.objects.get_for_model(Post)
            model_class = Post
        else:
            content_type = ContentType.objects.get_for_model(Comment)
            model_class = Comment
        
        # Check if object exists
        if not model_class.objects.filter(id=object_id).exists():
            raise serializers.ValidationError(f"{content_type_str} 不存在")
        
        attrs['content_type_obj'] = content_type
        return attrs
