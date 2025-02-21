"""
URL mappings for the app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from apps import views


router = DefaultRouter()
router.register('apps', views.AppViewSet)

app_name = 'app'

urlpatterns = [
    path('', include(router.urls)),
]
