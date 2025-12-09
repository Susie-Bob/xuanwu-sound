from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="确认密码")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'real_name', 'student_id', 'identity_type')
        extra_kwargs = {
            'email': {'required': True},
            'real_name': {'required': False},
            'student_id': {'required': False},
            'identity_type': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次输入的密码不一致"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    identity_type_display = serializers.CharField(source='get_identity_type_display', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'real_name', 'student_id', 'identity_type', 
                  'identity_type_display', 'is_verified', 'avatar', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'is_verified')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ('real_name', 'student_id', 'identity_type', 'avatar')
        extra_kwargs = {
            'student_id': {'required': False},
        }
    
    def validate_student_id(self, value):
        """Ensure student_id is unique if provided"""
        user = self.context['request'].user
        if value and User.objects.exclude(pk=user.pk).filter(student_id=value).exists():
            raise serializers.ValidationError("该学号/工号已被使用")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True, label="旧密码")
    new_password = serializers.CharField(required=True, validators=[validate_password], label="新密码")
    new_password2 = serializers.CharField(required=True, label="确认新密码")
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "两次输入的新密码不一致"})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value
