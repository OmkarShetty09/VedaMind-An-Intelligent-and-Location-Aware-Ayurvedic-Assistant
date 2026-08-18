from rest_framework.throttling import AnonRateThrottle as DRFAnonRateThrottle
from rest_framework.throttling import UserRateThrottle


class AnonRateThrottle(DRFAnonRateThrottle):
    scope = "anon"


class AuthedRateThrottle(UserRateThrottle):
    scope = "authed"


class ChatRateThrottle(UserRateThrottle):
    scope = "chat"


class GuardrailRateThrottle(UserRateThrottle):
    scope = "guardrail"
