from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, TeacherViewSet, CanteenViewSet, RatingViewSet

app_name = 'ratings'

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'canteen', CanteenViewSet, basename='canteen')
router.register(r'ratings', RatingViewSet, basename='rating')

urlpatterns = [
    path('', include(router.urls)),
]
