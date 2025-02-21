"""
Views for the app APIs
"""
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from apps.models import App
from apps import serializers


class AppViewSet(viewsets.ModelViewSet):
    """View for manage app APIs."""
    serializer_class = serializers.AppDetailSerializer
    queryset = App.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AppSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Ensure only the owner can delete the app. Return 404 if the app is not found
        or if the user is not the owner of the app.
        """
        app = self.get_object()
        if app.owner != request.user:
            raise NotFound("You do not have permission to delete this app.")
        return super().destroy(request, *args, **kwargs)