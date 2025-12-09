from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Tag, Teacher, Canteen, Rating, HelpfulMark
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Tag
        fields = ('id', 'name', 'category', 'category_display', 'color', 'order')
        read_only_fields = ('id',)


class TeacherListSerializer(serializers.ModelSerializer):
    """教师列表序列化器（简化版）"""
    average_rating = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Teacher
        fields = ('id', 'name', 'department', 'title', 'courses', 'image',
                  'average_rating', 'rating_count')
        read_only_fields = ('id',)


class TeacherDetailSerializer(serializers.ModelSerializer):
    """教师详情序列化器"""
    average_rating = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Teacher
        fields = ('id', 'name', 'department', 'title', 'courses', 'bio', 'image',
                  'email', 'office', 'average_rating', 'rating_count',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class CanteenListSerializer(serializers.ModelSerializer):
    """食堂窗口列表序列化器（简化版）"""
    average_rating = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Canteen
        fields = ('id', 'name', 'canteen_building', 'location', 'specialties',
                  'image', 'price_range', 'average_rating', 'rating_count')
        read_only_fields = ('id',)


class CanteenDetailSerializer(serializers.ModelSerializer):
    """食堂窗口详情序列化器"""
    average_rating = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Canteen
        fields = ('id', 'name', 'canteen_building', 'location', 'description',
                  'specialties', 'image', 'price_range', 'opening_hours',
                  'average_rating', 'rating_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class RatingSerializer(serializers.ModelSerializer):
    """评价序列化器"""
    user = UserSerializer(read_only=True)
    user_display = serializers.SerializerMethodField()
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    target_type = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()
    is_helpful = serializers.SerializerMethodField()
    
    class Meta:
        model = Rating
        fields = ('id', 'user', 'user_display', 'score', 'comment', 'tags', 'tags_detail',
                  'is_anonymous', 'helpful_count', 'is_helpful', 'target_type', 'target_name',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'helpful_count', 'created_at', 'updated_at')
    
    def get_user_display(self, obj):
        """根据是否匿名返回用户信息"""
        if obj.is_anonymous:
            return {"username": "匿名用户", "real_name": "匿名"}
        return UserSerializer(obj.user).data
    
    def get_target_type(self, obj):
        """获取评价对象类型"""
        if isinstance(obj.content_object, Teacher):
            return 'teacher'
        elif isinstance(obj.content_object, Canteen):
            return 'canteen'
        return 'unknown'
    
    def get_target_name(self, obj):
        """获取评价对象名称"""
        if obj.content_object:
            return str(obj.content_object)
        return ''
    
    def get_is_helpful(self, obj):
        """当前用户是否标记为有用"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return HelpfulMark.objects.filter(user=request.user, rating=obj).exists()
        return False


class RatingCreateSerializer(serializers.Serializer):
    """创建评价序列化器"""
    target_type = serializers.ChoiceField(choices=['teacher', 'canteen'])
    target_id = serializers.IntegerField()
    score = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    is_anonymous = serializers.BooleanField(default=False)
    
    def validate(self, attrs):
        target_type = attrs['target_type']
        target_id = attrs['target_id']
        
        # Get the model class and content type
        if target_type == 'teacher':
            model_class = Teacher
            content_type = ContentType.objects.get_for_model(Teacher)
        else:
            model_class = Canteen
            content_type = ContentType.objects.get_for_model(Canteen)
        
        # Check if target exists
        if not model_class.objects.filter(id=target_id).exists():
            raise serializers.ValidationError(f"{target_type} 不存在")
        
        # Check if user already rated this target
        user = self.context['request'].user
        if Rating.objects.filter(
            user=user,
            content_type=content_type,
            object_id=target_id
        ).exists():
            raise serializers.ValidationError("您已经评价过该对象")
        
        # Validate tags
        if 'tags' in attrs and attrs['tags']:
            tag_category = 'TEACHER' if target_type == 'teacher' else 'CANTEEN'
            valid_tags = Tag.objects.filter(id__in=attrs['tags'], category=tag_category)
            if len(valid_tags) != len(attrs['tags']):
                raise serializers.ValidationError("部分标签不存在或不适用于该类型")
        
        attrs['content_type'] = content_type
        attrs['model_class'] = model_class
        return attrs


class RatingUpdateSerializer(serializers.ModelSerializer):
    """更新评价序列化器"""
    
    class Meta:
        model = Rating
        fields = ('score', 'comment', 'tags', 'is_anonymous')
    
    def validate_tags(self, value):
        """验证标签是否适用"""
        instance = self.instance
        if isinstance(instance.content_object, Teacher):
            category = 'TEACHER'
        else:
            category = 'CANTEEN'
        
        valid_tags = Tag.objects.filter(id__in=[t.id for t in value], category=category)
        if len(valid_tags) != len(value):
            raise serializers.ValidationError("部分标签不适用于该类型")
        return value
