from rest_framework import serializers

from apps.models import App
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'owner', 'app', 'purchase_date']
        read_only_fields = ['id', 'owner', 'purchase_date']

    def create(self, validated_data):
        """Ensure the app is verified before allowing it to be purchased."""
        app = validated_data.get('app')

        # Check if the app is verified
        if app.verification_status != App.STATUS_VERIFIED:
            raise serializers.ValidationError("This app cannot be purchased until it is verified.")

        # Proceed with creating the order
        return super().create(validated_data)
