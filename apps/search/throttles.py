from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class SearchRateThrottle(UserRateThrottle):
    """
    Rate limit for search operations (can be resource intensive).
    30 requests per minute for authenticated users.
    """
    rate = '30/min'


class SearchAnonRateThrottle(AnonRateThrottle):
    """
    Rate limit for anonymous search operations.
    10 requests per minute.
    """
    rate = '10/min'

