from django.utils.timezone import now
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


def delete_expired_tokens():
    OutstandingToken.objects.filter(expires_at__lt=now()).delete()
