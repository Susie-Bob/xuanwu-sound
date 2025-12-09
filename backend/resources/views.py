from django.shortcuts import render

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.db.models import F, Q
from django.db import transaction
from .models import ResourceCategory, Resource, ResourceDownload, ResourceComment
from .serializers import (
    ResourceCategorySerializer,
    ResourceListSerializer,
    ResourceDetailSerializer,
    ResourceUploadSerializer,
    ResourceUpdateSerializer,
    ResourceCommentSerializer,
    ResourceDownloadSerializer
)


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ResourceCategoryViewSet(viewsets.ModelViewSet):
    """资源分类视图集"""
    queryset = ResourceCategory.objects.all()
    serializer_class = ResourceCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        # Only admin can create/update/delete categories
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ResourceViewSet(viewsets.ModelViewSet):
    """资源视图集"""
    queryset = Resource.objects.filter(is_approved=True).select_related('uploader', 'category')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'course', 'tags']
    ordering_fields = ['created_at', 'download_count', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ResourceListSerializer
        elif self.action == 'create':
            return ResourceUploadSerializer
        elif self.action in ['update', 'partial_update']:
            return ResourceUpdateSerializer
        return ResourceDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by uploader
        uploader_id = self.request.query_params.get('uploader')
        if uploader_id:
            queryset = queryset.filter(uploader_id=uploader_id)
        
        # Filter by course
        course = self.request.query_params.get('course')
        if course:
            queryset = queryset.filter(course__icontains=course)
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        # Filter by file extension
        file_ext = self.request.query_params.get('file_type')
        if file_ext:
            queryset = queryset.filter(file__iendswith=f'.{file_ext}')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)
    
    def perform_update(self, serializer):
        # Only uploader or admin can update
        instance = self.get_object()
        if instance.uploader != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('您没有权限修改此资源')
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only uploader or admin can delete
        if instance.uploader != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('您没有权限删除此资源')
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """下载资源文件"""
        resource = self.get_object()
        
        if not resource.file:
            raise Http404("文件不存在")
        
        # Record download
        if request.user.is_authenticated:
            ResourceDownload.objects.create(
                resource=resource,
                user=request.user,
                ip_address=get_client_ip(request)
            )
            # Increment download count atomically
            Resource.objects.filter(pk=resource.pk).update(download_count=F('download_count') + 1)
        
        # Return file response
        try:
            response = FileResponse(resource.file.open('rb'), as_attachment=True, 
                                   filename=resource.file.name.split('/')[-1])
            return response
        except FileNotFoundError:
            raise Http404("文件不存在")
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取资源评论"""
        resource = self.get_object()
        comments = resource.comments.all().order_by('-created_at')
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = ResourceCommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ResourceCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_uploads(self, request):
        """获取我上传的资源"""
        resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')
        page = self.paginate_queryset(resources)
        if page is not None:
            serializer = ResourceListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ResourceListSerializer(resources, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_downloads(self, request):
        """获取我下载的资源"""
        downloads = ResourceDownload.objects.filter(user=request.user).select_related('resource').order_by('-downloaded_at')
        page = self.paginate_queryset(downloads)
        if page is not None:
            serializer = ResourceDownloadSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ResourceDownloadSerializer(downloads, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取资源统计信息"""
        resource = self.get_object()
        
        # Download statistics by user type
        downloads = resource.downloads.select_related('user')
        download_by_identity = {}
        for download in downloads:
            if download.user.identity_type:
                identity = download.user.get_identity_type_display()
                download_by_identity[identity] = download_by_identity.get(identity, 0) + 1
        
        return Response({
            'total_downloads': resource.download_count,
            'average_rating': resource.average_rating,
            'comment_count': resource.comment_count,
            'download_by_identity': download_by_identity
        })


class ResourceCommentViewSet(viewsets.ModelViewSet):
    """资源评论视图集"""
    queryset = ResourceComment.objects.all().select_related('user', 'resource')
    serializer_class = ResourceCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by resource
        resource_id = self.request.query_params.get('resource')
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        # Only author can update
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied('您没有权限修改此评论')
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only author or admin can delete
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('您没有权限删除此评论')
        instance.delete()
