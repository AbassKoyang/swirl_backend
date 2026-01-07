from rest_framework import serializers
from .models import Notification
from apps.core.serializers import UserSummarySerializer


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    actor = UserSummarySerializer(read_only=True)
    target_object_id = serializers.IntegerField(source='object_id', read_only=True)
    target_content_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'actor',
            'action_type',
            'target_object_id',
            'target_content_type',
            'is_read',
            'created_at'
        ]
        read_only_fields = [
            'user',
            'actor',
            'action_type',
            'target_object_id',
            'target_content_type',
            'created_at'
        ]


class MarkNotificationReadSerializer(serializers.Serializer):
    """Serializer for marking notification as read"""
    pass

