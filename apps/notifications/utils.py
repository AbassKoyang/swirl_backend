from django.contrib.contenttypes.models import ContentType
from .models import Notification
from .services import send_email_notification, send_push_notification


def create_notification(user, actor, action_type, target_object=None, send_push=True):
    if user == actor and target_object is not None:
        return None
    
    try:
        if target_object is None:
            notification = Notification.objects.create(
                user=user,
                actor=actor,
                action_type=action_type,
                content_type=None,
                object_id=None
            )
        else:
            content_type = ContentType.objects.get_for_model(target_object)
            notification = Notification.objects.create(
                user=user,
                actor=actor,
                action_type=action_type,
                content_type=content_type,
                object_id=target_object.pk
            )
        
        if send_push:
            push_sent = send_push_notification(notification)
            if push_sent:
                notification.push_sent = True
                notification.save(update_fields=['push_sent'])
        
        return notification
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None
