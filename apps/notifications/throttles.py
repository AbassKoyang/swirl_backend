from rest_framework.throttling import UserRateThrottle


class NotificationReadRateThrottle(UserRateThrottle):
    """
    Rate limit for reading notifications.
    100 requests per minute.
    """
    rate = '100/min'


class NotificationMarkReadRateThrottle(UserRateThrottle):
    """
    Rate limit for marking notifications as read.
    60 requests per minute.
    """
    rate = '60/min'

