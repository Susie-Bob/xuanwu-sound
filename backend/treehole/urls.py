from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TreeholePostViewSet, TreeholeCommentViewSet

app_name = 'treehole'

router = DefaultRouter()
router.register(r'posts', TreeholePostViewSet, basename='post')
router.register(r'comments', TreeholeCommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]
