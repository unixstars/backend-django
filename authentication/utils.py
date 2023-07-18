from api.utils import FieldRateThrottle


class SendRateThrottle(FieldRateThrottle):
    rate = "15/hour"


class LoginRateThrottle(FieldRateThrottle):
    rate = "10/hour"
