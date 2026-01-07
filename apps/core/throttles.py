from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AuthRateThrottle(UserRateThrottle):

    rate = '5/min'


class AuthAnonRateThrottle(AnonRateThrottle):

    rate = '3/min'


class UserActionRateThrottle(UserRateThrottle):
    rate = '20/min'


class ReadOnlyRateThrottle(UserRateThrottle):
    rate = '100/min'


class ReadOnlyAnonRateThrottle(AnonRateThrottle):
    rate = '30/min'

