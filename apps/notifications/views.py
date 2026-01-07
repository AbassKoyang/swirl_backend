from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Notification
from .serializers import NotificationSerializer
from .throttles import NotificationReadRateThrottle, NotificationMarkReadRateThrottle


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [NotificationReadRateThrottle]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('user', 'actor').order_by('-created_at')


class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [NotificationMarkReadRateThrottle]

    def post(self, request, id, **kwargs):
        notification = get_object_or_404(
            Notification,
            pk=id,
            user=request.user
        )
        
        if notification.is_read:
            return Response(
                {"message": "Notification is already marked as read"},
                status=status.HTTP_200_OK
            )
        
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)

