from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import TreeholePost, TreeholeComment, TreeholeLike
from .utils import generate_anonymous_name, should_refresh_anonymous_name


class TreeholeCommentSerializer(serializers.ModelSerializer):
    """树洞评论序列化器"""
    anonymous_name = serializers.CharField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = TreeholeComment
        fields = ('id', 'post', 'anonymous_name', 'content', 'parent', 
                  'likes_count', 'is_liked', 'replies', 'created_at', 'is_hidden')
        read_only_fields = ('id', 'anonymous_name', 'created_at', 'is_hidden')
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TreeholeLike.objects.filter(
                user=request.user,
                comment=obj
            ).exists()
        return False
    
    def get_replies(self, obj):
        if obj.parent is None:  # Only show replies for top-level comments
            replies = obj.replies.filter(is_hidden=False)
            return TreeholeCommentSerializer(replies, many=True, context=self.context).data
        return []


class TreeholeCommentCreateSerializer(serializers.ModelSerializer):
    """树洞评论创建序列化器"""
    anonymous_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = TreeholeComment
        fields = ('post', 'content', 'parent', 'anonymous_name', 'id', 'created_at')
        read_only_fields = ('anonymous_name', 'id', 'created_at')
    
    def validate(self, attrs):
        # Validate parent comment belongs to the same post
        if attrs.get('parent'):
            if attrs['parent'].post != attrs['post']:
                raise serializers.ValidationError("父评论必须属于同一个帖子")
        return attrs
    
    def create(self, validated_data):
        # Generate anonymous name
        user = self.context['request'].user
        validated_data['author'] = user
        validated_data['anonymous_name'] = generate_anonymous_name()
        validated_data['anonymous_name_expires'] = timezone.now() + timedelta(hours=24)
        
        comment = super().create(validated_data)
        
        # Update post comments count
        post = comment.post
        post.comments_count = post.comments.count()
        post.save(update_fields=['comments_count'])
        
        return comment


class TreeholePostListSerializer(serializers.ModelSerializer):
    """树洞帖子列表序列化器（简化版）"""
    anonymous_name = serializers.CharField(read_only=True)
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = TreeholePost
        fields = ('id', 'anonymous_name', 'content', 'post_type', 'post_type_display',
                  'likes_count', 'comments_count', 'created_at', 'is_hidden')
        read_only_fields = ('id', 'anonymous_name', 'created_at', 'is_hidden')


class TreeholePostDetailSerializer(serializers.ModelSerializer):
    """树洞帖子详情序列化器"""
    anonymous_name = serializers.CharField(read_only=True)
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = TreeholePost
        fields = ('id', 'anonymous_name', 'content', 'images', 'post_type', 
                  'post_type_display', 'likes_count', 'comments_count', 'is_liked',
                  'comments', 'created_at', 'updated_at', 'is_hidden')
        read_only_fields = ('id', 'anonymous_name', 'created_at', 'updated_at', 'is_hidden')
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TreeholeLike.objects.filter(
                user=request.user,
                post=obj
            ).exists()
        return False
    
    def get_comments(self, obj):
        # Only return top-level comments that are not hidden
        comments = obj.comments.filter(parent=None, is_hidden=False)
        return TreeholeCommentSerializer(comments, many=True, context=self.context).data


class TreeholePostCreateSerializer(serializers.ModelSerializer):
    """树洞帖子创建序列化器"""
    anonymous_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = TreeholePost
        fields = ('content', 'images', 'post_type', 'anonymous_name', 'id', 'created_at')
        read_only_fields = ('anonymous_name', 'id', 'created_at')
    
    def validate_images(self, value):
        """验证图片列表"""
        if not isinstance(value, list):
            raise serializers.ValidationError("图片必须是列表格式")
        if len(value) > 9:
            raise serializers.ValidationError("最多只能上传9张图片")
        return value
    
    def create(self, validated_data):
        # Generate anonymous name
        user = self.context['request'].user
        validated_data['author'] = user
        validated_data['anonymous_name'] = generate_anonymous_name()
        validated_data['anonymous_name_expires'] = timezone.now() + timedelta(hours=24)
        
        return super().create(validated_data)
