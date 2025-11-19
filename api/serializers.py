from rest_framework import serializers
from app.models import Support


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = ['id', 'user', 'subject', 'description', 'image', 'status', 'created_at']


