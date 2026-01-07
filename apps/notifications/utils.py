from django.contrib.contenttypes.models import ContentType
from .models import Notification


def create_notification(user, actor, action_type, target_object=None):
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
        return notification
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None

