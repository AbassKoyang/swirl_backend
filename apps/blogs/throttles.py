from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class PostCreateRateThrottle(UserRateThrottle):
    rate = '10/min'


class PostUpdateRateThrottle(UserRateThrottle):
    rate = '20/min'


class CommentCreateRateThrottle(UserRateThrottle):
    rate = '30/min'


class ReactionRateThrottle(UserRateThrottle):
    """
    Rate limit for reactions.
    60 requests per minute.
    """
    rate = '60/min'


class BookmarkRateThrottle(UserRateThrottle):
    rate = '30/min'


class PostReadRateThrottle(UserRateThrottle):
    rate = '100/min'


class PostReadAnonRateThrottle(AnonRateThrottle):
    rate = '50/min'

