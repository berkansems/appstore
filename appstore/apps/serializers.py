from rest_framework import serializers
from .models import App


class AppSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = App
        fields = ['id', 'title', 'price', 'owner', 'verification_status']
        read_only_fields = ['id', 'owner', 'verification_status']

class AppDetailSerializer(AppSerializer):
    class Meta(AppSerializer.Meta):
        fields = AppSerializer.Meta.fields + ['description']
