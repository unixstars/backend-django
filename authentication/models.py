from django.db import models
from django.conf import settings


class LoginEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self) -> str:
        return f"{self.user}로그인/IP:{self.ip_address}"
