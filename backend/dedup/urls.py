from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DedupViewSet

router = DefaultRouter()
router.register(r'dedup', DedupViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 