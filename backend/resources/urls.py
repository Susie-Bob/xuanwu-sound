from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceCategoryViewSet, ResourceViewSet, ResourceCommentViewSet

app_name = 'resources'

router = DefaultRouter()
router.register(r'categories', ResourceCategoryViewSet, basename='category')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'comments', ResourceCommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
