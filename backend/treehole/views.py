from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import TreeholePost, TreeholeComment, TreeholeLike
from .serializers import (
    TreeholePostListSerializer,
    TreeholePostDetailSerializer,
    TreeholePostCreateSerializer,
    TreeholeCommentSerializer,
    TreeholeCommentCreateSerializer,
)


class TreeholePostViewSet(viewsets.ModelViewSet):
    """树洞帖子视图集"""
    queryset = TreeholePost.objects.filter(is_hidden=False)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['content']
    ordering_fields = ['created_at', 'likes_count', 'comments_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TreeholePostListSerializer
        elif self.action == 'create':
            return TreeholePostCreateSerializer
        return TreeholePostDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by post type
        post_type = self.request.query_params.get('post_type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        return queryset
    
    def perform_destroy(self, instance):
        # Only author or admin can delete
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('您没有权限删除此帖子')
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞或取消点赞帖子"""
        post = self.get_object()
        
        like, created = TreeholeLike.objects.get_or_create(
            user=request.user,
            post=post,
            defaults={'comment': None}
        )
        
        if not created:
            like.delete()
            # Update likes count
            post.likes_count = post.likes.count()
            post.save(update_fields=['likes_count'])
            return Response({'message': '已取消点赞', 'liked': False})
        
        # Update likes count
        post.likes_count = post.likes.count()
        post.save(update_fields=['likes_count'])
        return Response({'message': '点赞成功', 'liked': True})
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取帖子的所有评论"""
        post = self.get_object()
        comments = post.comments.filter(parent=None, is_hidden=False)
        serializer = TreeholeCommentSerializer(
            comments, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)


class TreeholeCommentViewSet(viewsets.ModelViewSet):
    """树洞评论视图集"""
    queryset = TreeholeComment.objects.filter(is_hidden=False)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TreeholeCommentCreateSerializer
        return TreeholeCommentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by post
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset
    
    def perform_destroy(self, instance):
        # Only author or admin can delete
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('您没有权限删除此评论')
        
        # Update post comments count
        post = instance.post
        instance.delete()
        post.comments_count = post.comments.count()
        post.save(update_fields=['comments_count'])
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞或取消点赞评论"""
        comment = self.get_object()
        
        like, created = TreeholeLike.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'post': None}
        )
        
        if not created:
            like.delete()
            # Update likes count
            comment.likes_count = comment.likes.count()
            comment.save(update_fields=['likes_count'])
            return Response({'message': '已取消点赞', 'liked': False})
        
        # Update likes count
        comment.likes_count = comment.likes.count()
        comment.save(update_fields=['likes_count'])
        return Response({'message': '点赞成功', 'liked': True})
