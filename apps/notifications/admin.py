from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'actor', 'action_type', 'is_read', 'created_at']
    list_filter = ['action_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'actor__email']
    readonly_fields = ['created_at']

