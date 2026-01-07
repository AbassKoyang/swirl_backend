from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class FeedRateThrottle(UserRateThrottle):
    """
    Rate limit for feed operations (can be resource intensive).
    60 requests per minute for authenticated users.
    """
    rate = '60/min'


class FeedAnonRateThrottle(AnonRateThrottle):
    """
    Rate limit for anonymous feed operations.
    20 requests per minute.
    """
    rate = '20/min'

