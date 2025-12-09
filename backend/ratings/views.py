from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, F
from django.db import transaction
from .models import Tag, Teacher, Canteen, Rating, HelpfulMark
from .serializers import (
    TagSerializer,
    TeacherListSerializer,
    TeacherDetailSerializer,
    CanteenListSerializer,
    CanteenDetailSerializer,
    RatingSerializer,
    RatingCreateSerializer,
    RatingUpdateSerializer
)


class IsVerifiedUser(permissions.BasePermission):
    """仅实名认证用户可以评价"""
    message = "您需要完成实名认证才能评价"
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_verified


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """标签视图集（只读）"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category.upper())
        return queryset


class TeacherViewSet(viewsets.ModelViewSet):
    """教师视图集"""
    queryset = Teacher.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'department', 'courses']
    ordering_fields = ['name', 'department', 'created_at']
    ordering = ['department', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TeacherListSerializer
        return TeacherDetailSerializer
    
    def get_permissions(self):
        # Only admin can create/update/delete teachers
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)
        return queryset
    
    @action(detail=True, methods=['get'])
    def ratings(self, request, pk=None):
        """获取教师的所有评价"""
        teacher = self.get_object()
        content_type = ContentType.objects.get_for_model(Teacher)
        ratings = Rating.objects.filter(
            content_type=content_type,
            object_id=teacher.id
        ).prefetch_related('tags').select_related('user').order_by('-created_at')
        
        # Pagination
        page = self.paginate_queryset(ratings)
        if page is not None:
            serializer = RatingSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = RatingSerializer(ratings, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取教师的评价统计"""
        teacher = self.get_object()
        content_type = ContentType.objects.get_for_model(Teacher)
        ratings = Rating.objects.filter(
            content_type=content_type,
            object_id=teacher.id
        ).prefetch_related('tags')
        
        # Score distribution
        score_distribution = {}
        for i in range(1, 6):
            score_distribution[f'{i}星'] = ratings.filter(score=i).count()
        
        # Tag statistics
        tag_stats = {}
        for rating in ratings:
            for tag in rating.tags.all():
                tag_stats[tag.name] = tag_stats.get(tag.name, 0) + 1
        
        return Response({
            'average_rating': teacher.average_rating,
            'total_ratings': teacher.rating_count,
            'score_distribution': score_distribution,
            'popular_tags': sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        })


class CanteenViewSet(viewsets.ModelViewSet):
    """食堂窗口视图集"""
    queryset = Canteen.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'canteen_building', 'specialties']
    ordering_fields = ['name', 'canteen_building', 'created_at']
    ordering = ['canteen_building', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CanteenListSerializer
        return CanteenDetailSerializer
    
    def get_permissions(self):
        # Only admin can create/update/delete canteen
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        building = self.request.query_params.get('building')
        if building:
            queryset = queryset.filter(canteen_building__icontains=building)
        return queryset
    
    @action(detail=True, methods=['get'])
    def ratings(self, request, pk=None):
        """获取食堂窗口的所有评价"""
        canteen = self.get_object()
        content_type = ContentType.objects.get_for_model(Canteen)
        ratings = Rating.objects.filter(
            content_type=content_type,
            object_id=canteen.id
        ).prefetch_related('tags').select_related('user').order_by('-created_at')
        
        # Pagination
        page = self.paginate_queryset(ratings)
        if page is not None:
            serializer = RatingSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = RatingSerializer(ratings, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取食堂窗口的评价统计"""
        canteen = self.get_object()
        content_type = ContentType.objects.get_for_model(Canteen)
        ratings = Rating.objects.filter(
            content_type=content_type,
            object_id=canteen.id
        ).prefetch_related('tags')
        
        # Score distribution
        score_distribution = {}
        for i in range(1, 6):
            score_distribution[f'{i}星'] = ratings.filter(score=i).count()
        
        # Tag statistics
        tag_stats = {}
        for rating in ratings:
            for tag in rating.tags.all():
                tag_stats[tag.name] = tag_stats.get(tag.name, 0) + 1
        
        return Response({
            'average_rating': canteen.average_rating,
            'total_ratings': canteen.rating_count,
            'score_distribution': score_distribution,
            'popular_tags': sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        })


class RatingViewSet(viewsets.ModelViewSet):
    """评价视图集"""
    queryset = Rating.objects.all()
    permission_classes = [IsVerifiedUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RatingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RatingUpdateSerializer
        return RatingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by target type and id
        target_type = self.request.query_params.get('target_type')
        target_id = self.request.query_params.get('target_id')
        
        if target_type and target_id:
            if target_type == 'teacher':
                content_type = ContentType.objects.get_for_model(Teacher)
            elif target_type == 'canteen':
                content_type = ContentType.objects.get_for_model(Canteen)
            else:
                return queryset.none()
            
            queryset = queryset.filter(content_type=content_type, object_id=target_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create rating
        validated_data = serializer.validated_data
        tag_ids = validated_data.pop('tags', [])
        content_type = validated_data.pop('content_type')
        model_class = validated_data.pop('model_class')
        target_id = validated_data.pop('target_id')
        validated_data.pop('target_type')
        
        rating = Rating.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=target_id,
            **validated_data
        )
        
        # Add tags
        if tag_ids:
            rating.tags.set(Tag.objects.filter(id__in=tag_ids))
        
        return Response(
            RatingSerializer(rating, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    def perform_update(self, serializer):
        # Only author can update
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied('您没有权限修改此评价')
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only author or admin can delete
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('您没有权限删除此评价')
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """标记评价为有用/取消标记"""
        rating = self.get_object()
        
        with transaction.atomic():
            helpful_mark, created = HelpfulMark.objects.get_or_create(
                user=request.user,
                rating=rating
            )
            
            if not created:
                helpful_mark.delete()
                # Use F() expression for atomic decrement
                Rating.objects.filter(pk=rating.pk).update(helpful_count=F('helpful_count') - 1)
                return Response({'message': '已取消标记', 'marked': False})
            
            # Use F() expression for atomic increment
            Rating.objects.filter(pk=rating.pk).update(helpful_count=F('helpful_count') + 1)
            return Response({'message': '已标记为有用', 'marked': True})
    
    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """获取当前用户的评价"""
        ratings = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(ratings)
        if page is not None:
            serializer = RatingSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = RatingSerializer(ratings, many=True, context={'request': request})
        return Response(serializer.data)
