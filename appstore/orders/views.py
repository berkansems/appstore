from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter orders to return only the ones belonging to the current user
        queryset = Order.objects.filter(owner=self.request.user)
        return queryset

    def perform_create(self, serializer):
        # Automatically set the owner to the authenticated user
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Retrieve the order object to check its owner
        order = self.get_object()

        # Check if the authenticated user is the owner of the order
        if order.owner != request.user:
            raise PermissionDenied("You cannot delete someone else's order.")

        # If the check passes, proceed with the deletion
        return super().destroy(request, *args, **kwargs)
