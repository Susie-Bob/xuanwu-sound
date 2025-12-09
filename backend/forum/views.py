from django.shortcuts import render

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from .models import Category, Post, Comment, Like
from .serializers import (
    CategorySerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    LikeSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        # Only admin can create/update/delete categories
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class PostViewSet(viewsets.ModelViewSet):
    """帖子视图集"""
    queryset = Post.objects.select_related('author', 'category').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count', 'updated_at']
    ordering = ['-is_pinned', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by author
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        # Only author or admin can update
        instance = self.get_object()
        if instance.author != self.request.user and not self.request.user.is_staff:
            return Response(
                {'detail': '您没有权限修改此帖子'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only author or admin can delete
        if instance.author != self.request.user and not self.request.user.is_staff:
            return Response(
                {'detail': '您没有权限删除此帖子'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞或取消点赞帖子"""
        post = self.get_object()
        content_type = ContentType.objects.get_for_model(Post)
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=post.id
        )
        
        if not created:
            like.delete()
            return Response({'message': '已取消点赞', 'liked': False})
        
        return Response({'message': '点赞成功', 'liked': True})
    
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """获取当前用户的帖子"""
        posts = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    queryset = Comment.objects.select_related('author', 'post', 'parent').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by post
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        # Only author can update
        instance = self.get_object()
        if instance.author != self.request.user:
            return Response(
                {'detail': '您没有权限修改此评论'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only author or admin can delete
        if instance.author != self.request.user and not self.request.user.is_staff:
            return Response(
                {'detail': '您没有权限删除此评论'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞或取消点赞评论"""
        comment = self.get_object()
        content_type = ContentType.objects.get_for_model(Comment)
        
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=comment.id
        )
        
        if not created:
            like.delete()
            return Response({'message': '已取消点赞', 'liked': False})
        
        return Response({'message': '点赞成功', 'liked': True})
